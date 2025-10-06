<script lang="ts">
	import theme from '$lib/stores/theme';
	import { Sun, Moon } from 'lucide-svelte';

	function toggleTheme() {
		// Add class to disable transitions during theme change
		document.body.classList.add('theme-transitioning');

		theme.update((currentTheme) => (currentTheme === 'light' ? 'dark' : 'light'));

		// Remove class after a brief delay to re-enable transitions
		requestAnimationFrame(() => {
			setTimeout(() => {
				document.body.classList.remove('theme-transitioning');
			}, 50);
		});
	}
</script>

<button on:click={toggleTheme} class="theme-switch">
	{#if $theme === 'light'}
		<Moon />
	{:else}
		<Sun />
	{/if}
</button>

<style>
	.theme-switch {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		color: var(--color-primary);
	}
</style>
