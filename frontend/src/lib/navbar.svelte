<!--
	SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
	SPDX-FileCopyrightText: 2026 ГБПОУ КСТ

	SPDX-License-Identifier: MPL-2.0

	Переключатель тёмной темы убран целиком (23.09.2026) — платформа
	только светлая, см. +layout.svelte.
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { signedIn, pathname } from '$lib/stores';
	import Logo from '$lib/brand/logo.svelte';
	import { beforeNavigate } from '$app/navigation';
	import { draw, slide } from 'svelte/transition';
	import { registration_disabled } from './config';

	const { t } = getLocalization();

	let menuIsClosed = $state(true);
	const toggleMenu = () => {
		menuIsClosed = !menuIsClosed;
	};

	beforeNavigate(() => {
		menuIsClosed = true; // Closes menu to let the user see the page beneath
	});
</script>

<nav class="w-screen px-4 lg:px-10 py-2 fixed backdrop-blur-2xl bg-white/70 shadow-md z-30 top-0">
	<!-- Desktop navbar -->
	<div class="hidden lg:flex lg:items-center lg:flex-row lg:justify-between">
		<div class="lg:flex lg:items-center lg:flex-row gap-1">
			<a href="/" class="link-hover px-3 lg:px-5">
				<Logo />
			</a>
			<a class="btn-nav border-2 rounded-sm" href="/play">{$t('words.play')}</a>
			<a class="btn-nav" href="/explore">{$t('words.explore')}</a>
			<a class="btn-nav" href="/search">{$t('words.search')}</a>
			{#if $signedIn}
				<a class="btn-nav" href="/dashboard">{$t('words.dashboard')}</a>
				<a class="btn-nav" href="/dashboard/groups">Группы</a>
			{:else}
				<a class="btn-nav" href="/docs">{$t('words.docs')}</a>
			{/if}
		</div>
		<div class="lg:flex lg:items-center lg:flex-row gap-1">
			{#if $signedIn}
				<a class="btn-nav" href="/api/v1/users/logout">{$t('words.logout')}</a>
			{:else}
				{#if !registration_disabled}
					<a class="btn-nav" href="/account/register">{$t('words.register')}</a>
				{/if}

				<a class="btn-nav" href="/account/login?returnTo={$pathname}">{$t('words.login')}</a
				>
			{/if}
		</div>
	</div>

	<!-- Mobile navbar -->
	<div class="lg:hidden">
		<!-- Navbar header -->
		<div class="flex items-center justify-between">
			<a href="/" class="link-hover px-3 lg:px-5">
				<Logo size="sm" />
			</a>
			<a class="btn-nav flex" href="/play">{$t('words.play')}</a>

			<!-- Open/Close menu -->
			<div class="flex items-center">
				{#if menuIsClosed}
					<button
						class="px-3"
						id="open-menu"
						onclick={toggleMenu}
						aria-label="Open navbar"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="#000000"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M3 6h18M3 12h18M3 18h18" />
						</svg>
					</button>
				{:else}
					<button
						class="px-3"
						id="close-menu"
						onclick={toggleMenu}
						aria-label="Close navbar"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="#000000"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							><path in:draw|global={{ duration: 300 }} d="M18 6 6 18" /><path
								in:draw|global={{ duration: 300 }}
								d="m6 6 12 12"
							/></svg
						>
					</button>
				{/if}
			</div>
		</div>

		<!-- Navbar content -->
		{#if !menuIsClosed}
			<div class="flex flex-col" transition:slide|global={{ duration: 400 }}>
				<a class="btn-nav" href="/explore">{$t('words.explore')}</a>
				<a class="btn-nav" href="/search">{$t('words.search')}</a>
				{#if $signedIn}
					<a class="btn-nav" href="/dashboard">{$t('words.dashboard')}</a>
					<a class="btn-nav" href="/dashboard/groups">Группы</a>
				{:else}
					<a class="btn-nav" href="/docs">{$t('words.docs')}</a>
				{/if}

				<hr class="my-1 border" />
				{#if $signedIn}
					<a class="btn-nav" href="/api/v1/users/logout">{$t('words.logout')}</a>
				{:else}
					{#if !registration_disabled}
						<a class="btn-nav" href="/account/register">{$t('words.register')}</a>
					{/if}

					<a class="btn-nav" href="/account/login?returnTo={$pathname}"
						>{$t('words.login')}</a
					>
				{/if}
			</div>
		{/if}
	</div>
</nav>
