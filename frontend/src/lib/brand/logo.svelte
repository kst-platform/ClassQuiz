<!--
	SPDX-FileCopyrightText: 2026 ГБПОУ КСТ

	SPDX-License-Identifier: MPL-2.0

	Логотип «КСТ.Квиз»: присланная иконка (assets/brand/logo-icon.png,
	обрезана по содержимому, прозрачный фон) + текстовый wordmark шрифтом.
	Текст остаётся HTML/CSS, а не частью картинки — чтобы не размывался
	при увеличении (на главной странице лого крупнее, чем в навбаре).
-->
<script lang="ts">
	import IconSrc from '$lib/assets/brand/logo-icon.png';

	interface Props {
		size?: 'sm' | 'md';
	}
	let { size = 'md' }: Props = $props();
	const iconPx = size === 'sm' ? 28 : 34;
	const textClass = size === 'sm' ? 'text-lg' : 'text-xl lg:text-2xl';
</script>

<span class="inline-flex items-center gap-2">
	<img src={IconSrc} alt="" width={iconPx} height={iconPx} aria-hidden="true" />
	<span
		class={`font-extrabold tracking-tight text-[#26333C] ${textClass}`}
		style="font-family:'Montserrat',Arial,sans-serif"
	>
		КСТ<span class="text-[#2F678C]">.</span>Квиз
	</span>
</span>
