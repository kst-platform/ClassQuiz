<!--
	SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
	SPDX-FileCopyrightText: 2026 ГБПОУ КСТ

	SPDX-License-Identifier: MPL-2.0

	Футер «КСТ.Квиз» — без донатов, Mastodon и ссылок на автора апстрима.
-->
<script lang="ts">
	import LanguageToggle from './language-toggle.svelte';
</script>

<footer class="text-center text-white border-black w-screen">
	<div class="grid grid-cols-12 w-full pt-4 bg-[#26333C] pb-4">
		<p class="col-start-2 col-end-12 text-center w-full">
			КСТ.Квиз — платформа для живых квизов и опросов на занятиях.
			ГБПОУ «Колледж современных технологий имени Героя Советского Союза М.Ф. Панова»
		</p>
		<div
			class="flex flex-col items-center min-h-full h-full md:block hidden col-start-11 col-end-13"
		>
			<div class="my-auto mr-4">
				<LanguageToggle />
			</div>
		</div>
	</div>
	<div class="md:hidden block bg-[#26333C] pb-3">
		<div class="flex justify-center">
			<LanguageToggle />
		</div>
	</div>
</footer>
