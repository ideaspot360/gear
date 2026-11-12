import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

/**
 * H-GEAR STUDIO 기술 백서 전용 조건부 Zod 메타데이터 스키마
 * 
 * [아키텍처 원칙]:
 * 1. 일반 문서 및 랜딩 페이지(index.mdx)의 정적 빌드 붕괴를 방지하기 위해 기본 필드는 .optional()로 수용.
 * 2. 기술 백서(part 또는 gear_type이 선언된 문서)에 대해서는 .superRefine()을 통해 학술 필수 필드를 100% 엄격 강제.
 */
const technicalPaperSchema = z.object({
  part: z.number().int().min(1).optional().describe('도서 Part 번호 (예: 1)'),
  chapter: z.number().int().min(1).optional().describe('도서 Chapter 번호 (예: 1)'),
  gear_type: z.enum([
    'spur', 'helical', 'internal', 'bevel', 'hypoid', 'worm', 'planetary'
  ]).optional().describe('다루는 기어 공학 대상 유형'),
  standards: z.array(z.string()).min(1).optional().describe('근거 국제 표준 (예: ISO 21771, DIN 3960)'),
  required_diagrams: z.array(z.string()).min(1).optional().describe('본문 필수 임베딩 도안 파일명 목록'),
  academic_level: z.enum(['undergraduate', 'graduate', 'industrial_expert']).optional(),
  equations_hash: z.string().length(64).optional().describe('KaTeX 공학 수식 SHA-256 불변 해시'),
  kernel_verified: z.boolean().optional().describe('백엔드 profile_service 기하학 검증 완료 여부'),
  doi: z.string().optional().describe('학술 인용 식별자 (선택)'),
  review_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional().describe('최종 공학 감사 일자 (YYYY-MM-DD)'),
}).superRefine((data, ctx) => {
  const isTechnicalPaper = data.part !== undefined || data.gear_type !== undefined;

  if (isTechnicalPaper) {
    if (data.part === undefined) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 'part' 번호가 필수입니다.", path: ['part'] });
    }
    if (data.chapter === undefined) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 'chapter' 번호가 필수입니다.", path: ['chapter'] });
    }
    if (data.gear_type === undefined) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 'gear_type' 지정이 필수입니다.", path: ['gear_type'] });
    }
    if (!data.standards || data.standards.length === 0) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 최소 1개 이상의 'standards'(국제 표준) 목록이 필수입니다.", path: ['standards'] });
    }
    if (!data.required_diagrams || data.required_diagrams.length === 0) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 'required_diagrams' 필수 도안 목록이 필요합니다.", path: ['required_diagrams'] });
    }
    if (data.academic_level === undefined) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 'academic_level' (undergraduate/graduate/industrial_expert) 지정이 필수입니다.", path: ['academic_level'] });
    }
    if (!data.equations_hash || data.equations_hash.length !== 64) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 64자리 SHA-256 'equations_hash'가 필수입니다.", path: ['equations_hash'] });
    }
    if (data.kernel_verified !== true) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 백엔드 profile_service 검증 완료 플래그('kernel_verified: true')가 필수입니다.", path: ['kernel_verified'] });
    }
    if (!data.review_date) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "기술 백서는 최종 공학 감사 일자('review_date': YYYY-MM-DD)가 필수입니다.", path: ['review_date'] });
    }
  }
});

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: technicalPaperSchema
    })
  })
};
