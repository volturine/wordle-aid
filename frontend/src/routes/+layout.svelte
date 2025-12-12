<script lang="ts">
	import { page } from '$app/state';

	let { children } = $props();

	const status = $derived(page.status);
</script>

{#if status === 404}
	<h1>404: Not Found</h1>
	<p>Sorry, the page you requested could not be found.</p>
{:else}
	{@render children()}
{/if}
