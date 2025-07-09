import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';

export default {
	plugins: [
		tailwindcss(),
		sveltekit(),
		SvelteKitPWA({
			registerType: 'autoUpdate',
			workbox: {
				globPatterns: ['**/*.{js,css,html,ico,png,svg,webmanifest}']
			},
			manifest: {
				name: 'Wordle-Aid',
				short_name: 'Wordle-Aid',
				start_url: '/',
				display: 'standalone',
				background_color: '#ffffff',
				theme_color: '#000000',
				icons: [
					{
						src: '/favicon-192x192.png',
						sizes: '192x192',
						type: 'image/png'
					},
					{
						src: '/favicon-512x512.png',
						sizes: '512x512',
						type: 'image/png'
					}
				]
			}
		})
	],
	server: {
		port: 3000,
		allowedHosts: [
			"localhost",
			"wordle-aid.com"
		],
	},
};