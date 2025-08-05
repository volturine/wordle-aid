import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: 'index.html', // Enable SPA fallback for better PWA support
			precompress: false,
			strict: true
		}),
		files: {
			assets: 'static'
		}
	}
};
