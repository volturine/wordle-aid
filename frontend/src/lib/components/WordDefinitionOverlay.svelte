<script lang="ts">
	import { on } from 'svelte/events';
	import { fade } from 'svelte/transition';
	import { prefersReducedMotion } from 'svelte/motion';
	import { X } from '@lucide/svelte';
	import type { DictionaryResponse } from '#lib/types.js';
	import { getWordDefinition } from '#lib/api.js';
	import { getCachedDefinition, setCachedDefinition } from '#lib/utils/definitionCache.js';

	let {
		selectedWord = '',
		bubblePos = { top: 0, bottom: 0, left: 0, maxHeight: 320 },
		onClose,
		onUseWord,
		position = 'bottom'
	}: {
		selectedWord: string;
		bubblePos: { top: number; bottom: number; left: number; maxHeight: number };
		onClose: (restoreFocus?: boolean) => void;
		onUseWord?: (word: string) => void;
		position: 'top' | 'bottom';
	} = $props();

	let wordDefinition = $state<DictionaryResponse | null>(null);
	let definitionLoading = $state(false);
	let definitionError = $state('');
	let bubbleEl = $state<HTMLDivElement | null>(null);

	const overlayStyle = $derived(
		position === 'top'
			? `top: ${bubblePos.top - 8}px; left: ${bubblePos.left}px; max-height: ${bubblePos.maxHeight}px;`
			: `top: ${bubblePos.bottom + 8}px; left: ${bubblePos.left}px; max-height: ${bubblePos.maxHeight}px;`
	);

	$effect(() => {
		const requestedWord = selectedWord;
		if (!requestedWord) {
			wordDefinition = null;
			definitionLoading = false;
			definitionError = '';
			return;
		}

		let active = true;
		definitionError = '';
		definitionLoading = true;
		wordDefinition = null;

		const cached = getCachedDefinition(requestedWord);
		if (cached) {
			wordDefinition = cached;
			definitionLoading = false;
		} else {
			getWordDefinition(requestedWord)
				.then((definition) => {
					if (!active) return;
					wordDefinition = definition;
					setCachedDefinition(requestedWord, definition);
				})
				.catch((cause) => {
					if (!active) return;
					console.error('Definition error:', cause);
					definitionError =
						'We couldn’t load this definition. Check your connection and try again.';
				})
				.finally(() => {
					if (active) definitionLoading = false;
				});
		}

		return () => {
			active = false;
		};
	});

	$effect(() => {
		if (!selectedWord || !bubbleEl) return;

		bubbleEl.querySelector<HTMLButtonElement>('button')?.focus();
		const handleKeydown = (event: KeyboardEvent) => {
			if (event.key === 'Escape') {
				event.preventDefault();
				onClose();
			}
		};
		const handlePointerDown = (event: PointerEvent) => {
			if (bubbleEl && !bubbleEl.contains(event.target as Node)) onClose(false);
		};
		const handleScroll = () => onClose();
		const removeKeydown = on(document, 'keydown', handleKeydown);
		const removePointerDown = on(document, 'pointerdown', handlePointerDown);
		const removeScroll = on(window, 'scroll', handleScroll, { passive: true });

		return () => {
			removeKeydown();
			removePointerDown();
			removeScroll();
		};
	});
</script>

{#if selectedWord}
	<div
		class="word-bubble"
		class:position-top={position === 'top'}
		style={overlayStyle}
		bind:this={bubbleEl}
		role="dialog"
		aria-modal="false"
		aria-labelledby="definition-title"
		transition:fade={{ duration: prefersReducedMotion.current ? 0 : 160 }}
	>
		<div class="bubble-content">
			<div class="bubble-header">
				<button
					class="use-word-button"
					aria-label={`Use ${selectedWord} as a guess`}
					onclick={() => {
						onUseWord?.(selectedWord);
						onClose(false);
					}}
				>
					Use guess
				</button>
				<button class="close-button" aria-label="Close definition" onclick={() => onClose()}>
					<X size={18} aria-hidden="true" />
				</button>
			</div>

			<h2 id="definition-title" class="word-title">{selectedWord}</h2>

			{#if definitionLoading}
				<p class="loading-text" role="status" aria-live="polite">Loading definition…</p>
			{:else if definitionError}
				<p class="error-text" role="alert">{definitionError}</p>
			{:else if wordDefinition?.definitions?.length}
				<div class="meanings-container">
					{#each wordDefinition.definitions.slice(0, 3) as meaning (meaning.definition)}
						<article class="meaning">
							<h3 class="part-of-speech">{meaning.partOfSpeech}</h3>
							<p class="definition-text">{meaning.definition}</p>
						</article>
					{/each}
				</div>
			{:else}
				<p class="empty-definition">No definition is available for this word.</p>
			{/if}
		</div>
	</div>
{/if}

<style>
	.word-bubble {
		position: fixed;
		z-index: 1000;
		width: min(24rem, calc(100vw - 2rem));
		transform: translateX(-50%);
	}

	.word-bubble.position-top {
		transform: translate(-50%, -100%);
	}

	.bubble-content {
		position: relative;
		max-height: inherit;
		overflow: auto;
		padding: var(--space-4);
		border: 1px solid var(--line);
		border-radius: var(--radius-card);
		background: var(--surface-raised);
		box-shadow: var(--shadow);
	}

	.bubble-header {
		display: flex;
		justify-content: flex-end;
		align-items: center;
		gap: var(--space-2);
		margin-bottom: var(--space-3);
	}

	.use-word-button {
		padding: 0 var(--space-3);
		border-color: var(--green);
		background: var(--green);
		color: var(--action-ink);
		font-weight: 700;
	}

	.use-word-button:hover:not(:disabled) {
		border-color: var(--green-hover);
		background: var(--green-hover);
	}

	.close-button {
		display: grid;
		width: 44px;
		place-items: center;
		padding: 0;
	}

	.word-title {
		margin: 0 0 var(--space-3);
		font-size: 1.25rem;
		line-height: 1.3;
		text-transform: uppercase;
	}

	.loading-text,
	.empty-definition {
		margin: 0;
		color: var(--muted);
		line-height: 1.5;
	}

	.meanings-container {
		display: grid;
		gap: var(--space-3);
	}

	.meaning {
		margin: 0;
	}

	.part-of-speech {
		display: inline-block;
		margin: 0 0 var(--space-2);
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-badge);
		background: var(--page);
		color: var(--green);
		font-size: 0.875rem;
		font-weight: 700;
		text-transform: capitalize;
	}

	.definition-text {
		margin: 0;
		color: var(--ink);
		font-size: 1rem;
		line-height: 1.5;
	}

	.error-text {
		margin: 0;
		color: var(--danger);
		line-height: 1.5;
	}

	@media (max-width: 520px) {
		.word-bubble {
			width: calc(100vw - 1.5rem);
		}
	}
</style>
