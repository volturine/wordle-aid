<script lang="ts">
	import theme from '#lib/stores/theme.js';
	import { Sun, Moon } from '@lucide/svelte';

	function toggleTheme() {
		document.body.classList.add('theme-transitioning');

		theme.update((currentTheme) => (currentTheme === 'light' ? 'dark' : 'light'));

		void document.body.offsetHeight;
		requestAnimationFrame(() =>
			requestAnimationFrame(() => document.body.classList.remove('theme-transitioning'))
		);
	}
</script>

<button
	onclick={toggleTheme}
	class="theme-switch"
	aria-label={$theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'}
	aria-pressed={$theme === 'dark'}
	title={$theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'}
>
	{#if $theme === 'light'}
		<Moon aria-hidden="true" />
	{:else}
		<Sun aria-hidden="true" />
	{/if}
</button>

<style>
	.theme-switch {
		flex: 0 0 44px;
		width: 44px;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--surface-raised);
		color: var(--ink);
	}

	.theme-switch:hover:not(:disabled) {
		background: var(--page);
	}

	@media (prefers-reduced-motion: reduce) {
		.theme-switch {
			transition-duration: 0.01ms;
		}
	}
</style>
