<!--
	SPDX-FileCopyrightText: 2026 ГБПОУ КСТ

	SPDX-License-Identifier: MPL-2.0

	Управление группами студентов: своя учётка видит только свои группы
	(classquiz/routers/groups.py проверяет владельца на каждый запрос).
	Группа привязывается к игре на экране запуска (start_game.svelte) —
	тогда студент на входе выбирает своё имя из списка, а не вводит ник.
-->
<script lang="ts">
	import { onMount } from 'svelte';

	interface GroupMember {
		id: string;
		full_name: string;
	}
	interface GroupListItem {
		id: string;
		name: string;
		created_at: string;
		member_count: number;
	}
	interface GroupDetail extends GroupListItem {
		members: GroupMember[];
	}

	let groups: GroupListItem[] = $state([]);
	let loading = $state(true);
	let loadError = $state('');

	let newGroupName = $state('');
	let createBusy = $state(false);
	let createError = $state('');

	let selected: GroupDetail | null = $state(null);
	let selectedLoading = $state(false);

	let bulkNames = $state('');
	let addBusy = $state(false);
	let addError = $state('');

	let renameValue = $state('');
	let renameBusy = $state(false);

	let deleteTarget: GroupListItem | null = $state(null);
	let deleteBusy = $state(false);

	async function loadGroups() {
		loading = true;
		loadError = '';
		const res = await fetch('/api/v1/groups');
		if (!res.ok) {
			loadError = 'Не удалось загрузить список групп';
			loading = false;
			return;
		}
		groups = await res.json();
		loading = false;
	}

	onMount(loadGroups);

	async function createGroup(e: Event) {
		e.preventDefault();
		const name = newGroupName.trim();
		if (!name) return;
		createBusy = true;
		createError = '';
		const res = await fetch('/api/v1/groups', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name })
		});
		createBusy = false;
		if (res.ok) {
			newGroupName = '';
			await loadGroups();
		} else {
			const body = await res.json().catch(() => ({}));
			createError = body.detail ?? 'Не удалось создать группу';
		}
	}

	async function openGroup(g: GroupListItem) {
		selectedLoading = true;
		bulkNames = '';
		addError = '';
		const res = await fetch(`/api/v1/groups/${g.id}`);
		selectedLoading = false;
		if (res.ok) {
			selected = await res.json();
			renameValue = selected.name;
		}
	}

	async function addMembers(e: Event) {
		e.preventDefault();
		if (!selected || !bulkNames.trim()) return;
		addBusy = true;
		addError = '';
		const res = await fetch(`/api/v1/groups/${selected.id}/members`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ names: bulkNames })
		});
		addBusy = false;
		if (res.ok) {
			selected = await res.json();
			bulkNames = '';
			await loadGroups();
		} else {
			const body = await res.json().catch(() => ({}));
			addError = body.detail ?? 'Не удалось добавить студентов';
		}
	}

	async function removeMember(memberId: string) {
		if (!selected) return;
		const res = await fetch(`/api/v1/groups/${selected.id}/members/${memberId}`, {
			method: 'DELETE'
		});
		if (res.ok) {
			await openGroup(selected);
			await loadGroups();
		}
	}

	async function submitRename(e: Event) {
		e.preventDefault();
		if (!selected) return;
		const name = renameValue.trim();
		if (!name) return;
		renameBusy = true;
		const res = await fetch(`/api/v1/groups/${selected.id}`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name })
		});
		renameBusy = false;
		if (res.ok) {
			await openGroup(selected);
			await loadGroups();
		}
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		deleteBusy = true;
		const res = await fetch(`/api/v1/groups/${deleteTarget.id}`, { method: 'DELETE' });
		deleteBusy = false;
		if (res.ok) {
			if (selected?.id === deleteTarget.id) selected = null;
			deleteTarget = null;
			await loadGroups();
		}
	}
</script>

<svelte:head>
	<title>Группы — КСТ.Квиз</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-4 pt-24 pb-16 grid grid-cols-1 md:grid-cols-2 gap-8">
	<section>
		<h1 class="text-2xl font-extrabold text-[#26333C] mb-4">Мои группы</h1>

		{#if loading}
			<p class="text-[#6B7A84]">Загрузка…</p>
		{:else}
			{#if loadError}
				<p class="text-[#C82E3E] mb-3">{loadError}</p>
			{/if}
			<div class="border border-[#E3E7EA] rounded-md overflow-hidden mb-6">
				{#if groups.length === 0}
					<p class="px-4 py-3 text-[#6B7A84]">Групп пока нет</p>
				{/if}
				{#each groups as g (g.id)}
					<div
						class="flex items-center justify-between gap-2 px-4 py-3 border-b border-[#E3E7EA] last:border-b-0 cursor-pointer hover:bg-[#F5F6F6]"
						class:bg-[#F5F6F6]={selected?.id === g.id}
						onclick={() => openGroup(g)}
					>
						<div class="min-w-0">
							<div class="font-medium text-[#26333C] truncate">{g.name}</div>
							<div class="text-sm text-[#6B7A84]">{g.member_count} студентов</div>
						</div>
						<button
							class="action-button text-[#C82E3E] shrink-0"
							onclick={(e) => {
								e.stopPropagation();
								deleteTarget = g;
							}}
						>
							Удалить
						</button>
					</div>
				{/each}
			</div>

			<form class="flex flex-col gap-2 max-w-sm" onsubmit={createGroup}>
				<label class="font-bold text-[#26333C]" for="new-group-name">Новая группа</label>
				<input
					id="new-group-name"
					class="border border-[#E3E7EA] rounded-sm px-3 py-2"
					type="text"
					placeholder="Например, СОБ-213/25"
					bind:value={newGroupName}
				/>
				{#if createError}
					<p class="text-[#C82E3E] text-sm">{createError}</p>
				{/if}
				<button class="admin-button w-fit" disabled={createBusy}>
					{createBusy ? 'Создаём…' : 'Создать'}
				</button>
			</form>
		{/if}
	</section>

	<section>
		{#if selectedLoading}
			<p class="text-[#6B7A84]">Загрузка…</p>
		{:else if selected}
			<h2 class="text-xl font-bold text-[#26333C] mb-4">{selected.name}</h2>

			<form class="flex gap-2 mb-4" onsubmit={submitRename}>
				<input class="border border-[#E3E7EA] rounded-sm px-3 py-2 flex-1" bind:value={renameValue} />
				<button class="action-button" disabled={renameBusy}>Переименовать</button>
			</form>

			<div class="border border-[#E3E7EA] rounded-md overflow-hidden mb-4 max-h-64 overflow-y-auto">
				{#if selected.members.length === 0}
					<p class="px-4 py-3 text-[#6B7A84]">В группе пока нет студентов</p>
				{/if}
				{#each selected.members as m (m.id)}
					<div
						class="flex items-center justify-between px-4 py-2 border-b border-[#E3E7EA] last:border-b-0"
					>
						<span class="text-[#26333C]">{m.full_name}</span>
						<button class="action-button text-[#C82E3E]" onclick={() => removeMember(m.id)}>
							Убрать
						</button>
					</div>
				{/each}
			</div>

			<form class="flex flex-col gap-2" onsubmit={addMembers}>
				<label class="font-bold text-[#26333C]" for="bulk-names">
					Добавить студентов (по одному ФИО на строку — можно вставить прямо из ведомости)
				</label>
				<textarea
					id="bulk-names"
					class="border border-[#E3E7EA] rounded-sm px-3 py-2 h-32"
					placeholder={'Иванова А.П.\nПетров И.С.\n...'}
					bind:value={bulkNames}
				></textarea>
				{#if addError}
					<p class="text-[#C82E3E] text-sm">{addError}</p>
				{/if}
				<button class="admin-button w-fit" disabled={addBusy}>
					{addBusy ? 'Добавляем…' : 'Добавить'}
				</button>
			</form>
		{:else}
			<p class="text-[#6B7A84]">Выберите группу слева, чтобы посмотреть список студентов.</p>
		{/if}
	</section>
</div>

{#if deleteTarget}
	<div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
		<div class="bg-white rounded-md p-6 w-full max-w-sm flex flex-col gap-3">
			<h3 class="font-bold text-[#26333C]">Удалить группу «{deleteTarget.name}»?</h3>
			<p class="text-sm text-[#6B7A84]">
				Список студентов группы удалится безвозвратно. Уже сыгранные игры и их результаты
				это не затронет.
			</p>
			<div class="flex gap-2 justify-end">
				<button class="action-button" onclick={() => (deleteTarget = null)}>Отмена</button>
				<button
					class="admin-button bg-[#C82E3E] hover:bg-[#a8242f]"
					disabled={deleteBusy}
					onclick={confirmDelete}
				>
					{deleteBusy ? 'Удаляем…' : 'Удалить'}
				</button>
			</div>
		</div>
	</div>
{/if}
