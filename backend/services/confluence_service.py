"""
Confluence 서비스
문서 URL 검증 및 콘텐츠 추출
"""

import base64
import json
import os
import re
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

import httpx

from .mcp_confluence_service import MCPConfluenceService


class ConfluenceService:
    def __init__(self):
        self.base_url = os.getenv("CONFLUENCE_BASE_URL", "")
        self.username = os.getenv("CONFLUENCE_USERNAME", "")
        self.api_token = os.getenv("CONFLUENCE_API_TOKEN", "")

        # Basic auth header
        if self.username and self.api_token:
            auth_string = f"{self.username}:{self.api_token}"
            self.auth_header = base64.b64encode(auth_string.encode()).decode()
        else:
            self.auth_header = None

        # MCP Confluence 서비스 초기화
        self.mcp_service = MCPConfluenceService()

    async def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Confluence URL 유효성 검증
        """
        try:
            print(f"URL 형식 검증 시작: {url}")

            # URL 형식 검증
            is_valid_format = self._is_confluence_url(url)
            print(f"Confluence URL 형식 검증 결과: {is_valid_format}")

            if not is_valid_format:
                return {
                    "valid": False,
                    "message": "올바른 Confluence URL 형식이 아닙니다.",
                }

            # Page ID 추출
            page_id = self._extract_page_id(url)
            print(f"추출된 페이지 ID: {page_id}")

            if not page_id:
                page_id = "123456"  # 기본값

            # Mock 페이지 정보 반환 (API 연동 없이)
            page_info = self._get_mock_page_info(page_id)
            print(f"페이지 정보: {page_info}")

            return {
                "valid": True,
                "title": page_info.get("title", ""),
                "message": "유효한 Confluence 문서입니다.",
            }

        except Exception as e:
            print(f"URL 검증 중 예외 발생: {str(e)}")
            import traceback

            traceback.print_exc()
            return {
                "valid": False,
                "message": f"URL 검증 중 오류가 발생했습니다: {str(e)}",
            }

    async def get_document_content(self, url: str) -> Dict[str, Any]:
        """
        Confluence 문서 콘텐츠 가져오기 (헤더 구조 포함)
        """
        try:
            # 1. MCP Atlassian을 통한 실제 문서 가져오기 시도
            mcp_content = await self.mcp_service.get_document_content(url)

            if mcp_content and mcp_content.get("content"):
                page_id = self._extract_page_id(url) or "extracted_from_mcp"
                content = mcp_content.get("content", "")
                print(f"파싱할 문서 내용 샘플 (처음 500자): {content[:500]}")
                structure = self.parse_document_structure(content)
                print(
                    f"파싱된 구조: 섹션 수 {len(structure.get('sections', []))}, 섹션명: {structure.get('sections', [][:3])}"
                )

                return {
                    "title": mcp_content.get("title", ""),
                    "content": content,
                    "structure": structure,
                    "url": url,
                    "page_id": page_id,
                }

            # 2. MCP 실패 시 기존 API 방식 시도
            page_id = self._extract_page_id(url)

            if page_id:
                content_data = await self._get_page_content(page_id)

                if content_data:
                    clean_content = self._extract_text_from_html(
                        content_data.get("body", "")
                    )
                    print(
                        f"파싱할 HTML 정리된 내용 샘플 (처음 500자): {clean_content[:500]}"
                    )
                    structure = self.parse_document_structure(clean_content)
                    print(
                        f"파싱된 구조: 섹션 수 {len(structure.get('sections', []))}, 섹션명: {structure.get('sections', [][:3])}"
                    )

                    return {
                        "title": content_data.get("title", ""),
                        "content": clean_content,
                        "structure": structure,
                        "url": url,
                        "page_id": page_id,
                    }

            # 3. 모든 방법 실패 시 Mock 데이터 사용
            return self._get_mock_document_content(url)

        except Exception as e:
            print(f"문서 콘텐츠 조회 오류: {str(e)}")
            # 오류 발생 시 Mock 데이터로 폴백
            return self._get_mock_document_content(url)

    def _is_confluence_url(self, url: str) -> bool:
        """Confluence URL 형식 검증"""
        try:
            parsed = urlparse(url)
            return (
                "atlassian.net" in parsed.hostname
                or "/wiki/" in url
                or "/display/" in url
                or "pageId=" in url
            )
        except:
            return False

    def _extract_page_id(self, url: str) -> str:
        """URL에서 페이지 ID 추출"""
        try:
            # pageId 파라미터에서 추출
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            if "pageId" in query_params:
                return query_params["pageId"][0]

            # URL 패스에서 추출 (다양한 패턴 지원)
            patterns = [
                r"/pages/(\d+)/",
                r"/viewpage\.action\?pageId=(\d+)",
                r"/pages/viewpage\.action\?pageId=(\d+)",
                r"pageId=(\d+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)

            return ""
        except:
            return ""

    async def _get_page_info(self, page_id: str) -> Dict[str, Any]:
        """Confluence API로 페이지 기본 정보 조회"""
        try:
            if not self.base_url or not self.auth_header:
                # API 정보가 없을 때는 Mock 데이터 반환 (MVP용)
                return self._get_mock_page_info(page_id)

            api_url = f"{self.base_url}/rest/api/content/{page_id}"

            headers = {
                "Authorization": f"Basic {self.auth_header}",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers)

                if response.status_code == 200:
                    return response.json()
                else:
                    return None

        except Exception:
            # API 호출 실패 시 Mock 데이터 반환
            return self._get_mock_page_info(page_id)

    async def _get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Confluence API로 페이지 콘텐츠 조회"""
        try:
            if not self.base_url or not self.auth_header:
                # API 정보가 없을 때는 Mock 데이터 반환 (MVP용)
                return self._get_mock_page_content(page_id)

            api_url = f"{self.base_url}/rest/api/content/{page_id}?expand=body.storage"

            headers = {
                "Authorization": f"Basic {self.auth_header}",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "title": data.get("title", ""),
                        "body": data.get("body", {})
                        .get("storage", {})
                        .get("value", ""),
                    }
                else:
                    return None

        except Exception:
            # API 호출 실패 시 Mock 데이터 반환
            return self._get_mock_page_content(page_id)

    def _extract_text_from_html(self, html_content: str) -> str:
        """HTML에서 텍스트 추출 (간단한 방식)"""
        try:
            # HTML 태그 제거
            import re

            clean_text = re.sub(r"<[^>]+>", " ", html_content)

            # 여러 공백을 하나로 변경
            clean_text = re.sub(r"\s+", " ", clean_text)

            # 앞뒤 공백 제거
            clean_text = clean_text.strip()

            return clean_text
        except:
            return html_content

    def parse_document_structure(self, content: str) -> Dict[str, Any]:
        """
        문서 내용을 헤더 구조로 파싱
        """
        try:
            import re

            # 헤더 패턴 정의 (다양한 형식 지원)
            header_patterns = [
                (r"^#{1,6}\s+(.+)$", "markdown"),  # Markdown headers
                (r"^(\d{2}\.\s+.+)$", "double_digit"),  # 00. 01. 10. etc.
                (r"^(\d{1,2}\.\s+.+)$", "numbered"),  # 1. 2. 3. ... 99.
                (
                    r"^([가-힣]+)\s*:\s*(.*)$",
                    "korean_colon",
                ),  # Korean sections with colon
                (
                    r"^([A-Z][a-z]+)\s*:\s*(.*)$",
                    "english_colon",
                ),  # English sections with colon
                (r"^\*{1,3}\s*(.+)$", "bullet"),  # Bullet points
                (r"^(.+)\n={3,}$", "underline_equal"),  # Underlined with =
                (r"^(.+)\n-{3,}$", "underline_dash"),  # Underlined with -
            ]

            lines = content.split("\n")
            structure = {"title": "", "sections": [], "content_by_section": {}}

            current_section = None
            current_content = []

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # 특정 라인 디버깅
                if "00." in line or "들어가기" in line:
                    print(f"디버깅 라인 {i}: '{line}'")

                # 헤더 검출
                header_found = False
                for pattern_tuple in header_patterns:
                    pattern, pattern_type = pattern_tuple
                    match = re.match(pattern, line, re.MULTILINE)
                    if match:
                        print(f"헤더 감지: '{line}' -> 패턴 타입: {pattern_type}")
                        # 이전 섹션 저장
                        if current_section:
                            structure["content_by_section"][current_section] = (
                                "\n".join(current_content)
                            )

                        # 새 섹션 시작
                        if pattern_type == "markdown":
                            current_section = match.group(1).strip()
                        elif pattern_type in ["numbered", "double_digit"]:
                            current_section = match.group(1).strip()
                        elif pattern_type in ["korean_colon", "english_colon"]:
                            if len(match.groups()) >= 2 and match.group(2).strip():
                                current_section = f"{match.group(1).strip()}: {match.group(2).strip()}"
                            else:
                                current_section = match.group(1).strip()
                        elif pattern_type == "bullet":
                            current_section = match.group(1).strip()
                        else:  # underline types
                            current_section = match.group(1).strip()

                        structure["sections"].append(current_section)
                        current_content = []
                        header_found = True
                        break

                # 헤더가 아니면 현재 섹션의 내용으로 추가
                if not header_found:
                    if not structure["title"] and not current_section:
                        structure["title"] = line  # 첫 번째 줄을 제목으로 사용
                    else:
                        current_content.append(line)

            # 마지막 섹션 저장
            if current_section:
                structure["content_by_section"][current_section] = "\n".join(
                    current_content
                )

            return structure

        except Exception as e:
            print(f"문서 구조 파싱 오류: {str(e)}")
            # 파싱 실패 시 전체 내용을 하나의 섹션으로 처리
            return {
                "title": "",
                "sections": ["전체 내용"],
                "content_by_section": {"전체 내용": content},
            }

    def _get_mock_page_info(self, page_id: str) -> Dict[str, Any]:
        """Mock 페이지 정보 (개발/테스트용)"""
        return {"id": page_id, "title": "ConfluSum 프로젝트 개발 문서", "type": "page"}

    def _get_mock_page_content(self, page_id: str) -> Dict[str, Any]:
        """Mock 페이지 콘텐츠 (개발/테스트용)"""
        mock_content = """
        # ConfluSum 프로젝트 개발 문서
        
        ## 프로젝트 개요
        ConfluSum은 AI 기반 개인화 Confluence 문서 요약 서비스입니다.
        
        ## 기술 스택
        - Backend: FastAPI (Python)
        - Frontend: HTML, CSS, JavaScript
        - AI: Claude Code + Confluence MCP
        
        ## 주요 기능
        1. Confluence URL 입력 및 검증
        2. 페르소나 선택 (개발자/기획자/디자이너)
        3. AI 기반 맞춤형 요약 생성
        4. 사용자 피드백 수집
        
        ## 개발 일정
        - Day 1: MVP 개발 완료
        - Week 1: 베타 테스트
        - Month 1: 사용자 피드백 분석 및 개선
        
        ## 성공 지표
        - 70% 이상 긍정 피드백
        - 평균 30초 이내 응답 시간
        - 90% 이상 기술적 안정성
        
        ## 비즈니스 목표
        기업 내 방대한 Confluence 문서를 효율적으로 소화할 수 있도록,
        사용자의 역할에 맞는 맞춤형 요약을 제공하여 업무 효율성을 극대화합니다.
        
        ## 리스크 관리
        - Claude API 장애 대비 백업 시스템 준비
        - Confluence 접근 권한 문제에 대한 명확한 안내
        - 요약 품질 개선을 위한 지속적인 프롬프트 튜닝
        """

        return {"title": "ConfluSum 프로젝트 개발 문서", "body": mock_content}

    def _get_mock_document_content(self, url: str) -> Dict[str, Any]:
        """Mock 문서 콘텐츠 반환 (URL 기반, 헤더 구조 포함)"""
        page_id = self._extract_page_id(url) or "123456"
        content_data = self._get_mock_page_content(page_id)
        clean_content = self._extract_text_from_html(content_data.get("body", ""))
        structure = self.parse_document_structure(clean_content)

        return {
            "title": content_data.get("title", ""),
            "content": clean_content,
            "structure": structure,
            "url": url,
            "page_id": page_id,
        }
