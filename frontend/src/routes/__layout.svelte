<script>
	import { page } from '$app/stores';
</script>

{#if $page.status === 404}
	<h1>404: Not Found</h1>
	<p>Sorry, the page you requested could not be found.</p>
{:else}
	<slot />
{/if}
