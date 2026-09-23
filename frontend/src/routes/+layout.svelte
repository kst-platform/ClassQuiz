<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/navbar.svelte';
	import { pathname } from '$lib/stores';
	import { navbarVisible } from '$lib/stores.svelte';

	import { initLocalizationContext } from '$lib/i18n';
	import { browser } from '$app/environment';
	import CommandPalette from '$lib/components/commandpalette.svelte';
	import { plausible_data_url } from '$lib/config';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	// Тёмной темы больше нет — убрана целиком (была "нестабильна": часть
	// из 145 компонентов рёбрендилась под неё, часть так и осталась на
	// исходной палитре ClassQuiz, из-за чего при переключении вперемешку
	// показывались то новые, то старые цвета). Фирменный стиль колледжа и
	// так предполагает только светлые экраны (~/.claude/skills/lessons-spo/
	// references/style.md). html.dark больше нигде не проставляется —
	// все dark:-варианты Tailwind по всему приложению теперь просто
	// неактивны, ничего чинить file-by-file не нужно.
	if (browser) {
		pathname.set(window.location.pathname);
		document.documentElement.classList.remove('dark');
	}
	// Язык платформы всегда русский, без переключателя и без определения
	// по браузеру (по прямому указанию пользователя).
	if (browser) {
		document.documentElement.lang = 'ru';
		document.documentElement.dir = 'ltr';
	}
	initLocalizationContext('ru');
</script>

<svelte:head>
	{#if plausible_data_url}
		<script
			defer
			data-domain={plausible_data_url}
			src="https://plausible.nexus.mawoka.eu/js/script.file-downloads.outbound-links.pageview-props.tagged-events.js"
		></script>
		<script>
			window.plausible =
				window.plausible ||
				function () {
					(window.plausible.q = window.plausible.q || []).push(arguments);
				};
		</script>
	{/if}
</svelte:head>

{#if navbarVisible.visible}
	<Navbar />
	<div class="pt-16">
		<div class="z-40"></div>
	</div>
{/if}
{@render children?.()}
<CommandPalette />

<style lang="scss">
	:global(html) {
		background-color: #f5f6f6;
		color: #26333c;
	}

	@keyframes background_animation {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}
</style>
