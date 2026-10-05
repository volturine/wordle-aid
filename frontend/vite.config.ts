import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => ({
	plugins: [
		sveltekit(),
		SvelteKitPWA({
			registerType: 'autoUpdate',
			injectRegister: null,
			kit: { adapterFallback: '404.html' },
			manifest: {
				name: 'Wordle Aid — Find possible answers',
				short_name: 'Wordle Aid',
				description:
					'Enter Wordle guesses, mark letter colors, and find possible answers with definitions.',
				start_url: '/',
				display: 'standalone',
				background_color: '#f5f4ef',
				theme_color: '#376a34',
				orientation: 'portrait-primary',
				scope: '/',
				id: '/?source=pwa',
				lang: 'en',
				dir: 'ltr',
				categories: ['games', 'education'],
				icons: [
					{
						src: '/favicon-16x16.png',
						sizes: '16x16',
						type: 'image/png',
						purpose: 'any'
					},
					{
						src: '/favicon-32x32.png',
						sizes: '32x32',
						type: 'image/png',
						purpose: 'any'
					},
					{
						src: '/favicon-192x192.png',
						sizes: '192x192',
						type: 'image/png',
						purpose: 'any'
					},
					{
						src: '/favicon-512x512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'any'
					}
				]
			}
		})
	],
	server: {
		port: 3000,
		allowedHosts: ['wordle-aid.com', 'dev.wordle-aid.com'],
		proxy: {
			// `uv run pywrangler dev` in worker/; override with WORKER_ORIGIN.
			'/api': {
				target: loadEnv(mode, '.', '').WORKER_ORIGIN || 'http://localhost:8787',
				changeOrigin: true
			}
		}
	}
}));
