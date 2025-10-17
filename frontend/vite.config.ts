import { sveltekit } from '@sveltejs/kit/vite';
import { VitePWA } from 'vite-plugin-pwa'

export default {
	plugins: [
		sveltekit(),
		VitePWA({
			registerType: 'autoUpdate',
			workbox: {
				globPatterns: ['**/*.{js,css,html,ico,png,svg,webmanifest,json,xml}']
			},
			manifest: {
				name: 'Wordle Aid - Your Daily Wordle Helper',
				short_name: 'Wordle Aid',
				description: 'Get hints and solutions for your daily Wordle puzzle. Your helpful Wordle assistant with word definitions and smart suggestions.',
				start_url: '/',
				display: 'standalone',
				background_color: '#ffffff',
				theme_color: '#6aaa64',
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
				],
			}
		})
	],
	server: {
		port: 3000,
		allowedHosts: [
			"localhost",
			"wordle-aid.com",
			"dev.wordle-aid.com"
		],
		proxy: {
			'/api': 'http://localhost:8000'
		}
	},
};