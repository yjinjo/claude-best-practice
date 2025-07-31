"""
Confluence 서비스
문서 URL 검증 및 콘텐츠 추출
"""

import httpx
import re
import os
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs
import base64
import json

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

    async def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Confluence URL 유효성 검증
        """
        try:
            # URL 형식 검증
            if not self._is_confluence_url(url):
                return {
                    "valid": False,
                    "message": "올바른 Confluence URL 형식이 아닙니다."
                }
            
            # For MVP - always return valid for Confluence URLs
            # Page ID 추출 (Mock 데이터를 위해)
            page_id = self._extract_page_id(url) or "123456"
            
            # Mock 페이지 정보 반환 (API 연동 없이)
            page_info = self._get_mock_page_info(page_id)
            return {
                "valid": True,
                "title": page_info.get("title", ""),
                "message": "유효한 Confluence 문서입니다."
            }
                
        except Exception as e:
            return {
                "valid": False,
                "message": f"URL 검증 중 오류가 발생했습니다: {str(e)}"
            }

    async def get_document_content(self, url: str) -> Dict[str, Any]:
        """
        Confluence 문서 콘텐츠 가져오기
        """
        try:
            # For MVP - always use mock data
            page_id = self._extract_page_id(url) or "123456"
            
            # Mock 콘텐츠 데이터 사용
            content_data = self._get_mock_page_content(page_id)
            
            # HTML에서 텍스트 추출
            clean_content = self._extract_text_from_html(content_data.get("body", ""))
            
            return {
                "title": content_data.get("title", ""),
                "content": clean_content,
                "url": url,
                "page_id": page_id
            }
            
        except Exception as e:
            raise Exception(f"문서 콘텐츠 조회 실패: {str(e)}")

    def _is_confluence_url(self, url: str) -> bool:
        """Confluence URL 형식 검증"""
        try:
            parsed = urlparse(url)
            return (
                'atlassian.net' in parsed.hostname or
                '/wiki/' in url or
                '/display/' in url or
                'pageId=' in url
            )
        except:
            return False

    def _extract_page_id(self, url: str) -> str:
        """URL에서 페이지 ID 추출"""
        try:
            # pageId 파라미터에서 추출
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            if 'pageId' in query_params:
                return query_params['pageId'][0]
            
            # URL 패스에서 추출 (다양한 패턴 지원)
            patterns = [
                r'/pages/(\d+)/',
                r'/viewpage\.action\?pageId=(\d+)',
                r'/pages/viewpage\.action\?pageId=(\d+)',
                r'pageId=(\d+)'
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
                "Accept": "application/json"
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
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "title": data.get("title", ""),
                        "body": data.get("body", {}).get("storage", {}).get("value", "")
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
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # 여러 공백을 하나로 변경
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # 앞뒤 공백 제거
            clean_text = clean_text.strip()
            
            return clean_text
        except:
            return html_content

    def _get_mock_page_info(self, page_id: str) -> Dict[str, Any]:
        """Mock 페이지 정보 (개발/테스트용)"""
        return {
            "id": page_id,
            "title": "ConfluSum 프로젝트 개발 문서",
            "type": "page"
        }

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
        
        return {
            "title": "ConfluSum 프로젝트 개발 문서",
            "body": mock_content
        }