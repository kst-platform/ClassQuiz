// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import i18next from 'i18next';
import ru from './locales/ru.json';

import type { i18n } from 'i18next';

// КСТ.Квиз — платформа одного русскоязычного колледжа, переключатель
// языка убран по прямому указанию пользователя ("не надо давать менять
// язык"). Раньше здесь стоял i18next-browser-languagedetector, который
// асинхронно определял язык браузера и мог переопределить русский уже
// после того, как он был явно выставлен — гонка, из-за которой у
// пользователя с не-русской локалью браузера всё показывалось по-английски
// несмотря на fallbackLng. Теперь язык всегда и безусловно 'ru', других
// языковых бандлов не грузим — меньше кода, нечему давать сбой.
export class I18nService {
	i18n: i18n;

	constructor() {
		this.i18n = i18next;
		this.initialize();
	}
	t(key: string, replacements?: Record<string, unknown>): string {
		return this.i18n.t(key, replacements);
	}

	// Initializing i18n
	initialize(): void {
		this.i18n.init({
			lng: 'ru',
			compatibilityJSON: 'v4',
			fallbackLng: 'ru',
			debug: false,
			defaultNS: 'translation',
			interpolation: {
				escapeValue: false
			},
			returnEmptyString: false,
			simplifyPluralSuffix: true
		});
		this.i18n.addResourceBundle('ru', 'translation', ru);
	}

	// Оставлено ради translation-service.ts (Writable-стор locale дёргает
	// этот метод при .set()) — переключателя языка в UI больше нет, так что
	// на практике не вызывается, но пусть будет, а не падает.
	changeLanguage(language: string): void {
		this.i18n.changeLanguage(language);
	}
}
