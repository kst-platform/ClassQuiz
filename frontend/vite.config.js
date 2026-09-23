// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { sveltekit } from '@sveltejs/kit/vite';

/** @type {import("vite").UserConfig} */
const config = {
	plugins: [
		sveltekit(),
		{
			name: 'configure-response-headers',
			configureServer: (server) => {
				server.middlewares.use((_req, res, next) => {
					/*        res.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
        res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
        res.setHeader("Access-Control-Allow-Origin", "https://ncs3.classquiz.de");*/
					next();
				});
			}
		}
	],
	server: {
		port: 3000,
		// Без этого прокси весь fetch('/api/...') и Socket.IO из браузера
		// уходят на сам dev-сервер (порт 3000), а не на бэкенд (uvicorn,
		// порт 8000) — именно так выглядели "не работает поиск/обзор/
		// документация": запрос 404-ился прямо на порту фронтенда, до
		// бэкенда не долетая вовсе. В docker-compose эту роль на проде
		// играет Caddy (Caddyfile-docker), здесь — сам Vite.
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true
			},
			'/socket.io': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
				ws: true
			}
		}
	},
	preview: {
		port: 3000
	},
	optimizeDeps: {
		include: ['swiper', 'tippy.js']
	},
	build: {
		sourcemap: true
	}

	/* Trying

	ssr: {
		noExternal: ['@ckeditor/*'],
	}

 end trying*/
};

export default config;
