<script lang="ts">
	import type { DictionaryResponse } from '$lib/types';
	import { getWordDefinition } from '$lib/api';

	// Cache configuration
	const CACHE_KEY = 'word_definitions_cache';
	const CACHE_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days

	// Helper functions for localStorage cache
	function getCachedDefinition(word: string): DictionaryResponse | null {
		try {
			const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
			const cached = cache[word.toLowerCase()];

			if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
				return cached.data;
			}

			// Clean up expired entry
			if (cached) {
				delete cache[word.toLowerCase()];
				localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
			}
		} catch (e) {
			console.warn('Cache read error:', e);
		}
		return null;
	}

	function setCachedDefinition(word: string, data: DictionaryResponse): void {
		try {
			const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
			cache[word.toLowerCase()] = {
				data,
				timestamp: Date.now()
			};
			localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
		} catch (e) {
			console.warn('Cache write error:', e);
		}
	}

	let {
		selectedWord = '',
		bubblePos = { top: 0, bottom: 0, left: 0 },
		onClose,
		position = 'bottom'
	}: {
		selectedWord: string;
		bubblePos: { top: number; bottom: number; left: number };
		onClose: () => void;
		position: 'top' | 'bottom';
	} = $props();

	let wordDefinition = $state<DictionaryResponse | null>(null);
	let definitionLoading = $state(false);
	let definitionError = $state('');
	let bubbleEl = $state<HTMLDivElement | null>(null);

	// Watch for word changes
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

	// Global event handlers
	$effect(() => {
		function handleKeyDown(event: KeyboardEvent) {
			if (event.key === 'Escape') {
				onClose();
			}
		}

		function handleScroll() {
			onClose();
		}

		// handle clicks outside the bubble
		function handleClick(event: MouseEvent) {
			// This check ensures we don't close the overlay on the same click that opened it.
			if (bubbleEl && !bubbleEl.contains(event.target as Node)) {
				onClose();
			}
		}

		// Only add listeners when the overlay is visible
		if (selectedWord) {
			document.addEventListener('keydown', handleKeyDown);
			window.addEventListener('scroll', handleScroll, { once: true });
			setTimeout(() => {
				document.addEventListener('click', handleClick);
			});
		}

		// The effect's cleanup function automatically removes the listeners
		return () => {
			document.removeEventListener('keydown', handleKeyDown);
			window.removeEventListener('scroll', handleScroll);
			document.removeEventListener('click', handleClick);
		};
	});
</script>

{#if selectedWord}
	<div
		class="word-bubble"
		class:position-top={position === 'top'}
		style="top: {position === 'top'
			? bubblePos.top - 2
			: bubblePos.bottom + 2}px; left: {bubblePos.left}px;"
		bind:this={bubbleEl}
	>
		<div class="bubble-content">
			<button class="close-button" onclick={onClose}>✕</button>
			<h3>{selectedWord}</h3>

			{#if definitionLoading}
				<p>Loading definition...</p>
			{:else if definitionError}
				<p class="error-text">{definitionError}</p>
			{:else if wordDefinition && Array.isArray(wordDefinition) && wordDefinition.length > 0}
				{@const entry = wordDefinition[0]}
				{#if entry.phonetic}
					<p class="phonetic">/{entry.phonetic}/</p>
				{/if}

				{#if entry.meanings && entry.meanings.length > 0}
					{#each entry.meanings.slice(0, 2) as meaning}
						<div class="meaning">
							<h4 class="part-of-speech">{meaning.partOfSpeech}</h4>
							{#if meaning.definitions && meaning.definitions.length > 0}
								{#each meaning.definitions.slice(0, 2) as definition}
									<div class="definition">
										<p class="definition-text">{definition.definition}</p>
										{#if definition.example}
											<p class="example">"{definition.example}"</p>
										{/if}
									</div>
								{/each}
							{/if}
						</div>
					{/each}
				{/if}
			{:else}
				<p class="error-text">No definition available</p>
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

	.close-button {
		position: absolute;
		top: 0.3rem;
		right: 0.5rem;
		border: none;
		background: transparent;
		font-size: 1.2rem;
		cursor: pointer;
		color: var(--color-secondary);
	}

	.close-button:hover {
		color: var(--red);
	}

	.bubble-content h3 {
		margin: 0 0 0.5rem 0;
		text-transform: uppercase;
		font-weight: bold;
		color: var(--color-primary);
	}

	.phonetic {
		color: var(--color-secondary);
		font-style: italic;
		margin: 0 0 1rem 0;
		font-family: 'Courier New', monospace;
		font-size: 1.1rem;
	}

	.meaning {
		margin-bottom: 1.25rem;
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
	}

	.error-text {
		color: var(--red);
		margin: 0;
	}
</style>
