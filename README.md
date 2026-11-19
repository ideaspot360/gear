# 01_GEAR_MANAGER

> **H-GEAR STUDIO 생태계 통합 매니저 & 다국어 엔지니어링 퍼블리싱 허브**

본 프로젝트는 초정밀 공학 기어 설계 소프트웨어 **H-GEAR STUDIO**의 다국어(KO, EN, DE, JA) 기술 블로그, 공식 포털 웹사이트, 사용자 회원 관리, 라이선스 매니저를 총괄하는 독립 관리 프로젝트입니다.

---

## 🌟 주요 기능 및 구성

1. **글로벌 4개 국어 공학 기술 블로그**:
   - 프레임워크: Astro v5 + Starlight
   - 수식 렌더링: KaTeX (Remark-Math / Rehype-KaTeX)
   - 이미지 뷰어: PhotoSwipe 딥 줌 & 팬
   - 32종 기하학 벡터 SVG 도안 및 44편 고품질 기술 백서

2. **4대 철벽 품질 보증 게이트키퍼**:
   - **Gate 1 (`npm run gate`)**: 마크다운 문체, 금지어 및 휴먼 오리지널리티 감사 (`blog-gatekeeper`)
   - **Gate 2 (`npm run lint:images`)**: 4개 국어 이미지 참조 및 언어 격리 무결성 5대 규칙 감사
   - **Gate 3 (도안 최종 육안검수 철벽게이트)**: 모든 공학 도안(KO/EN/DE/JA)에 대한 에이전트/서브에이전트 직접 육안검수 실시 및 지적 0건 무한 개선 루프 통과
   - **Gate 4 (`npm run build`)**: 정적 사이트 완전 빌드 검증

3. **Article 13 준수 엣지 배포 파이프라인**:
   - `publish_to_edge.py`: 내부 도안 스크립트, 테스트 코드, 수치 스펙의 누출을 100% 차단하고 GitHub Pages 공개 저장소(`ideaspot360/gear.git`)로 안전하게 배포

4. **차기 확장 로드맵**:
   - H-GEAR 공식 브랜드 웹사이트
   - 사용자 계정 및 라이선스 키 관리 포털
   - 클라이언트 앱 업데이트 및 텔레메트리

---

## 🚀 빠른 시작 (Quick Start)

### 의존성 설치
```bash
npm install
```

### 개발 서버 실행
```bash
npm run dev
# 브라우저 접속: http://localhost:4321
```

### 4대 철벽 게이트 검증
```bash
npm run gate
npm run lint:images
# Gate 3: 도안 최종 육안검수 (에이전트/서브에이전트 지적 0건 PASS 확인)
npm run build
```

### 공개 엣지 배포
```bash
npm run publish:edge "chore: release updates"
```

---

## 📖 상세 지침 및 헌법
모든 개발 및 인수인계 지침은 [AGENTS.md](./AGENTS.md)를 참조하십시오.
