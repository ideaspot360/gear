// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// https://astro.build/config
export default defineConfig({
	site: 'https://gear.ideaspot360.com',
	markdown: {
		remarkPlugins: [remarkMath],
		rehypePlugins: [rehypeKatex],
	},
	integrations: [
		starlight({
			title: 'H-GEAR STUDIO Engineering',
			description: 'Official Multi-Language Technical Whitepaper & Gear Engineering Knowledge Base',
			defaultLocale: 'en',
			locales: {
				en: {
					label: 'English',
					lang: 'en',
				},
				de: {
					label: 'Deutsch',
					lang: 'de',
				},
				ja: {
					label: '日本語',
					lang: 'ja',
				},
				ko: {
					label: '한국어',
					lang: 'ko',
				},
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/ideaspot360/gear' }
			],
			head: [
				{
					tag: 'script',
					attrs: {
						src: 'https://www.googletagmanager.com/gtag/js?id=G-B7NFDK1QFM',
						async: true,
					},
				},
				{
					tag: 'script',
					content: "window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-B7NFDK1QFM');",
				},
				{
					tag: 'meta',
					attrs: {
						name: 'naver-site-verification',
						content: 'eb2c2728bb177a71bd7af42817abc0a39ec04fbc',
					},
				},
				{
					tag: 'link',
					attrs: {
						rel: 'stylesheet',
						href: 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css',
						crossorigin: 'anonymous',
					},
				},
			],
			sidebar: [
				{
					label: 'Part 1: Kinematics & Conjugate Meshing',
					translations: {
						de: 'Teil 1: Kinematik & Konjugierte Verzahnung',
						ja: '第1部: 歯形運動学と共役噛み合い理論',
						ko: '제1부: 치형 기구학 및 맞물림 기본 법칙',
					},
					items: [
						{ autogenerate: { directory: 'part1-kinematics' } },
					],
				},
			],
		}),
	],
});
