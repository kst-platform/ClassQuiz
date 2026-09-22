<!--
	Логотип «КСТ.Квиз»: простая иконка + текстовый wordmark.
	Фирменная палитра колледжа — ~/.claude/skills/lessons-spo/references/style.md.
	Без изображений-логотипов КСТ/МО — только цвет и типографика.
-->
<script lang="ts">
	interface Props {
		size?: 'sm' | 'md';
	}
	let { size = 'md' }: Props = $props();
	const iconPx = size === 'sm' ? 28 : 34;
	const textClass = size === 'sm' ? 'text-lg' : 'text-xl lg:text-2xl';
</script>

<span class="inline-flex items-center gap-2">
	<svg
		width={iconPx}
		height={iconPx}
		viewBox="0 0 34 34"
		xmlns="http://www.w3.org/2000/svg"
		aria-hidden="true"
	>
		<rect width="34" height="34" rx="8" fill="#2F678C" />
		<path
			d="M12 13.2c0-2.9 2.2-4.9 5.2-4.9 3 0 5.1 1.9 5.1 4.6 0 2-1.1 3.3-2.7 4.2-1.3.7-1.7 1.2-1.7 2.1v.5h-2.9v-.7c0-1.7.8-2.7 2.3-3.5 1.3-.7 1.9-1.4 1.9-2.5 0-1.2-.9-2-2.2-2-1.3 0-2.2.8-2.3 2.2H12Z"
			fill="#FFFFFF"
		/>
		<circle cx="17.1" cy="24.4" r="1.7" fill="#C82E3E" />
	</svg>
	<span class={`font-extrabold tracking-tight text-[#26333C] ${textClass}`} style="font-family:'Montserrat',Arial,sans-serif">
		КСТ<span class="text-[#2F678C]">.</span>Квиз
	</span>
</span>
