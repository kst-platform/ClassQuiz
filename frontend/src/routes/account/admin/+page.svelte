<!--
	SPDX-FileCopyrightText: 2026 ГБПОУ КСТ

	SPDX-License-Identifier: MPL-2.0

	Панель администратора «КСТ.Квиз»: одобрение регистраций, создание учёток,
	смена пароля, удаление (с подтверждением своим паролем). Доступна только
	учёткам из ADMINS (classquiz/auth.py get_admin_user) — при отсутствии
	прав API вернёт 403, страница покажет соответствующее сообщение.

	Не путать с /admin — там экран ведущего живой игры, это другая роль.
-->
<script lang="ts">
	import { onMount } from 'svelte';

	interface AdminUser {
		id: string;
		email: string;
		username: string;
		verified: boolean;
		approved: boolean;
		created_at: string;
	}

	let users: AdminUser[] = $state([]);
	let forbidden = $state(false);
	let loadError = $state('');
	let loading = $state(true);

	let newUser = $state({ email: '', username: '', password: '' });
	let createError = $state('');
	let createBusy = $state(false);

	let resetTarget: AdminUser | null = $state(null);
	let resetNewPassword = $state('');
	let resetAdminPassword = $state('');
	let resetError = $state('');
	let resetBusy = $state(false);

	let deleteTarget: AdminUser | null = $state(null);
	let deleteAdminPassword = $state('');
	let deleteError = $state('');
	let deleteBusy = $state(false);

	async function loadUsers() {
		loading = true;
		loadError = '';
		const res = await fetch('/api/v1/admin/users');
		if (res.status === 403) {
			forbidden = true;
			loading = false;
			return;
		}
		if (!res.ok) {
			loadError = 'Не удалось загрузить список учёток';
			loading = false;
			return;
		}
		users = await res.json();
		loading = false;
	}

	onMount(loadUsers);

	const pending = $derived(users.filter((u) => !u.approved));
	const approved = $derived(users.filter((u) => u.approved));

	async function approveUser(user: AdminUser) {
		const res = await fetch(`/api/v1/admin/users/${user.id}/approve`, { method: 'POST' });
		if (res.ok) {
			await loadUsers();
		} else {
			loadError = 'Не удалось одобрить учётку';
		}
	}

	async function createUser(e: Event) {
		e.preventDefault();
		createError = '';
		if (newUser.password.length < 8) {
			createError = 'Пароль должен быть не короче 8 символов';
			return;
		}
		createBusy = true;
		const res = await fetch('/api/v1/admin/users', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(newUser)
		});
		createBusy = false;
		if (res.ok) {
			newUser = { email: '', username: '', password: '' };
			await loadUsers();
		} else {
			const body = await res.json().catch(() => ({}));
			createError = body.detail ?? 'Не удалось создать учётку';
		}
	}

	function openResetModal(user: AdminUser) {
		resetTarget = user;
		resetNewPassword = '';
		resetAdminPassword = '';
		resetError = '';
	}

	async function submitReset(e: Event) {
		e.preventDefault();
		if (!resetTarget) return;
		if (resetNewPassword.length < 8) {
			resetError = 'Пароль должен быть не короче 8 символов';
			return;
		}
		resetBusy = true;
		const res = await fetch(`/api/v1/admin/users/${resetTarget.id}/reset-password`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ new_password: resetNewPassword, admin_password: resetAdminPassword })
		});
		resetBusy = false;
		if (res.ok) {
			resetTarget = null;
		} else {
			const body = await res.json().catch(() => ({}));
			resetError = body.detail ?? 'Не удалось сменить пароль';
		}
	}

	function openDeleteModal(user: AdminUser) {
		deleteTarget = user;
		deleteAdminPassword = '';
		deleteError = '';
	}

	async function submitDelete(e: Event) {
		e.preventDefault();
		if (!deleteTarget) return;
		deleteBusy = true;
		const res = await fetch('/api/v1/admin/user/id', {
			method: 'DELETE',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ user_id: deleteTarget.id, admin_password: deleteAdminPassword })
		});
		deleteBusy = false;
		if (res.ok) {
			deleteTarget = null;
			await loadUsers();
		} else {
			const body = await res.json().catch(() => ({}));
			deleteError = body.detail ?? 'Не удалось удалить учётку';
		}
	}
</script>

<svelte:head>
	<title>Управление учётками — КСТ.Квиз</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 pt-24 pb-16">
	<h1 class="text-2xl font-extrabold text-[#26333C] mb-6">Управление учётками преподавателей</h1>

	{#if forbidden}
		<p class="text-[#C82E3E] font-medium">
			У вашей учётки нет прав администратора этой платформы.
		</p>
	{:else if loading}
		<p class="text-[#6B7A84]">Загрузка…</p>
	{:else}
		{#if loadError}
			<p class="text-[#C82E3E] mb-4">{loadError}</p>
		{/if}

		{#if pending.length > 0}
			<section class="mb-8">
				<h2 class="text-lg font-bold text-[#26333C] mb-2">
					Заявки на регистрацию ({pending.length})
				</h2>
				<div class="border border-[#E3E7EA] rounded-md overflow-hidden">
					{#each pending as user (user.id)}
						<div
							class="flex items-center justify-between px-4 py-3 border-b border-[#E3E7EA] last:border-b-0 bg-[#F5F6F6]"
						>
							<div>
								<div class="font-medium text-[#26333C]">{user.username}</div>
								<div class="text-sm text-[#6B7A84]">{user.email}</div>
							</div>
							<button class="admin-button" onclick={() => approveUser(user)}>Одобрить</button>
						</div>
					{/each}
				</div>
			</section>
		{/if}

		<section class="mb-8">
			<h2 class="text-lg font-bold text-[#26333C] mb-2">
				Все учётки ({approved.length})
			</h2>
			<div class="border border-[#E3E7EA] rounded-md overflow-hidden">
				{#each approved as user (user.id)}
					<div
						class="flex items-center justify-between px-4 py-3 border-b border-[#E3E7EA] last:border-b-0"
					>
						<div>
							<div class="font-medium text-[#26333C]">{user.username}</div>
							<div class="text-sm text-[#6B7A84]">{user.email}</div>
						</div>
						<div class="flex gap-2">
							<button class="action-button" onclick={() => openResetModal(user)}>
								Сменить пароль
							</button>
							<button
								class="action-button text-[#C82E3E]"
								onclick={() => openDeleteModal(user)}
							>
								Удалить
							</button>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<section>
			<h2 class="text-lg font-bold text-[#26333C] mb-2">Создать учётку</h2>
			<form class="flex flex-col gap-3 max-w-sm" onsubmit={createUser}>
				<input
					class="border border-[#E3E7EA] rounded-sm px-3 py-2"
					type="text"
					placeholder="Имя пользователя"
					required
					bind:value={newUser.username}
				/>
				<input
					class="border border-[#E3E7EA] rounded-sm px-3 py-2"
					type="email"
					placeholder="Почта"
					required
					bind:value={newUser.email}
				/>
				<input
					class="border border-[#E3E7EA] rounded-sm px-3 py-2"
					type="password"
					placeholder="Пароль (минимум 8 символов)"
					required
					bind:value={newUser.password}
				/>
				{#if createError}
					<p class="text-[#C82E3E] text-sm">{createError}</p>
				{/if}
				<button class="admin-button w-fit" disabled={createBusy}>
					{createBusy ? 'Создаём…' : 'Создать учётку'}
				</button>
			</form>
		</section>
	{/if}
</div>

{#if resetTarget}
	<div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
		<form
			class="bg-white rounded-md p-6 w-full max-w-sm flex flex-col gap-3"
			onsubmit={submitReset}
		>
			<h3 class="font-bold text-[#26333C]">
				Новый пароль для {resetTarget.username}
			</h3>
			<input
				class="border border-[#E3E7EA] rounded-sm px-3 py-2"
				type="password"
				placeholder="Новый пароль"
				required
				bind:value={resetNewPassword}
			/>
			<input
				class="border border-[#E3E7EA] rounded-sm px-3 py-2"
				type="password"
				placeholder="Ваш пароль для подтверждения"
				required
				bind:value={resetAdminPassword}
			/>
			{#if resetError}
				<p class="text-[#C82E3E] text-sm">{resetError}</p>
			{/if}
			<div class="flex gap-2 justify-end">
				<button type="button" class="action-button" onclick={() => (resetTarget = null)}>
					Отмена
				</button>
				<button class="admin-button" disabled={resetBusy}>
					{resetBusy ? 'Сохраняем…' : 'Сохранить'}
				</button>
			</div>
		</form>
	</div>
{/if}

{#if deleteTarget}
	<div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
		<form
			class="bg-white rounded-md p-6 w-full max-w-sm flex flex-col gap-3"
			onsubmit={submitDelete}
		>
			<h3 class="font-bold text-[#26333C]">
				Удалить учётку {deleteTarget.username}?
			</h3>
			<p class="text-sm text-[#6B7A84]">
				Действие необратимо. Введите свой пароль администратора для подтверждения.
			</p>
			<input
				class="border border-[#E3E7EA] rounded-sm px-3 py-2"
				type="password"
				placeholder="Ваш пароль"
				required
				bind:value={deleteAdminPassword}
			/>
			{#if deleteError}
				<p class="text-[#C82E3E] text-sm">{deleteError}</p>
			{/if}
			<div class="flex gap-2 justify-end">
				<button type="button" class="action-button" onclick={() => (deleteTarget = null)}>
					Отмена
				</button>
				<button class="admin-button bg-[#C82E3E] hover:bg-[#a8242f]" disabled={deleteBusy}>
					{deleteBusy ? 'Удаляем…' : 'Удалить'}
				</button>
			</div>
		</form>
	</div>
{/if}
