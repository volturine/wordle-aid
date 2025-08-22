import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
	preprocess: [vitePreprocess()],

	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: 'index.html', // Enable SPA fallback for better PWA support
			fallback: '404.html', // This line is important
			precompress: false,
			strict: true
		}),

		// Ensure the app is served from the root path
		paths: {
			base: ''
		},
	}
};
