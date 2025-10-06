<script lang="ts">
	import theme from '$lib/stores/theme';
	import { Sun, Moon } from 'lucide-svelte';

	function toggleTheme() {
		document.body.classList.add('theme-transitioning');

		theme.update((currentTheme) => (currentTheme === 'light' ? 'dark' : 'light'));

		requestAnimationFrame(() => {
			document.body.classList.remove('theme-transitioning');
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
