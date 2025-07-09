<script lang="ts">
	import { filterWords } from '$lib/api';
	import { handleSingleCharInput } from '$lib/utils';
	import type { WordRow } from '$lib/types';
	import { CharacterState } from '$lib/types';
	import { onMount } from 'svelte';
	import { XIcon } from 'svelte-feather-icons';

	// State management
	let wordRows = $state<WordRow[]>([
		Array(5)
			.fill('')
			.map((v) => ({ value: v, state: CharacterState.INCORRECT }))
	]);
	let result = $state<string[]>([]);
	let error = $state('');
	let loading = $state(false);

	// Local storage keys
	const WORD_ROWS_KEY = 'wordle-helper-wordRows';
	const RESULT_KEY = 'wordle-helper-result';

	onMount(() => {
		const savedRows = localStorage.getItem(WORD_ROWS_KEY);
		if (savedRows) {
			try {
				wordRows = JSON.parse(savedRows);
			} catch {}
		}
		const savedResult = localStorage.getItem(RESULT_KEY);
		if (savedResult) {
			try {
				result = JSON.parse(savedResult);
			} catch {}
		}
	});

	$effect(() => {
		localStorage.setItem(WORD_ROWS_KEY, JSON.stringify(wordRows));
	});
	$effect(() => {
		localStorage.setItem(RESULT_KEY, JSON.stringify(result));
	});

	function handleCharInput(rowIdx: number, charIdx: number, event: Event) {
		const input = event.target as HTMLInputElement;
		const value = handleSingleCharInput(input.value);
		wordRows[rowIdx][charIdx].value = value;
		input.value = value;
		console.log(`Row ${rowIdx}, Char ${charIdx} updated to: ${value}`);
		// Move focus to next input if value was entered
		if (value) {
			console.log(`Moving focus to next character in row ${rowIdx}`);
			const nextCharIdx = charIdx + 1;
			console.log(`Next character index: ${nextCharIdx}`);
			if (nextCharIdx < 5) {
				const nextInput = document.querySelector(
					`input[data-row="${rowIdx}"][data-char="${nextCharIdx}"]`
				) as HTMLInputElement;
				if (nextInput) nextInput.focus();
			}
		}
	}

	function handleCharKeydown(rowIdx: number, charIdx: number, event: KeyboardEvent) {
		if (event.key === 'Backspace') {
			const current = wordRows[rowIdx][charIdx];
			if (!current.value && charIdx > 0) {
				const prevCharIdx = charIdx - 1;
				wordRows[rowIdx][prevCharIdx].value = '';
				const prevInput = document.querySelector(
					`input[data-row="${rowIdx}"][data-char="${prevCharIdx}"]`
				) as HTMLInputElement;
				if (prevInput) prevInput.focus();
				// Prevent default so browser doesn't go back
				event.preventDefault();
			}
		}
	}
	function toggleCharState(rowIdx: number, charIdx: number) {
		if (!wordRows[rowIdx][charIdx].value) return; // Don't toggle empty cells
		const states = Object.values(CharacterState);
		const currentState = wordRows[rowIdx][charIdx].state;
		const currentIdx = states.indexOf(currentState);
		const nextIdx = (currentIdx + 1) % states.length;
		wordRows[rowIdx][charIdx].state = states[nextIdx];
	}

	function addNewRow() {
		wordRows = [
			...wordRows,
			Array(5)
				.fill('')
				.map((v) => ({ value: v, state: CharacterState.INCORRECT }))
		];
	}

	function removeRow(rowIdx: number) {
		if (wordRows.length > 1) {
			wordRows = wordRows.filter((_, idx) => idx !== rowIdx);
		}
	}
	function reset() {
		wordRows = Array(1)
			.fill('')
			.map(() => Array(5).fill({ value: '', state: 'incorrect' }));
		result = [];
		error = '';
	}
	async function handleSearch() {
		try {
			loading = true;
			error = '';
			result = await filterWords(wordRows);
		} catch (e) {
			error = 'Request failed';
			console.error('Filter error:', e);
		} finally {
			loading = false;
		}
	}
</script>

<div class="container">
	<h1>Welcome</h1>
	<p class="instructions">
		Enter words and click on the letters to toggle their state
		<span class="example incorrect">Gray for incorrect letters</span>
		<span class="example wrong-position">Yellow for letters in wrong position</span>
		<span class="example correct-position">Green for letters in correct position</span>
	</p>
	<main class="main-content">
		<div class="word-grid">
			{#each wordRows as row, rowIdx}
				<div class="word-row">
					<button
						class="remove-row"
						onclick={() => removeRow(rowIdx)}
						title="Remove row"
						aria-label="Remove row"
					>
						<XIcon />
					</button>
					<div class="word-row-content">
						{#each row as char, charIdx}
							<input
								type="text"
								maxlength="1"
								data-row={rowIdx}
								data-char={charIdx}
								value={char.value}
								class={char.state}
								onfocus={(e) => (e.target as HTMLInputElement).select()}
								oninput={(e) => handleCharInput(rowIdx, charIdx, e)}
								onkeydown={(e) => handleCharKeydown(rowIdx, charIdx, e)}
								onclick={() => toggleCharState(rowIdx, charIdx)}
							/>
						{/each}
					</div>
					<div class="empty-space"></div>
				</div>
			{/each}
		</div>

		<div class="controls">
			<button onclick={addNewRow} disabled={wordRows.length >= 6} class="add-row">Add Row</button>
			<button onclick={handleSearch} class="search">Filter</button>
			<button onclick={reset} class="reset">Reset</button>
		</div>

		{#if error}
			<div class="error">{error}</div>
		{/if}

		{#if loading}
			<div class="loading">Loading...</div>
		{:else if result.length}
			<div class="results">
				<h2>Found {result.length} words:</h2>
				<div class="word-list">
					{#each result as word}
						<span class="word">{word}</span>
					{/each}
				</div>
			</div>
		{/if}
	</main>
	<footer class="footer">
		<p>
			This website is an independent tool designed to assist users in solving word puzzles and is
			not affiliated with, endorsed by, or sponsored by The New York Times Company or the official
			Wordle game. "Wordle" is a trademark of The New York Times Company. All references to Wordle
			are made for descriptive and informational purposes only. This site does not host or reproduce
			the original Wordle game and is intended solely as a resource for players. All content and
			tools provided here are independently created.
		</p>
	</footer>
</div>

<style>
	:root {
		--white: white;

		--gray-dark: #1a1a1a;
		--gray-medium: #4a4a4a;
		--gray-light: #787c7e;
		--gray-border: #d3d6da;
		--gray-border-focus: #878a8c;

		--yellow: #c9b458;
		--green: #6aaa64;
		--red: #dc2626;

		--shadow-hover: rgba(0, 0, 0, 0.1);

		--color-primary: var(--gray-dark);
		--color-secondary: var(--gray-medium);
		--color-tertiary: var(--white);
		--color-background: var(--gray-medium);

		--color-incorrect-position: var(--gray-light);
		--color-correct-position: var(--green);
		--color-wrong-position: var(--yellow);

		--color-error-background: var(--white);
		--color-error: var(--red);
	}

	.main-content {
		flex: 1;
	}

	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		font-family:
			system-ui,
			-apple-system,
			sans-serif;
	}

	h1 {
		text-align: center;
		color: var(--color-primary);
		margin-bottom: 1rem;
		font-size: 2.7rem;
		font-weight: 700;
	}

	.instructions {
		text-align: center;
		margin-bottom: 2rem;
		color: var(--color-secondary);
		line-height: 1.5;
	}

	.example {
		padding: 2px 8px;
		border-radius: 4px;
		margin: 0 4px;
		display: block;
	}

	.word-grid {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin: 20px auto;
		width: 100%;
		align-items: center;
	}

	.word-row {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 12px;
		width: 100%;
	}

	.word-row-content {
		display: flex;
		gap: 8px;
		justify-content: center;
	}

	.empty-space {
		width: 54px;
		height: 54px;
	}

	.remove-row {
		width: 54px;
		height: 54px;
		background: none;
		border: none;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		color: var(--red);
	}

	input {
		width: 54px;
		height: 54px;
		padding: 2px;
		text-align: center;
		justify-content: center;
		font-size: 2em;
		font-weight: bold;
		text-transform: uppercase;
		border: 2px solid var(--gray-border);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s ease;
	}
	input::selection {
		background: transparent;
		color: inherit;
	}

	input:hover {
		transform: scale(1.05);
	}

	input:focus {
		border-color: var(--gray-border-focus);
	}

	input.correct-position {
		background-color: var(--color-correct-position);
		border-color: var(--color-correct-position);
		color: var(--color-tertiary);
	}

	input.wrong-position {
		background-color: var(--color-wrong-position);
		border-color: var(--color-wrong-position);
		color: var(--color-tertiary);
	}

	input.incorrect {
		background-color: var(--color-incorrect-position);
		border-color: var(--color-incorrect-position);
		color: var(--color-tertiary);
	}

	.controls {
		display: flex;
		gap: 16px;
		justify-content: center;
		margin: 24px auto;
		width: fit-content;
	}

	@media (max-width: 400px) {
		.controls {
			flex-direction: column;
			gap: 10px;
		}
	}

	button {
		padding: 12px 12px;
		font-size: 1em;
		cursor: pointer;
		border: none;
		border-radius: 4px;
		font-weight: 600;
		transition: all 0.2s ease;
	}

	button.add-row {
		width: 100px;
		background-color: var(--color-secondary);
		color: var(--color-tertiary);
	}

	button.search {
		width: 100px;
		background-color: var(--color-correct-position);
		color: var(--color-tertiary);
	}

	button.reset {
		width: 100px;
		background-color: var(--red);
		color: var(--color-tertiary);
	}

	button.reset:hover:not(:disabled),
	button:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 2px 8px var(--shadow-hover);
	}

	button:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.error {
		color: var(--color-error);
		text-align: center;
		margin: 16px 0;
		padding: 12px;
		background-color: var(--color-error-background);
		border-radius: 4px;
	}

	.loading {
		text-align: center;
		margin: 16px 0;
		color: var(--color-secondary);
	}

	.results {
		margin: 24px 0;
	}

	.results h2 {
		text-align: center;
		color: var(--color-secondary);
		margin-bottom: 16px;
	}

	.word-list {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		justify-content: center;
	}

	.word {
		padding: 8px 16px;
		background-color: var(--color-background);
		border-radius: 4px;
		text-transform: uppercase;
		font-weight: 600;
		color: var(--color-tertiary);
		transition: all 0.2s ease;
	}

	.word:hover {
		transform: translateY(-2px);
		box-shadow: 0 2px 8px var(--shadow-hover);
	}

	.footer {
		padding: 1rem;
		text-align: center;
		color: var(--color-secondary);
		font-size: 0.9em;
	}
</style>
