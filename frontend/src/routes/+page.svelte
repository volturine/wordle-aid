<script lang="ts">
	import { filterWords } from '$lib/api';
	import { handleSingleCharInput } from '$lib/utils';
	import type { WordRow } from '$lib/types';
	import { CharacterState } from '$lib/types';
	import { onMount } from 'svelte';

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

		// Move focus to next input if value was entered
		if (value) {
			const nextCharIdx = charIdx + 1;
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

	<div class="word-grid">
		{#each wordRows as row, rowIdx}
			<div class="word-row">
				<div class="word-row-content">
					{#each row as char, charIdx}
						<input
							type="text"
							maxlength="1"
							data-row={rowIdx}
							data-char={charIdx}
							value={char.value}
							class={char.state}
							on:input={(e) => handleCharInput(rowIdx, charIdx, e)}
							on:keydown={(e) => handleCharKeydown(rowIdx, charIdx, e)}
							on:click={() => toggleCharState(rowIdx, charIdx)}
						/>
					{/each}
				</div>
			</div>
			<button
				class="remove-row"
				on:click={() => removeRow(rowIdx)}
				title="Remove row"
				aria-label="Remove row"
			>
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M4 4L12 12M12 4L4 12"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
					/>
				</svg>
			</button>
		{/each}
	</div>

	<div class="controls">
		<button on:click={addNewRow} disabled={wordRows.length >= 6} class="add-row">Add Row</button>
		<button on:click={handleSearch} class="search">Filter Words</button>
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
</div>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
		font-family:
			system-ui,
			-apple-system,
			sans-serif;
	}

	h1 {
		text-align: center;
		color: #1a1a1a;
		margin-bottom: 1rem;
	}

	.instructions {
		text-align: center;
		margin-bottom: 2rem;
		color: #4a4a4a;
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
		gap: 12px;
		margin: 20px auto;
		width: 100%;
		max-width: 400px;
	}

	.word-row {
		position: relative;
		display: flex;
		justify-content: center;
		width: 100%;
	}

	.word-row-content {
		display: flex;
		gap: 8px;
		justify-content: center;
		width: fit-content;
		position: relative;
	}
	/* hide cursor in inputs so when i type i dont want to see the I like character */

	input {
		width: 54px;
		height: 54px;
		text-align: center;
		font-size: 2em;
		font-weight: bold;
		text-transform: uppercase;
		border: 2px solid #d3d6da;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s ease;
		caret-color: transparent;
	}

	input:hover {
		transform: scale(1.05);
	}

	input:focus {
		outline: none;
		border-color: #878a8c;
	}

	input.correct-position {
		background-color: #6aaa64;
		border-color: #6aaa64;
		color: white;
	}

	input.wrong-position {
		background-color: #c9b458;
		border-color: #c9b458;
		color: white;
	}

	input.incorrect {
		background-color: #787c7e;
		border-color: #787c7e;
		color: white;
	}

	.controls {
		display: flex;
		gap: 16px;
		justify-content: center;
		margin: 24px auto;
		width: fit-content;
	}

	/* Center the controls absolutely in the container if needed */
	@media (max-width: 600px) {
		.controls {
			flex-direction: column;
			gap: 10px;
		}
	}

	button {
		padding: 12px 24px;
		font-size: 1em;
		cursor: pointer;
		border: none;
		border-radius: 4px;
		font-weight: 600;
		transition: all 0.2s ease;
	}

	button.add-row {
		background-color: #4a4a4a;
		color: white;
	}

	button.search {
		background-color: #6aaa64;
		color: white;
	}

	button:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	button:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.error {
		color: #dc2626;
		text-align: center;
		margin: 16px 0;
		padding: 12px;
		background-color: #fef2f2;
		border-radius: 4px;
	}

	.loading {
		text-align: center;
		margin: 16px 0;
		color: #4a4a4a;
	}

	.results {
		margin: 24px 0;
	}

	.results h2 {
		text-align: center;
		color: #4a4a4a;
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
		background-color: #f4f4f5;
		border-radius: 4px;
		text-transform: uppercase;
		font-weight: 600;
		color: #4a4a4a;
		transition: all 0.2s ease;
	}

	.word:hover {
		transform: translateY(-2px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.remove-row {
		/* position: relative; */
		background: transparent;
		/* border: none; */
		/* cursor: pointer; */
		display: flex;
		align-items: center;
		justify-content: center;
		color: #4b4f58;
	}

	.remove-row svg {
		pointer-events: none;
		display: block;
		width: 18px;
		height: 18px;
	}
</style>
