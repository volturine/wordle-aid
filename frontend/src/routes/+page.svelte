<script lang="ts">
	import WordDefinitionOverlay from '$lib/components/WordDefinitionOverlay.svelte';
	import { X, FilePenLine, Grid2x2Check } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import ThemeSwitch from '$lib/components/ThemeSwitch.svelte';

	import type { WordRow } from '$lib/types';
	import { CharacterState } from '$lib/interfaces';
	import { filterWords } from '$lib/api';

	// State management
	let wordRows = $state<WordRow[]>([
		Array(5)
			.fill('')
			.map((v) => ({ value: v, state: CharacterState.INCORRECT }))
	]);
	let result = $state<string[]>([]);
	let error = $state('');
	let loading = $state(false);

	let selectedWord = $state('');
	let bubblePos = $state({ top: 0, bottom: 0, left: 0 });
	let overlayPosition = $state<'top' | 'bottom'>('bottom');

	let input_state = $state(CharacterState.WRITING);

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

	function closeOverlay() {
		selectedWord = '';
	}

	function handleUseWord(word: string) {
		input_state = CharacterState.WRITING;
		const newRow = word.split('').map((char) => ({
			value: char.toLowerCase(),
			state: CharacterState.INCORRECT
		}));

		// if row is empty, replace it
		const emptyRowIdx = wordRows.findIndex((row) => row.every((char) => !char.value));
		if (emptyRowIdx !== -1) {
			wordRows[emptyRowIdx] = newRow;
		} else {
			wordRows = [...wordRows, newRow];
		}

		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

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

	function handleMouseDown(rowIdx: number, charIdx: number, event: MouseEvent) {
		if (input_state != CharacterState.WRITING) {
			toggleCharState(rowIdx, charIdx);
			event.preventDefault();
		}
	}

	function toggleCharState(rowIdx: number, charIdx: number) {
		// based on input_state, toggle the character state
		const currentChar = wordRows[rowIdx][charIdx];
		switch (input_state) {
			case CharacterState.WRITING:
				currentChar.state = currentChar.state;
				break;
			default:
				if (!wordRows[rowIdx][charIdx].value) return; // Don't toggle empty cells
				const states = Object.values(CharacterState);
				const currentState = wordRows[rowIdx][charIdx].state;
				const currentIdx = states.indexOf(currentState);
				const nextIdx = (currentIdx + 1) % states.length;
				wordRows[rowIdx][charIdx].state = states[nextIdx];
				// ignore the writing state
				if (states[nextIdx] === CharacterState.WRITING) {
					wordRows[rowIdx][charIdx].state = CharacterState.INCORRECT;
				}
		}
	}

	function addNewRow() {
		input_state = CharacterState.WRITING;
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
		input_state = CharacterState.WRITING;
		wordRows = Array(1)
			.fill('')
			.map(() => Array(5).fill({ value: '', state: 'incorrect' }));
		result = [];
		error = '';
	}

	function handleSingleCharInput(value: string): string {
		return value.slice(0, 1);
	}

	function showOverlay(word: string, event: MouseEvent) {
		selectedWord = word;
		const target = event.target as HTMLElement;
		const rect = target.getBoundingClientRect();
		bubblePos = {
			top: rect.top,
			bottom: rect.bottom,
			left: window.innerWidth < 1200 ? window.innerWidth / 2 : rect.left - window.scrollX
		};
		overlayPosition = rect.top < window.innerHeight / 2 ? 'bottom' : 'top';
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

<div class="page-background">
	<div class="container">
		<header class="header">
			<h1 class="welcome">Welcome</h1>
			<div><ThemeSwitch /></div>
		</header>
		<p class="instructions">
			<span class="example">Gray for incorrect letters</span>
			<span class="example">Yellow for letters in wrong position</span>
			<span class="example">Green for letters in correct position</span>
		</p>
		<main class="main-content">
			<div class="action-buttons">
				<button
					class="action-button write"
					class:active={input_state === CharacterState.WRITING}
					title="Write Mode"
					onclick={() => (input_state = CharacterState.WRITING)}
				>
					<FilePenLine />
				</button>
				<button
					class="action-button select"
					class:active={input_state !== CharacterState.WRITING}
					title="Select State Mode"
					onclick={() => (input_state = CharacterState.INCORRECT)}
				>
					<Grid2x2Check />
				</button>
			</div>
			<div class="word-grid">
				{#each wordRows as row, rowIdx}
					<div class="word-row">
						<button
							class="remove-row"
							onclick={() => removeRow(rowIdx)}
							title="Remove row"
							aria-label="Remove row"
						>
							<X />
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
									onmousedown={(e) => handleMouseDown(rowIdx, charIdx, e)}
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
		</main>
		{#if loading}
			<div class="loading">Loading...</div>
		{:else if result.length}
			<div class="results">
				<h2>Found {result.length} words</h2>
				<div class="word-list">
					{#each result as word}
						<button class="word" onclick={(e) => showOverlay(word, e)}>{word}</button>
					{/each}
				</div>
			</div>
		{/if}
		<WordDefinitionOverlay
			{selectedWord}
			{bubblePos}
			onClose={closeOverlay}
			onUseWord={handleUseWord}
			position={overlayPosition}
		/>

		<footer class="footer">
			<p>
				This website is an independent tool designed to assist users in solving word puzzles and is
				not affiliated with, endorsed by, or sponsored by The New York Times Company or the official
				Wordle game. "Wordle" is a trademark of The New York Times Company. All references to Wordle
				are made for descriptive and informational purposes only. This site does not host or
				reproduce the original Wordle game and is intended solely as a resource for players. All
				content and tools provided here are independently created.
			</p>
		</footer>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: 'Comic Sans MS';
	}

	:global(button) {
		font-family: 'Comic Sans MS';
		font-size: 1em;
	}

	:global(input) {
		font-family: 'Comic Sans MS';
	}

	:global(:root) {
		--white: white;
		--black: #1a1a1a;

		--gray-dark-base: #1a1a1a;
		--gray-medium-base: #4a4a4a;
		--gray-light-base: #787c7e;
		--gray-border-base: #d3d6da;
		--gray-border-focus-base: #878a8c;

		--yellow-base: #c9b458;
		--green-base: #6aaa64;
		--red-base: #dc2626;

		--shadow-hover: rgba(0, 0, 0, 0.1);

		/* Light Theme */
		--color-page-bg: #f4f4f5; /* zinc-100 */
		--color-container-bg: var(--white);
		--color-primary: var(--gray-dark-base);
		--color-secondary: var(--gray-medium-base);
		--color-tertiary: var(--white);
		--gray-border: var(--gray-border-base);
		--gray-border-focus: var(--gray-border-focus-base);
		--color-incorrect: var(--gray-light-base);
		--color-correct-position: var(--green-base);
		--color-wrong-position: var(--yellow-base);
		--color-error-background: var(--white);
		--color-error: var(--red-base);
		--red: var(--red-base);
	}

	:global(body.dark) {
		--gray-dark-base: #e5e5e5;
		--gray-medium-base: #a3a3a3;
		--gray-light-base: #737373;
		--gray-border-base: #525252;
		--gray-border-focus-base: #737373;

		/* Dark Theme */
		--color-page-bg: var(--black);
		--color-container-bg: #27272a; /* zinc-800 */
		--color-primary: var(--gray-dark-base);
		--color-secondary: var(--gray-medium-base);
		--color-tertiary: var(--black);
		--gray-border: var(--gray-border-base);
		--gray-border-focus: var(--gray-border-focus-base);
		--color-incorrect: var(--gray-light-base);
	}

	.page-background {
		background-color: var(--color-page-bg);
		min-height: 100vh;
		padding: 20px 0;
	}

	.header {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: flex-end;
		height: 60px;
	}

	.welcome {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		margin: 0;
	}

	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
		display: flex;
		flex-direction: column;
		min-height: calc(100vh - 80px);
		background-color: var(--color-bg);
		color: var(--color-primary);
	}

	h1 {
		text-align: center;
		color: var(--color-primary);
		margin-bottom: 1rem;
		font-size: 2.7rem;
		font-weight: 700;
	}
	.action-buttons {
		display: flex;
		justify-content: center;
		gap: 14px;
		margin-bottom: 16px;
	}

	.action-button {
		width: 43px;
		height: 43px;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		transition: all 0.2s ease;
		padding: 0;
	}

	.action-button.active {
		border-color: var(--color-primary);
		transform: scale(1.35);
	}

	.write {
		background-color: var(--color-secondary);
		color: var(--color-tertiary);
	}

	.select {
		/* gradient over incorect, wrongposition, correct */
		background: linear-gradient(
			to right,
			var(--color-incorrect),
			var(--color-wrong-position),
			var(--color-correct-position)
		);
		color: var(--color-tertiary);
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
		font-size: 1.7em;
		font-weight: bold;
		text-transform: uppercase;
		border: 2px solid var(--gray-border);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s ease;
		caret-color: transparent;
		-webkit-user-select: none; /* Safari */
		user-select: none; /* Standard syntax */
		background-color: transparent;
		color: var(--color-primary);
	}
	input::selection {
		background: transparent;
		color: inherit;
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
		background-color: var(--color-incorrect);
		border-color: var(--color-incorrect);
		color: var(--color-tertiary);
	}

	.controls {
		display: flex;
		gap: 16px;
		justify-content: center;
		margin: 24px auto;
	}

	@media (max-width: 480px) {
		input {
			width: clamp(35px, 12vw, 54px);
			height: clamp(35px, 12vw, 54px);
		}
	}

	button {
		padding: 12px 12px;
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
		box-shadow: 0 2px 8px var(--shadow-hover);
	}

	button:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.main-content {
		flex-grow: 1;
	}

	.results {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
	}

	.results h2 {
		text-align: center;
		color: var(--color-secondary);
		margin-bottom: 16px;
	}

	.word-list {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		justify-content: center;
		margin-top: 1rem;
		text-transform: uppercase;
		/* Performance optimizations */
		contain: layout style paint;
		will-change: auto;
	}

	.word {
		background-color: var(--color-secondary);
		color: var(--color-tertiary);
		padding: 8px 14px;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1em;
		transition: background-color 0.2s;
		text-transform: uppercase;
		/* Performance optimizations */
		content-visibility: auto;
	}

	/* Disable transitions during theme change */
	:global(body.theme-transitioning) .word {
		transition: none !important;
	}

	.word:hover {
		background-color: var(--color-primary);
	}

	.loading,
	.error {
		text-align: center;
		margin-top: 2rem;
		font-size: 1.2rem;
	}

	.footer {
		margin-top: 2rem;
		padding-top: 1rem;
		border-top: 1px solid var(--gray-border);
		font-size: 0.8rem;
		color: var(--color-secondary);
		text-align: center;
	}
</style>
