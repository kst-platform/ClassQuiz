<!--
	SPDX-FileCopyrightText: 2026 ГБПОУ КСТ

	SPDX-License-Identifier: MPL-2.0

	Главная страница КСТ.Квиз. Переписана заново вместо маркетингового
	лендинга апстрима ClassQuiz (донаты, "немецкий сервер", скриншоты
	чужого продукта, упоминания Kahoot/classquiz.de) — ничего из этого
	не относится к закрытой платформе колледжа.

	Специально без dark:-вариантов: только фирменная светлая палитра
	(~/.claude/skills/lessons-spo/references/style.md) — там же принцип
	"тёмные экраны не делать", распространён и сюда.
-->
<script lang="ts">
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import Footer from '$lib/footer.svelte';
	import Logo from '$lib/brand/logo.svelte';

	navbarVisible.visible = true;

	const steps = [
		{
			title: 'Создайте квиз',
			text: 'Вручную в редакторе или импортом готовых вопросов из формата GIFT — тот же формат, что используется в курсах колледжа.'
		},
		{
			title: 'Привяжите группу',
			text: 'Список студентов один раз вносится в «Группы» — на входе в игру студент выбирает своё имя из списка, а не вводит случайный ник.'
		},
		{
			title: 'Проведите игру',
			text: 'Студенты подключаются с телефона по PIN-коду или QR, вы управляете темпом с экрана преподавателя и сохраняете результаты.'
		}
	];
</script>

<svelte:head>
	<title>КСТ.Квиз</title>
	<meta
		name="description"
		content="КСТ.Квиз — платформа для живых квизов и опросов на занятиях в ГБПОУ «Колледж современных технологий имени Героя Советского Союза М.Ф. Панова»."
	/>
</svelte:head>

<div class="min-h-screen flex flex-col bg-[#F5F6F6]">
	<section class="pt-28 pb-16 px-4 text-center">
		<div class="flex justify-center mb-6">
			<Logo />
		</div>
		<h1 class="text-3xl sm:text-4xl font-extrabold text-[#26333C] max-w-2xl mx-auto">
			Живые квизы и опросы на занятиях
		</h1>
		<p class="text-lg text-[#6B7A84] max-w-xl mx-auto mt-4">
			Платформа для преподавателей ГБПОУ «Колледж современных технологий имени Героя
			Советского Союза М.Ф. Панова».
		</p>
		<div class="flex flex-wrap gap-4 justify-center mt-8">
			<a
				href="/play"
				class="px-6 py-3 rounded-lg bg-[#2F678C] text-white font-semibold hover:bg-[#265674] transition-colors"
			>
				Присоединиться к игре
			</a>
			<a
				href="/account/login"
				class="px-6 py-3 rounded-lg border border-[#2F678C] text-[#2F678C] font-semibold hover:bg-white transition-colors"
			>
				Войти как преподаватель
			</a>
		</div>
	</section>

	<section class="px-4 pb-20 max-w-4xl mx-auto w-full">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			{#each steps as step, i (step.title)}
				<div class="bg-white rounded-lg shadow-sm border border-[#E3E7EA] p-5">
					<div
						class="w-8 h-8 rounded-full bg-[#2F678C] text-white flex items-center justify-center font-bold mb-3"
					>
						{i + 1}
					</div>
					<h2 class="font-bold text-[#26333C] mb-1">{step.title}</h2>
					<p class="text-sm text-[#6B7A84]">{step.text}</p>
				</div>
			{/each}
		</div>
	</section>
</div>
<Footer />
