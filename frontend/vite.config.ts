import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { sveltekit } from '@sveltejs/kit/vite';
import type { Plugin } from 'vite';
import { defineConfig, loadEnv } from 'vite';
import { VitePWA, type VitePluginPWAAPI } from 'vite-plugin-pwa';

const adapterFallback = '404.html';
const staticAdapter = adapter({
	pages: 'build',
	assets: 'build',
	fallback: adapterFallback,
	precompress: false,
	strict: true
});

const pwaPlugins = VitePWA({
	outDir: 'build',
	registerType: 'autoUpdate',
	injectRegister: null,
	includeManifestIcons: false,
	workbox: {
		navigateFallback: adapterFallback,
		globPatterns: ['**/*.{html,js,css,ico,png,svg,webmanifest,json,xml}'],
		globIgnores: ['sw.js', 'workbox-*.js'],
		dontCacheBustURLsMatching: /_app\/immutable\//
	},
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
			{ src: '/favicon-16x16.png', sizes: '16x16', type: 'image/png', purpose: 'any' },
			{ src: '/favicon-32x32.png', sizes: '32x32', type: 'image/png', purpose: 'any' },
			{ src: '/favicon-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
			{ src: '/favicon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any' }
		]
	}
});

const pwaPlugin = pwaPlugins.find((plugin) => plugin.name === 'vite-plugin-pwa') as
	(Plugin & { api?: VitePluginPWAAPI }) | undefined;
const pwaBuildPlugin = pwaPlugins.find((plugin) => plugin.name === 'vite-plugin-pwa:build');

if (pwaBuildPlugin) {
	delete pwaBuildPlugin.transformIndexHtml;
	delete pwaBuildPlugin.closeBundle;
}

const svelteKitPwaPlugins = pwaPlugins.filter(
	(plugin) => plugin.name !== 'vite-plugin-pwa:pwa-assets'
);

const staticAdapterWithPwa: typeof staticAdapter = {
	...staticAdapter,
	async adapt(builder) {
		await staticAdapter.adapt(builder);
		await pwaPlugin?.api?.generateSW();
	}
};

export default defineConfig(({ mode }) => ({
	plugins: [
		sveltekit({
			preprocess: [vitePreprocess()],
			adapter: staticAdapterWithPwa,
			serviceWorker: { register: false },
			// Ensure the app is served from the root path
			paths: { base: '' }
		}),
		...svelteKitPwaPlugins
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
