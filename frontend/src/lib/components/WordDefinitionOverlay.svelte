<script lang="ts">
	import type { DictionaryResponse } from '$lib/types';
	import { getWordDefinition } from '$lib/api';
	import { getCachedDefinition, setCachedDefinition } from '$lib/utils/definitionCache';

	let {
		selectedWord = '',
		bubblePos = { top: 0, bottom: 0, left: 0 },
		onClose,
		onUseWord,
		position = 'bottom'
	}: {
		selectedWord: string;
		bubblePos: { top: number; bottom: number; left: number };
		onClose: () => void;
		onUseWord?: (word: string) => void;
		position: 'top' | 'bottom';
	} = $props();

	let wordDefinition = $state<DictionaryResponse | null>(null);
	let definitionLoading = $state(false);
	let definitionError = $state('');
	let bubbleEl = $state<HTMLDivElement | null>(null);
	let isInitialMount = $state(true);

	// Computed styles for positioning
	const overlayStyle = $derived(
		position === 'top'
			? `top: ${bubblePos.top - 2}px; left: ${bubblePos.left}px;`
			: `top: ${bubblePos.bottom + 2}px; left: ${bubblePos.left}px;`
	);

	// Fetch definition when word changes
	$effect(() => {
		if (selectedWord) {
			definitionError = '';
			definitionLoading = true;
			wordDefinition = null;

			// Check cache first
			const cached = getCachedDefinition(selectedWord);
			if (cached) {
				wordDefinition = cached;
				definitionLoading = false;
				return;
			}

			// Fetch from API if not cached
			getWordDefinition(selectedWord)
				.then((result) => {
					wordDefinition = result;
					setCachedDefinition(selectedWord, result);
				})
				.catch((e) => {
					console.error('Definition error:', e);
					definitionError = 'Definition not found';
				})
				.finally(() => {
					definitionLoading = false;
				});
		}
	});

	// Handle all event listeners in a single effect
	$effect(() => {
		if (!selectedWord) return;

		// Mark that we've mounted (prevents immediate close on click)
		isInitialMount = true;
		const mountTimer = setTimeout(() => {
			isInitialMount = false;
		}, 100);

		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Escape') onClose();
		};

		const handleScroll = () => onClose();

		const handleClickOutside = (event: MouseEvent) => {
			// Don't close if still in initial mount phase or click is inside bubble
			if (isInitialMount) return;
			if (bubbleEl && !bubbleEl.contains(event.target as Node)) {
				onClose();
			}
		};

		document.addEventListener('keydown', handleKeyDown);
		window.addEventListener('scroll', handleScroll, { passive: true });
		document.addEventListener('click', handleClickOutside);

		return () => {
			clearTimeout(mountTimer);
			document.removeEventListener('keydown', handleKeyDown);
			window.removeEventListener('scroll', handleScroll);
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

{#if selectedWord}
	<div
		class="word-bubble"
		class:position-top={position === 'top'}
		style={overlayStyle}
		bind:this={bubbleEl}
	>
		<div class="bubble-content">
			<div class="bubble-header">
				<button
					class="use-word-button"
					onclick={() => {
						if (onUseWord) {
							onUseWord(selectedWord);
						}
						onClose();
					}}
					title="Use this word">USE</button
				>
				<button class="close-button" onclick={onClose} title="Close">?</button>
			</div>

			<h3 class="word-title">{selectedWord}</h3>

			{#if definitionLoading}
				<p class="loading-text">Loading definition...</p>
			{:else if definitionError}
				<p class="error-text">{definitionError}</p>
			{:else if wordDefinition}
				<div class="meanings-container">
					{#each wordDefinition.meanings.slice(0, 4) as meaning}
						<div class="meaning">
							<h4 class="part-of-speech">{meaning.partOfSpeech}</h4>
							<p class="example">"{meaning.definition}"</p>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.word-bubble {
		position: fixed;
		transform: translate(-50%, 0);
		animation: dropDown 200ms ease-out;
		z-index: 1000;
		pointer-events: auto;
	}

	.word-bubble.position-top {
		transform: translate(-50%, -100%);
	}

	@keyframes dropDown {
		from {
			opacity: 0;
			transform: translate(-50%, -10px);
		}
		to {
			opacity: 1;
			transform: translate(-50%, 0);
		}
	}

	.bubble-content {
		background: var(--color-container-bg);
		border: 2px solid var(--gray-border);
		padding: 1rem;
		border-radius: 1rem;
		box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
		position: relative;
		min-width: 200px;
		max-width: 400px;
		max-height: 50vh;
		overflow-y: auto;
	}

	.bubble-header {
		display: flex;
		justify-content: right;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
	}

	.close-button {
		border: none;
		background: transparent;
		font-size: 1.2rem;
		cursor: pointer;
		color: var(--color-secondary);
		padding: 0.25rem;
		line-height: 1;
		transition: color 0.2s ease;
	}

	.close-button:hover {
		color: var(--red);
	}

	.use-word-button {
		border: none;
		background: var(--color-correct-position);
		color: white;
		padding: 0.35rem 0.85rem;
		border-radius: 0.375rem;
		font-size: 0.85rem;
		cursor: pointer;
		font-weight: 600;
		transition: all 0.2s ease;
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}

	.use-word-button:hover {
		background: var(--color-secondary);
		transform: translateY(-1px);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.use-word-button:active {
		transform: translateY(0);
	}

	.word-title {
		margin: 0 0 0.5rem 0;
		text-transform: uppercase;
		font-weight: bold;
		color: var(--color-primary);
		font-size: 1.25rem;
	}

	.phonetic {
		color: var(--color-secondary);
		font-style: italic;
		margin: 0 0 1rem 0;
		font-family: 'Courier New', monospace;
		font-size: 1.1rem;
	}

	.loading-text {
		color: var(--color-secondary);
		font-style: italic;
		margin: 0.5rem 0;
	}

	.meanings-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.meaning {
		margin-bottom: 0.5rem;
	}

	.part-of-speech {
		color: var(--color-correct-position);
		font-size: 0.9rem;
		margin: 0 0 0.75rem 0;
		font-weight: bold;
		text-transform: capitalize;
		padding: 0.25rem 0.5rem;
		background: rgba(106, 170, 100, 0.1);
		border-radius: 0.25rem;
		display: inline-block;
	}

	.definition {
		margin-bottom: 0.75rem;
	}

	.definition-text {
		margin: 0 0 0.25rem 0;
		color: var(--color-primary);
		line-height: 1.5;
		font-size: 0.95rem;
	}

	.example {
		margin: 0;
		color: var(--color-secondary);
		font-style: italic;
		font-size: 0.9rem;
		padding-left: 0.5rem;
		border-left: 2px solid var(--gray-border);
	}

	.error-text {
		color: var(--red);
		margin: 0.5rem 0;
	}
</style>
