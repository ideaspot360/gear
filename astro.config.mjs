// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// https://astro.build/config
export default defineConfig({
	site: 'https://gear.ideaspot360.com',
	redirects: {
		'/ko/part1-kinematics/01-conjugate-action': '/ko/series1-theory/part-a-spur/01-why-gears',
		'/ko/part1-kinematics/01-why-gears': '/ko/series1-theory/part-a-spur/01-why-gears',
		'/en/part1-kinematics/01-conjugate-action': '/en/series1-theory/part-a-spur/01-why-gears',
		'/en/part1-kinematics/01-why-gears': '/en/series1-theory/part-a-spur/01-why-gears',
		'/de/part1-kinematics/01-conjugate-action': '/de/series1-theory/part-a-spur/01-why-gears',
		'/de/part1-kinematics/01-why-gears': '/de/series1-theory/part-a-spur/01-why-gears',
		'/ja/part1-kinematics/01-conjugate-action': '/ja/series1-theory/part-a-spur/01-why-gears',
		'/ja/part1-kinematics/01-why-gears': '/ja/series1-theory/part-a-spur/01-why-gears',
		'/ko/part01-kinematics/01-why-gears': '/ko/series1-theory/part-a-spur/01-why-gears',
		'/en/part01-kinematics/01-why-gears': '/en/series1-theory/part-a-spur/01-why-gears',
		'/de/part01-kinematics/01-why-gears': '/de/series1-theory/part-a-spur/01-why-gears',
		'/ja/part01-kinematics/01-why-gears': '/ja/series1-theory/part-a-spur/01-why-gears',
	},
	markdown: {
		remarkPlugins: [remarkMath],
		rehypePlugins: [rehypeKatex],
	},
	integrations: [
		starlight({
			title: 'H-GEAR STUDIO Engineering',
			description: 'Official Multi-Language Technical Whitepaper & Gear Engineering Knowledge Base',
			defaultLocale: 'en',
			customCss: ['./src/styles/custom.css'],
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
					label: 'Series 1: Pure Gear Engineering',
					translations: {
						ko: '시리즈 1: 순수 기어 공학',
						de: 'Serie 1: Reine Zahnradtechnik',
						ja: 'シリーズ1: 純粋歯車工学理論',
					},
					items: [
						{
							label: 'Part A. Spur Gears (Ch 1~9)',
							translations: {
								ko: 'Part A. 평치차 공학 체계 (제1장 ~ 제9장)',
								de: 'Teil A. Stirnräder (Kapitel 1~9)',
								ja: 'Part A. 平歯車工学体系 (第1章〜第9章)',
							},
							items: [
								{ autogenerate: { directory: 'series1-theory/part-a-spur' } },
							],
						},
					],
				},
				{
					label: 'Series 2: Developer Architecture',
					translations: {
						ko: '시리즈 2: CAE/CAD 개발자 아키텍처',
						de: 'Serie 2: Entwickler-Architektur',
						ja: 'シリーズ2: CAE/CAD開発者アーキテクチャ',
					},
					items: [
						{
							label: 'Part 1. Differential Geometry',
							translations: {
								ko: 'Part 1. 전산 치형 기하학 및 미분기하학 (Ch 2-1~2-4)',
								de: 'Teil 1. Differentialgeometrie (Kapitel 2-1~2-4)',
								ja: 'Part 1. 計算歯形幾何学と微分幾何学 (第2-1章〜2-4章)',
							},
							items: [
								{ autogenerate: { directory: 'series2-architecture/part01-diff-geom' } },
							],
						},
					],
				},
			],
		}),
	],
});
