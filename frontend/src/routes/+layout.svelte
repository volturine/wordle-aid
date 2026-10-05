<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { onMount } from 'svelte';
	import { pwaInfo } from 'virtual:pwa-info';
	import '../app.css';

	let { children } = $props();

	const status = $derived(page.status);
	const webManifestLink = $derived(pwaInfo?.webManifest.linkTag ?? '');

	onMount(() => {
		if (pwaInfo) {
			void import('virtual:pwa-register').then(({ registerSW }) => {
				registerSW({ immediate: true });
			});
		}
	});
</script>

<svelte:head>
	{@html webManifestLink}
	{#if status === 404}
		<title>Page not found | Wordle Aid</title>
		<meta name="description" content="The page you requested could not be found." />
	{/if}
</svelte:head>

{#if status === 404}
	<main class="not-found">
		<p class="eyebrow">Wordle Aid</p>
		<h1>Page not found</h1>
		<p>That page isn’t here. Return to the Wordle helper and continue your puzzle.</p>
		<a href={resolve('/')}>Open Wordle Aid</a>
	</main>
{:else}
	{@render children()}
{/if}

<style>
	.not-found {
		width: min(100% - 2rem, 42rem);
		min-height: 100vh;
		margin: 0 auto;
		display: grid;
		align-content: center;
		justify-items: start;
		color: var(--ink);
	}

	.eyebrow {
		color: var(--muted);
		font-size: 0.875rem;
		font-weight: 650;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	h1 {
		margin: 0 0 0.75rem;
		font-size: 2rem;
	}

	.not-found a {
		margin-top: 0.5rem;
		color: var(--green);
		font-weight: 650;
	}
</style>
