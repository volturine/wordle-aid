<script lang="ts">
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { prefersReducedMotion } from 'svelte/motion';
	import { FilePenLine, Grid2x2Check, X } from 'lucide-svelte';
	import ThemeSwitch from '$lib/components/ThemeSwitch.svelte';
	import WordDefinitionOverlay from '$lib/components/WordDefinitionOverlay.svelte';
	import { CharacterState } from '$lib/interfaces';
	import { filterWords } from '$lib/api';
	import type { WordRow } from '$lib/types';

	const initialRow = (): WordRow =>
		Array.from({ length: 5 }, () => ({ value: '', state: CharacterState.INCORRECT }));
	const stateLabels: Record<CharacterState, string> = {
		[CharacterState.WRITING]: 'unmarked',
		[CharacterState.INCORRECT]: 'gray, not in the answer',
		[CharacterState.WRONG_POSITION]: 'yellow, in the wrong position',
		[CharacterState.CORRECT_POSITION]: 'green, in the correct position'
	};
	const feedbackStates = [
		CharacterState.INCORRECT,
		CharacterState.WRONG_POSITION,
		CharacterState.CORRECT_POSITION
	];
	const WORD_ROWS_KEY = 'wordle-helper-wordRows';
	const RESULT_KEY = 'wordle-helper-result';

	let wordRows = $state<WordRow[]>([initialRow()]);
	let result = $state<string[]>([]);
	let error = $state('');
	let validationError = $state('');
	let feedbackStatus = $state('');
	let invalidCell = $state<{ row: number; column: number } | null>(null);
	let loading = $state(false);
	let searchCompleted = $state(false);
	let inputMode = $state<'writing' | 'feedback'>('writing');
	let selectedWord = $state('');
	let bubblePos = $state({ top: 0, bottom: 0, left: 0, maxHeight: 320 });
	let overlayPosition = $state<'top' | 'bottom'>('bottom');
	let wordTrigger: HTMLButtonElement | null = null;
	let activeSearch: AbortController | null = null;

	onMount(() => {
		try {
			const savedRows = localStorage.getItem(WORD_ROWS_KEY);
			const parsedRows: unknown = savedRows ? JSON.parse(savedRows) : null;
			if (
				Array.isArray(parsedRows) &&
				parsedRows.length > 0 &&
				parsedRows.every(
					(row) =>
						Array.isArray(row) &&
						row.length === 5 &&
						row.every(
							(cell) =>
								typeof cell.value === 'string' && Object.values(CharacterState).includes(cell.state)
						)
				)
			) {
				wordRows = parsedRows as WordRow[];
			}

			const savedResult = localStorage.getItem(RESULT_KEY);
			const parsedResult: unknown = savedResult ? JSON.parse(savedResult) : null;
			if (Array.isArray(parsedResult) && parsedResult.every((word) => typeof word === 'string')) {
				result = parsedResult;
				searchCompleted = result.length > 0;
			}
		} catch {
			localStorage.removeItem(WORD_ROWS_KEY);
			localStorage.removeItem(RESULT_KEY);
		}
	});

	$effect(() => {
		localStorage.setItem(WORD_ROWS_KEY, JSON.stringify(wordRows));
	});

	$effect(() => {
		localStorage.setItem(RESULT_KEY, JSON.stringify(result));
	});

	function invalidateSearch(clearResults = true) {
		activeSearch?.abort();
		activeSearch = null;
		loading = false;
		if (clearResults) {
			result = [];
			searchCompleted = false;
		}
	}

	function closeOverlay(restoreFocus = true) {
		selectedWord = '';
		if (restoreFocus) requestAnimationFrame(() => wordTrigger?.focus());
	}

	function handleUseWord(word: string) {
		inputMode = 'writing';
		const newRow = word
			.toLowerCase()
			.split('')
			.map((value) => ({
				value,
				state: CharacterState.INCORRECT
			}));
		for (const row of wordRows) {
			row.forEach((cell, index) => {
				if (cell.value === newRow[index].value && cell.state === CharacterState.CORRECT_POSITION) {
					newRow[index].state = CharacterState.CORRECT_POSITION;
				}
			});
		}

		let targetRowIndex = wordRows.findIndex((row) => row.every((cell) => !cell.value));
		if (targetRowIndex >= 0) {
			wordRows[targetRowIndex] = newRow;
		} else if (wordRows.length < 6) {
			targetRowIndex = wordRows.length;
			wordRows = [...wordRows, newRow];
		} else {
			targetRowIndex = 0;
		}
		invalidateSearch();
		requestAnimationFrame(() =>
			document
				.querySelector<HTMLInputElement>(`input[data-row="${targetRowIndex}"][data-char="0"]`)
				?.focus()
		);
	}

	function handleCharInput(rowIndex: number, columnIndex: number, event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const rawValue = input.value;
		const value = rawValue.match(/[a-z]/i)?.[0]?.toLowerCase() ?? '';
		input.value = value;
		wordRows[rowIndex][columnIndex].value = value;
		invalidateSearch();
		error = '';

		if (rawValue && !/^[a-z]$/i.test(rawValue)) {
			invalidCell = { row: rowIndex, column: columnIndex };
			validationError = 'Use one letter from A to Z in each square.';
		} else if (invalidCell?.row === rowIndex && invalidCell.column === columnIndex) {
			invalidCell = null;
			validationError = '';
		}

		if (value && columnIndex < 4) {
			document
				.querySelector<HTMLInputElement>(
					`input[data-row="${rowIndex}"][data-char="${columnIndex + 1}"]`
				)
				?.focus();
		}
	}

	function cycleFeedback(rowIndex: number, columnIndex: number) {
		const cell = wordRows[rowIndex][columnIndex];
		if (!cell.value) return;
		const currentIndex = feedbackStates.indexOf(cell.state);
		cell.state = feedbackStates[(currentIndex + 1) % feedbackStates.length];
		feedbackStatus = `Guess ${rowIndex + 1}, letter ${columnIndex + 1}: ${stateLabels[cell.state]}.`;
		invalidateSearch();
	}

	function handleCharKeydown(rowIndex: number, columnIndex: number, event: KeyboardEvent) {
		if (inputMode === 'feedback' && (event.key === 'Enter' || event.key === ' ')) {
			event.preventDefault();
			cycleFeedback(rowIndex, columnIndex);
			return;
		}
		if (event.key === 'Enter') event.preventDefault();
		if (event.key === 'Backspace') {
			const cell = wordRows[rowIndex][columnIndex];
			if (!cell.value && columnIndex > 0) {
				wordRows[rowIndex][columnIndex - 1].value = '';
				document
					.querySelector<HTMLInputElement>(
						`input[data-row="${rowIndex}"][data-char="${columnIndex - 1}"]`
					)
					?.focus();
				event.preventDefault();
			}
		}
	}

	function addRow() {
		if (wordRows.length >= 6) return;
		inputMode = 'writing';
		wordRows = [...wordRows, initialRow()];
		invalidateSearch();
		requestAnimationFrame(() => {
			const index = wordRows.length - 1;
			document
				.querySelector<HTMLInputElement>(`input[data-row="${index}"][data-char="0"]`)
				?.focus();
		});
	}

	function removeRow(rowIndex: number) {
		if (wordRows.length <= 1) return;
		wordRows = wordRows.filter((_, index) => index !== rowIndex);
		invalidCell = null;
		validationError = '';
		invalidateSearch();
		requestAnimationFrame(() => {
			const nextRowIndex = Math.min(rowIndex, wordRows.length - 1);
			document
				.querySelector<HTMLInputElement>(`input[data-row="${nextRowIndex}"][data-char="0"]`)
				?.focus();
		});
	}

	function reset() {
		invalidateSearch();
		inputMode = 'writing';
		wordRows = [initialRow()];
		result = [];
		searchCompleted = false;
		error = '';
		validationError = '';
		invalidCell = null;
		selectedWord = '';
	}

	function showOverlay(word: string, event: MouseEvent) {
		wordTrigger = event.currentTarget as HTMLButtonElement;
		const rect = wordTrigger.getBoundingClientRect();
		const belowSpace = window.innerHeight - rect.bottom - 24;
		const aboveSpace = rect.top - 24;
		overlayPosition = belowSpace >= aboveSpace ? 'bottom' : 'top';
		bubblePos = {
			top: rect.top,
			bottom: rect.bottom,
			left: Math.max(
				Math.min(192, (window.innerWidth - 32) / 2) + 16,
				Math.min(
					window.innerWidth - Math.min(192, (window.innerWidth - 32) / 2) - 16,
					rect.left + rect.width / 2
				)
			),
			maxHeight: Math.max(0, Math.min(360, overlayPosition === 'bottom' ? belowSpace : aboveSpace))
		};
		selectedWord = word;
	}

	async function handleSearch(event: SubmitEvent) {
		event.preventDefault();
		const invalidRow = wordRows.findIndex((row) =>
			row.some((cell) => cell.value && !/^[a-z]$/i.test(cell.value))
		);
		if (invalidRow >= 0) {
			const invalidColumn = wordRows[invalidRow].findIndex(
				(cell) => cell.value && !/^[a-z]$/i.test(cell.value)
			);
			invalidCell = { row: invalidRow, column: invalidColumn };
			validationError = 'Use one letter from A to Z in each square.';
			document
				.querySelector<HTMLInputElement>(
					`input[data-row="${invalidRow}"][data-char="${invalidColumn}"]`
				)
				?.focus();
			return;
		}

		activeSearch?.abort();
		const controller = new AbortController();
		activeSearch = controller;
		loading = true;
		searchCompleted = false;
		error = '';
		validationError = '';
		invalidCell = null;
		result = [];

		try {
			const words = await filterWords(wordRows, controller.signal);
			if (activeSearch !== controller) return;
			result = words;
			searchCompleted = true;
		} catch (cause) {
			if (controller.signal.aborted) return;
			console.error('Filter error:', cause);
			error = 'We couldn’t reach the word list. Check your connection and try again.';
		} finally {
			if (activeSearch === controller) {
				activeSearch = null;
				loading = false;
			}
		}
	}
</script>

<svelte:head>
	<title>Wordle Aid — Find possible answers</title>
	<meta
		name="description"
		content="Enter your Wordle guesses, mark each letter’s color, and find possible answers with clear definitions."
	/>
	<meta property="og:title" content="Wordle Aid — Find possible answers" />
	<meta
		property="og:description"
		content="Enter your Wordle guesses, mark each letter’s color, and find possible answers with clear definitions."
	/>
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://wordle-aid.com/" />
	<meta property="og:image" content="https://wordle-aid.com/og-image.png" />
	<meta property="og:site_name" content="Wordle Aid" />
</svelte:head>

<div class="page-shell">
	<main class="app-card">
		<header class="page-header">
			<div class="top-bar">
				<p class="eyebrow">Wordle Aid</p>
				<ThemeSwitch />
			</div>
			<h1>Find possible answers.</h1>
			<p class="intro">Enter each guess, mark the letter colors, and narrow down your next move.</p>
		</header>

		<section class="legend" aria-label="Letter color guide">
			<p>
				<span class="legend-swatch gray"></span><strong>Gray</strong><span>Not in the word</span>
			</p>
			<p>
				<span class="legend-swatch yellow"></span><strong>Yellow</strong><span>Wrong spot</span>
			</p>
			<p>
				<span class="legend-swatch green"></span><strong>Green</strong><span>Right spot</span>
			</p>
		</section>

		<form class="guess-form" onsubmit={handleSearch} aria-busy={loading}>
			<div class="mode-switch" role="group" aria-label="Guess entry mode">
				<button
					type="button"
					class:active={inputMode === 'writing'}
					aria-pressed={inputMode === 'writing'}
					onclick={() => (inputMode = 'writing')}
				>
					<FilePenLine size={18} aria-hidden="true" />
					<span>Type letters</span>
				</button>
				<button
					type="button"
					class:active={inputMode === 'feedback'}
					aria-pressed={inputMode === 'feedback'}
					onclick={() => (inputMode = 'feedback')}
				>
					<Grid2x2Check size={18} aria-hidden="true" />
					<span>Mark colors</span>
				</button>
			</div>
			<p class="mode-help" id="mode-help">
				{inputMode === 'writing'
					? 'Type one letter in each square. Your guesses are saved on this device.'
					: 'Click a letter, or focus it and press Enter or Space, to cycle gray, yellow, and green.'}
			</p>

			<div class="word-grid" role="group" aria-label="Your guesses">
				{#each wordRows as row, rowIndex (row)}
					<div class="word-row" role="group" aria-label={`Guess ${rowIndex + 1}`}>
						<div class="word-row-content">
							{#each row as cell, columnIndex (columnIndex)}
								<input
									type="text"
									maxlength="1"
									inputmode="text"
									spellcheck="false"
									autocomplete="off"
									data-row={rowIndex}
									data-char={columnIndex}
									aria-label={`Guess ${rowIndex + 1}, letter ${columnIndex + 1}, ${stateLabels[cell.state]}`}
									aria-describedby={invalidCell?.row === rowIndex &&
									invalidCell.column === columnIndex
										? `mode-help guess-error-${rowIndex}`
										: 'mode-help'}
									aria-invalid={invalidCell?.row === rowIndex && invalidCell.column === columnIndex}
									value={cell.value}
									class={cell.value ? cell.state : 'empty'}
									onfocus={(event) => (event.currentTarget as HTMLInputElement).select()}
									oninput={(event) => handleCharInput(rowIndex, columnIndex, event)}
									onkeydown={(event) => handleCharKeydown(rowIndex, columnIndex, event)}
									onclick={() => inputMode === 'feedback' && cycleFeedback(rowIndex, columnIndex)}
								/>
							{/each}
						</div>
						{#if wordRows.length > 1}
							<button
								type="button"
								class="remove-row"
								aria-label={`Remove guess ${rowIndex + 1}`}
								title={`Remove guess ${rowIndex + 1}`}
								onclick={() => removeRow(rowIndex)}
							>
								<X size={18} aria-hidden="true" />
							</button>
						{:else}
							<span aria-hidden="true"></span>
						{/if}
					</div>
					{#if invalidCell?.row === rowIndex}
						<p class="field-error" role="alert" id={`guess-error-${rowIndex}`}>
							{validationError}
						</p>
					{/if}
				{/each}
			</div>
			<p class="visually-hidden" role="status" aria-live="polite">{feedbackStatus}</p>

			<div class="form-actions">
				<button type="submit" class="primary-action" disabled={loading}>
					{loading ? 'Finding answers…' : 'Filter candidates'}
				</button>
				<div class="secondary-actions">
					<button
						type="button"
						class="secondary-action"
						onclick={addRow}
						disabled={wordRows.length >= 6}
					>
						Add guess <span class="visually-hidden">({wordRows.length} of 6)</span>
					</button>
					<button type="button" class="reset-action" onclick={reset}>Reset</button>
				</div>
			</div>
		</form>

		{#if loading}
			<p class="status-message" role="status" aria-live="polite">Finding possible answers…</p>
		{:else if error}
			<p class="error-message" role="alert">{error}</p>
		{:else if searchCompleted && result.length === 0}
			<section
				class="empty-state"
				aria-live="polite"
				in:fade={{ duration: prefersReducedMotion.current ? 0 : 160 }}
			>
				<h2>No matching words</h2>
				<p>Check the colors on your guesses, then filter again.</p>
			</section>
		{:else if searchCompleted}
			<section
				class="results"
				aria-busy="false"
				in:fade={{ duration: prefersReducedMotion.current ? 0 : 160 }}
			>
				<p class="results-count" role="status" aria-live="polite">
					Found {result.length}
					{result.length === 1 ? 'possible answer' : 'possible answers'}.
				</p>
				<ul class="word-list" aria-label="Possible answers">
					{#each result as word (word)}
						<li>
							<button
								type="button"
								class="word-result"
								aria-haspopup="dialog"
								aria-expanded={selectedWord === word}
								onclick={(event) => showOverlay(word, event)}
							>
								{word}
							</button>
						</li>
					{/each}
				</ul>
			</section>
		{/if}

		<WordDefinitionOverlay
			{selectedWord}
			{bubblePos}
			position={overlayPosition}
			onClose={closeOverlay}
			onUseWord={handleUseWord}
		/>

		<footer class="footer">
			<p>
				Wordle is a trademark of The New York Times Company. Wordle Aid is an independent puzzle
				helper and is not affiliated with or endorsed by The New York Times.
			</p>
		</footer>
	</main>
</div>

<style>
	.page-shell {
		min-height: 100vh;
		padding: var(--space-8) var(--space-4);
		background: var(--page);
	}

	.app-card {
		width: min(100%, 48rem);
		margin: 0 auto;
		padding: var(--space-8);
		border: 1px solid var(--line);
		border-radius: var(--radius-card);
		background: var(--surface);
		box-shadow: var(--shadow);
	}

	.top-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-4);
		margin-bottom: var(--space-4);
	}

	.eyebrow {
		margin: 0;
		color: var(--muted);
		font-size: 0.875rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	h1 {
		margin: 0;
		font-size: 2rem;
		line-height: 1.15;
		letter-spacing: -0.02em;
		text-wrap: balance;
	}

	.intro {
		max-width: 38rem;
		margin: var(--space-2) 0 0;
		color: var(--muted);
		line-height: 1.5;
		text-wrap: pretty;
	}

	.legend {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: var(--space-3);
		margin: var(--space-6) 0;
		padding: var(--space-3) var(--space-4);
		border: 1px solid var(--line);
		border-radius: var(--radius-control);
		background: var(--page);
	}

	.legend p {
		display: grid;
		grid-template-columns: 12px minmax(0, 1fr);
		align-content: start;
		align-items: center;
		gap: 0 var(--space-2);
		margin: 0;
		font-size: 0.875rem;
		line-height: 1.45;
	}

	.legend p > span:last-child {
		grid-column: 2;
		color: var(--muted);
	}

	.legend-swatch {
		width: 12px;
		height: 12px;
		border-radius: var(--space-1);
	}

	.legend-swatch.gray {
		background: var(--gray);
	}
	.legend-swatch.yellow {
		background: var(--yellow);
	}
	.legend-swatch.green {
		background: var(--tile-green);
	}

	.guess-form {
		margin: 0;
	}

	.mode-switch {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: var(--space-1);
		max-width: 24rem;
		padding: var(--space-1);
		border: 1px solid var(--line);
		border-radius: var(--radius-control);
		background: var(--page);
	}

	.mode-switch button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-2);
		min-width: 0;
		padding: 0 var(--space-2);
		border-color: transparent;
		background: transparent;
		color: var(--muted);
		font-weight: 600;
		white-space: nowrap;
	}

	.mode-switch button:hover:not(:disabled) {
		border-color: transparent;
		color: var(--ink);
	}

	.mode-switch button.active {
		border-color: var(--line);
		background: var(--surface-raised);
		color: var(--ink);
		box-shadow: 0 1px 2px rgb(0 0 0 / 8%);
	}

	.mode-help {
		min-height: 2.9em;
		margin: var(--space-2) 0 var(--space-4);
		color: var(--muted);
		font-size: 0.875rem;
		line-height: 1.45;
	}

	.word-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.word-row {
		display: grid;
		grid-template-columns: 44px minmax(0, 20rem) 44px;
		justify-content: center;
		align-items: center;
		gap: var(--space-2);
	}

	.word-row-content {
		display: grid;
		grid-column: 2;
		grid-template-columns: repeat(5, minmax(0, 1fr));
		gap: var(--space-2);
		min-width: 0;
	}

	.word-row input {
		width: 100%;
		min-width: 0;
		min-height: 44px;
		aspect-ratio: 1;
		padding: 0;
		border: 2px solid var(--line);
		border-radius: var(--radius-control);
		background: var(--surface-raised);
		color: var(--ink);
		font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
		font-size: 1.5rem;
		font-weight: 700;
		text-align: center;
		text-transform: uppercase;
		caret-color: transparent;
		transition:
			background-color 160ms ease,
			border-color 160ms ease;
	}

	.word-row input.empty:focus {
		border-color: var(--line-strong);
	}

	.word-row input.incorrect,
	.word-row input.wrong-position,
	.word-row input.correct-position {
		border-color: transparent;
		color: var(--tile-ink);
	}

	.word-row input.incorrect {
		background: var(--gray);
	}
	.word-row input.wrong-position {
		background: var(--yellow);
	}
	.word-row input.correct-position {
		background: var(--tile-green);
	}

	.remove-row {
		width: 100%;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		border-color: transparent;
		background: transparent;
		color: var(--muted);
	}

	.remove-row:hover:not(:disabled) {
		border-color: var(--danger);
		background: var(--danger-surface);
		color: var(--danger);
	}

	.field-error {
		margin: 0;
		color: var(--danger);
		font-size: 0.875rem;
		text-align: center;
	}

	.form-actions {
		display: grid;
		gap: var(--space-2);
		margin-top: var(--space-6);
	}

	.primary-action {
		min-height: 48px;
		border-color: var(--green);
		background: var(--green);
		color: var(--action-ink);
		font-weight: 700;
	}

	.primary-action:hover:not(:disabled) {
		border-color: var(--green-hover);
		background: var(--green-hover);
	}

	.secondary-actions {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: var(--space-2);
	}

	.secondary-action,
	.reset-action {
		padding: 0 var(--space-4);
		font-weight: 600;
	}

	.reset-action {
		color: var(--danger);
	}

	.reset-action:hover:not(:disabled) {
		border-color: var(--danger);
		background: var(--danger-surface);
	}

	.status-message,
	.error-message {
		margin: var(--space-6) 0 0;
		padding: var(--space-3) var(--space-4);
		border-radius: var(--radius-control);
		line-height: 1.5;
	}

	.status-message {
		background: var(--page);
		color: var(--muted);
	}

	.error-message {
		border: 1px solid var(--danger);
		background: var(--danger-surface);
		color: var(--danger);
	}

	.empty-state,
	.results {
		margin-top: var(--space-6);
		padding-top: var(--space-6);
		border-top: 1px solid var(--line);
	}

	.empty-state h2 {
		margin: 0 0 var(--space-2);
		font-size: 1.25rem;
	}

	.empty-state p,
	.results-count {
		margin: 0;
		color: var(--muted);
		line-height: 1.5;
	}

	.word-list {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(5.5rem, 1fr));
		gap: var(--space-2);
		margin: var(--space-4) 0 0;
		padding: 0;
		list-style: none;
	}

	.word-list li {
		margin: 0;
	}

	.word-result {
		width: 100%;
		padding: 0 var(--space-2);
		font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.word-result:hover:not(:disabled) {
		border-color: var(--green);
		background: var(--page);
	}

	.footer {
		margin-top: var(--space-8);
		padding-top: var(--space-4);
		border-top: 1px solid var(--line);
		color: var(--muted);
		font-size: 0.875rem;
		line-height: 1.5;
	}

	.footer p {
		margin: 0;
	}

	@media (max-width: 520px) {
		.page-shell {
			padding: 0;
			background: var(--surface);
		}
		.app-card {
			min-height: 100vh;
			padding: var(--space-3) var(--space-4) var(--space-6);
			border: 0;
			border-radius: 0;
			box-shadow: none;
		}
		.top-bar {
			margin-bottom: var(--space-3);
		}
		h1 {
			font-size: 1.75rem;
		}
		.legend {
			grid-template-columns: 1fr;
			gap: var(--space-1);
			margin: var(--space-4) 0 var(--space-6);
			padding: var(--space-3) var(--space-4);
		}
		.legend p {
			grid-template-columns: 12px 4rem minmax(0, 1fr);
		}
		.legend p > span:last-child {
			grid-column: 3;
		}
		.mode-switch {
			max-width: none;
		}
		.word-row {
			grid-template-columns: 36px minmax(0, 1fr) 36px;
		}
		.word-row,
		.word-row-content {
			gap: var(--space-1);
		}
		.word-row input {
			font-size: 1.25rem;
		}
	}

	@media (max-width: 340px) {
		.app-card {
			padding-inline: var(--space-3);
		}
		.mode-switch button :global(svg) {
			display: none;
		}
		.word-row input {
			min-height: 0;
		}
	}
</style>
