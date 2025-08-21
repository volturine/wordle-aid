<script lang="ts">
	import theme from '$lib/stores/theme';
	import { Sun, Moon } from 'lucide-svelte';

	function toggleTheme() {
		theme.update((currentTheme) => (currentTheme === 'light' ? 'dark' : 'light'));
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
