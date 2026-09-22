// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

const config = {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'class',
	theme: {
		extend: {
			fontFamily: {
				sans: ['Montserrat', 'Arial', 'sans-serif']
			},
			colors: {
				green: {
					600: '#009444'
				},
				// Фирменная палитра КСТ (~/.claude/skills/lessons-spo/references/style.md)
				kst: {
					blue: '#2F678C',
					graphite: '#405A67',
					ink: '#26333C',
					greyblue: '#9BAEB4',
					wine: '#8F5B60',
					red: '#C82E3E',
					bg: '#F5F6F6',
					card: '#FFFFFF',
					line: '#E3E7EA',
					muted: '#6B7A84'
				}
			},
			typography: (theme) => ({
				DEFAULT: {
					css: {
						// color: theme('colors.yellow.50'),
						textDecoration: 'none',
						textColor: '#000',
						/*a: {
							color: theme('colors.blue.200')
						},
						blockquote: {
							color: theme('colors.yellow.50')
						},
						h1: {
							color: theme('colors.yellow.50')
						},
						h2: {
							color: theme('colors.yellow.50')
						},
						h3: {
							color: theme('colors.yellow.50')
						},
						h4: {
							color: theme('colors.yellow.50')
						},
						th: {
							color: theme('colors.yellow.50')
						},
						strong: {
							color: theme('colors.yellow.50')
						},*/
						'code::before': {
							content: '""',
							'padding-left': '0.25rem'
						},
						'code::after': {
							content: '""',
							'padding-right': '0.25rem'
						},
						code: {
							'padding-top': '0.25rem',
							'padding-bottom': '0.25rem',
							fontWeight: '400',
							color: theme('colors.gray.100'),
							'border-radius': '0.25rem',
							backgroundColor: theme('colors.slate.800')
						}
					}
				}
			})
		}
	},

	plugins: [require('@tailwindcss/typography')]
};

module.exports = config;
