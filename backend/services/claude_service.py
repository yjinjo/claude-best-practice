"""
Claude AI 서비스
페르소나별 맞춤형 문서 요약 생성
"""

import json
import os
from typing import Any, Dict

import httpx


class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-haiku-20240307"  # Fast and cost-effective for MVP

        # 페르소나별 프롬프트 템플릿
        self.persona_prompts = {
            "developer": {
                "name": "개발자",
                "description": "기술적 구현에 집중하는 백엔드/프론트엔드 개발자",
                "focus_areas": [
                    "기술적 요구사항 및 제약사항",
                    "API 명세 및 데이터 구조",
                    "구현 방법 및 기술 스택",
                    "성능 및 보안 고려사항",
                    "코드 관련 가이드라인",
                ],
                "prompt_template": """당신은 경험 많은 개발자입니다. 다음 Confluence 문서를 개발자 관점에서 요약해주세요.

다음 영역에 특히 집중해서 요약해주세요:
- 기술적 요구사항 및 제약사항
- API 명세 및 데이터 구조
- 구현 방법 및 기술 스택
- 성능 및 보안 고려사항
- 코드 관련 가이드라인

문서 내용에서 개발과 직접적으로 관련이 없는 비즈니스 전략이나 마케팅 관련 내용은 간략히 언급하거나 생략해도 됩니다.

요약은 다음 형식으로 작성해주세요:
## 🔧 기술 요약
## 📋 구현 요구사항
## ⚠️ 주의사항 및 제약
## 📊 성능/보안 고려사항

문서 제목: {title}

문서 내용:
{content}""",
            },
            "product_manager": {
                "name": "기획자/프로덕트 매니저",
                "description": "비즈니스 목표와 제품 전략에 집중하는 기획자",
                "focus_areas": [
                    "비즈니스 목표 및 전략",
                    "일정 및 마일스톤",
                    "리스크 및 이슈사항",
                    "의사결정 포인트",
                    "이해관계자 및 커뮤니케이션",
                ],
                "prompt_template": """당신은 경험 많은 프로덕트 매니저입니다. 다음 Confluence 문서를 기획자/PM 관점에서 요약해주세요.

다음 영역에 특히 집중해서 요약해주세요:
- 비즈니스 목표 및 전략
- 일정 및 마일스톤
- 리스크 및 이슈사항
- 의사결정 포인트
- 이해관계자 및 커뮤니케이션

기술적인 세부 구현 내용보다는 비즈니스 임팩트와 프로젝트 관리 관점에서 중요한 정보에 집중해주세요.

요약은 다음 형식으로 작성해주세요:
## 🎯 비즈니스 목표
## 📅 주요 일정 및 마일스톤
## ⚠️ 리스크 및 이슈
## 🤝 의사결정 포인트

문서 제목: {title}

문서 내용:
{content}""",
            },
            "designer": {
                "name": "UX/UI 디자이너",
                "description": "사용자 경험과 인터페이스 디자인에 집중하는 디자이너",
                "focus_areas": [
                    "사용자 경험 및 인터페이스",
                    "디자인 요구사항 및 가이드라인",
                    "사용자 리서치 및 피드백",
                    "인터랙션 및 플로우",
                    "브랜딩 및 비주얼 요소",
                ],
                "prompt_template": """당신은 경험 많은 UX/UI 디자이너입니다. 다음 Confluence 문서를 디자이너 관점에서 요약해주세요.

다음 영역에 특히 집중해서 요약해주세요:
- 사용자 경험 및 인터페이스 요구사항
- 디자인 가이드라인 및 스타일
- 사용자 리서치 및 피드백
- 인터랙션 및 사용자 플로우
- 브랜딩 및 비주얼 요소

기술적인 구현 세부사항이나 복잡한 비즈니스 로직보다는 사용자 관점과 디자인 관련 내용에 집중해주세요.

요약은 다음 형식으로 작성해주세요:
## 🎨 UX/UI 요구사항
## 👥 사용자 관점
## 📱 인터페이스 가이드라인
## 🔄 사용자 플로우

문서 제목: {title}

문서 내용:
{content}""",
            },
            "general": {
                "name": "일반",
                "description": "모든 직군이 이해할 수 있는 일반적인 요약",
                "focus_areas": [
                    "핵심 내용 및 주요 포인트",
                    "전체적인 맥락 및 배경",
                    "중요한 결론 및 시사점",
                    "액션 아이템 및 다음 단계",
                    "관련 이해관계자 정보",
                ],
                "prompt_template": """다음 Confluence 문서를 누구나 이해할 수 있도록 명확하고 간결하게 요약해주세요.

다음 사항을 포함해서 요약해주세요:
- 문서의 핵심 내용과 주요 포인트
- 전체적인 맥락과 배경 정보
- 중요한 결론이나 시사점
- 실행해야 할 액션 아이템이나 다음 단계
- 관련된 이해관계자나 담당자 정보

전문 용어는 최대한 쉽게 설명하고, 모든 직군의 사람들이 이해할 수 있도록 작성해주세요.

요약은 다음 형식으로 작성해주세요:
## 📄 문서 개요
## 🎯 핵심 내용
## 💡 주요 시사점
## ✅ 액션 아이템

문서 제목: {title}

문서 내용:
{content}""",
            },
        }

    async def generate_summary(
        self,
        content: str,
        persona: str,
        title: str = "",
        document_structure: Dict = None,
    ) -> str:
        """
        페르소나별 맞춤형 요약 생성
        """
        try:
            # 페르소나 프롬프트 가져오기
            persona_config = self.persona_prompts.get(persona)
            if not persona_config:
                raise Exception(f"지원하지 않는 페르소나: {persona}")

            # API 키가 없거나 콘텐츠가 비어있으면 Mock 요약 반환
            if not self.api_key:
                print("Claude API 키가 설정되지 않았습니다. Mock 요약을 반환합니다.")
                return self._generate_mock_summary(persona, title)

            if not content.strip():
                print("문서 내용이 비어있습니다. Mock 요약을 반환합니다.")
                return self._generate_mock_summary(persona, title)

            print(
                f"Claude API 호출 시작 - 페르소나: {persona}, 문서 제목: {title}, 내용 길이: {len(content)}"
            )

            # 프롬프트 생성 (헤더 구조 활용)
            if document_structure and document_structure.get("sections"):
                prompt = self._generate_structured_prompt(
                    persona_config, title, document_structure
                )
            else:
                prompt = persona_config["prompt_template"].format(
                    title=title or "제목 없음",
                    content=content[:4000],  # Claude 토큰 제한 고려
                )

            # Claude API 호출
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }

            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url, headers=headers, json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    summary = result["content"][0]["text"]
                    print(f"Claude API 호출 성공 - 요약 길이: {len(summary)}")
                    return summary
                else:
                    print(
                        f"Claude API 호출 실패: {response.status_code} - {response.text}"
                    )
                    # API 호출 실패 시 Mock 요약 반환
                    return self._generate_mock_summary(persona, title)

        except Exception as e:
            print(f"Claude 요약 생성 오류: {str(e)}")
            # 오류 발생 시 Mock 요약 반환
            return self._generate_mock_summary(persona, title)

    def _generate_mock_summary(self, persona: str, title: str) -> str:
        """Mock 요약 생성 (개발/테스트용)"""

        persona_config = self.persona_prompts.get(
            persona, self.persona_prompts["developer"]
        )
        persona_name = persona_config["name"]

        mock_summaries = {
            "developer": f"""## 🔧 기술 요약
{title or "ConfluSum 프로젝트"}는 FastAPI와 Claude AI를 활용한 문서 요약 서비스입니다.

## 📋 구현 요구사항
- **Backend**: FastAPI (Python) - REST API 서버 구축
- **Frontend**: HTML/CSS/JavaScript - 반응형 웹 인터페이스
- **AI Integration**: Claude API를 통한 자연어 처리
- **Database**: 피드백 데이터 저장용 경량 DB

## ⚠️ 주의사항 및 제약
- Claude API 토큰 제한: 요청당 최대 4,000 토큰
- Confluence API 인증: Basic Auth 또는 API Token 필요
- CORS 설정: 프론트엔드-백엔드 통신을 위한 적절한 CORS 정책

## 📊 성능/보안 고려사항
- 응답 시간 목표: 평균 30초 이내
- API 키 보안: 환경변수를 통한 민감정보 관리
- 에러 핸들링: 사용자 친화적 오류 메시지 제공""",
            "product_manager": f"""## 🎯 비즈니스 목표
{title or "ConfluSum 프로젝트"}는 기업 내 문서 처리 효율성을 90% 향상시키는 것을 목표로 합니다.

## 📅 주요 일정 및 마일스톤
- **Day 1**: MVP 개발 완료 및 내부 테스트
- **Week 1**: 베타 테스트 (10명 대상) 및 피드백 수집
- **Month 1**: 사용자 피드백 분석 후 개선사항 반영
- **Month 3**: 500명 활성 사용자 확보 목표

## ⚠️ 리스크 및 이슈
- **기술 리스크**: Claude API 의존성으로 인한 서비스 안정성
- **시장 리스크**: 사용자 니즈 검증 필요 (70% 이상 만족도 목표)
- **경쟁 리스크**: 대기업의 유사 서비스 출시 가능성

## 🤝 의사결정 포인트
- **Go/No-Go 결정**: 1주일 후 베타 테스트 결과 기반
- **성공 기준**: 70% 이상 긍정 피드백, 30초 이내 응답시간
- **실패 기준**: 50% 이하 만족도 시 프로젝트 피벗 검토""",
            "designer": f"""## 🎨 UX/UI 요구사항
{title or "ConfluSum 프로젝트"}는 직관적인 3단계 사용자 플로우를 제공합니다.

## 👥 사용자 관점
- **주 사용자**: 중소 IT 기업의 개발자, 기획자, 디자이너
- **사용 시나리오**: 긴 Confluence 문서를 역할에 맞게 빠르게 파악
- **사용자 니즈**: 복잡한 설정 없이 URL만으로 즉시 사용 가능

## 📱 인터페이스 가이드라인
- **디자인 원칙**: 단순함, 명확성, 접근성
- **색상**: 차분한 블루 계열 (#3498db) 메인 컬러
- **타이포그래피**: 시스템 폰트 사용으로 가독성 최적화
- **반응형**: 모바일/데스크톱 모든 환경에서 일관된 경험

## 🔄 사용자 플로우
1. **URL 입력**: Confluence 문서 링크 붙여넣기
2. **페르소나 선택**: 직관적인 카드 형태 인터페이스
3. **요약 확인**: 로딩 애니메이션과 함께 결과 표시
4. **피드백 제공**: 간단한 👍/👎 버튼으로 만족도 수집""",
            "general": f"""## 📄 문서 개요
{title or "ConfluSum 프로젝트"}는 AI를 활용해 긴 Confluence 문서를 사용자의 역할에 맞게 요약해주는 서비스입니다.

## 🎯 핵심 내용
- **서비스 목적**: 업무 효율성 향상을 위한 문서 요약 자동화
- **주요 기능**: URL 입력 → 페르소나 선택 → AI 맞춤형 요약 생성
- **대상 사용자**: 기업 내 모든 직군 (개발자, 기획자, 디자이너 등)
- **기술 스택**: FastAPI 백엔드 + React 프론트엔드 + Claude AI

## 💡 주요 시사점
- **시간 절약**: 30분 문서를 3분 만에 핵심 파악 가능
- **맞춤형 정보**: 각 직군별 관심사에 맞는 내용 추출
- **사용 편의성**: 복잡한 설정 없이 URL만으로 즉시 이용
- **피드백 시스템**: 지속적인 서비스 개선을 위한 사용자 의견 수집

## ✅ 액션 아이템
- **단기**: MVP 개발 완료 후 내부 테스트 진행
- **중기**: 베타 사용자 10명 대상 1주일 테스트
- **장기**: 사용자 피드백 기반 기능 개선 및 확장
- **성공 지표**: 70% 이상 긍정 피드백, 30초 이내 응답 시간 달성""",
        }

        return mock_summaries.get(persona, mock_summaries["developer"])

    def _generate_structured_prompt(
        self, persona_config: Dict, title: str, document_structure: Dict
    ) -> str:
        """
        문서 구조를 활용한 구조화된 프롬프트 생성
        """
        persona_name = persona_config["name"]
        focus_areas = persona_config["focus_areas"]

        # 헤더별 내용 정리
        sections_content = ""
        for i, section in enumerate(
            document_structure.get("sections", [])[:10]
        ):  # 최대 10개 섹션
            content = document_structure["content_by_section"].get(section, "")
            if content.strip():
                sections_content += (
                    f"\n### {section}\n{content[:500]}\n"  # 각 섹션당 500자 제한
                )

        # 구조화된 프롬프트 템플릿
        structured_prompt = f"""당신은 경험 많은 {persona_name}입니다. 다음 Confluence 문서를 {persona_name} 관점에서 헤더 구조에 따라 체계적으로 요약해주세요.

다음 영역에 특히 집중해서 요약해주세요:
{chr(10).join([f"- {area}" for area in focus_areas])}

**문서 제목**: {title or "제목 없음"}

**문서 구조 및 내용**:
{sections_content}

**요약 작성 지침**:
1. 각 헤더(섹션)별로 {persona_name} 관점에서 중요한 내용만 추출
2. 헤더 구조를 유지하면서 요약 제시
3. {persona_name}에게 불필요한 세부사항은 생략
4. 실행 가능한 인사이트나 액션 아이템 중심으로 정리

다음 형식으로 헤더별 요약을 작성해주세요:

## 📋 주요 섹션별 요약

### [섹션명]
- 핵심 내용 요약
- {persona_name} 관점의 중요 포인트

## 💡 {persona_name} 관점 종합 분석
- 전체 문서에서 {persona_name}가 주목해야 할 핵심 사항
- 연관된 섹션들 간의 관계 및 시사점

## ✅ 액션 아이템 및 다음 단계
- {persona_name}가 취해야 할 구체적인 행동 사항
- 후속 검토가 필요한 영역"""

        return structured_prompt

    def get_persona_info(self, persona: str) -> Dict[str, Any]:
        """페르소나 정보 반환"""
        return self.persona_prompts.get(persona, {})
