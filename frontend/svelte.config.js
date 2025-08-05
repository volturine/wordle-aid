import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: null, // Set to 'index.html' if using SPA-style fallback
			precompress: false
		})
	}
};
