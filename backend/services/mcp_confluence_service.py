"""
MCP Atlassian을 활용한 Confluence 서비스
"""

import subprocess
import json
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse

class MCPConfluenceService:
    def __init__(self):
        self.mcp_command = ["mcp", "run", "mcp-atlassian"]
    
    async def get_document_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        실제 Confluence API를 직접 호출해서 문서 내용 가져오기
        환경변수 기반 직접 호출 방식
        """
        try:
            import os
            import httpx
            import base64
            
            # 환경변수에서 인증 정보 가져오기
            confluence_url = os.getenv("CONFLUENCE_BASE_URL", "")
            username = os.getenv("CONFLUENCE_USERNAME", "")
            api_token = os.getenv("CONFLUENCE_API_TOKEN", "")
            
            if not all([confluence_url, username, api_token]):
                print(f"Confluence 인증 정보가 설정되지 않았습니다.")
                print(f"confluence_url: {'설정됨' if confluence_url else '없음'}")
                print(f"username: {'설정됨' if username else '없음'}")
                print(f"api_token: {'설정됨' if api_token else '없음'}")
                return None
            
            page_id = self._extract_page_id_from_url(url)
            print(f"추출된 페이지 ID: {page_id} (URL: {url})")
            
            if not page_id:
                print(f"URL에서 페이지 ID를 추출할 수 없습니다: {url}")
                return None

            # API URL 구성
            api_url = f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage"
            print(f"API 호출 URL: {api_url}")
            
            # Basic Auth 헤더 생성
            auth_string = f"{username}:{api_token}"
            auth_header = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_header}",
                "Accept": "application/json"
            }
            
            print("Confluence API 호출 시작...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url, headers=headers)
                
                print(f"API 응답 상태: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"API 응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    result = self._process_confluence_response(data)
                    print(f"처리된 결과 - 제목: {result.get('title', '없음')[:50]}..., 내용 길이: {len(result.get('content', ''))}")
                    return result
                elif response.status_code == 401:
                    print(f"Confluence API 인증 실패: {response.status_code} - 인증 정보를 확인해주세요")
                elif response.status_code == 404:
                    print(f"Confluence 페이지를 찾을 수 없습니다: {response.status_code} - 페이지 ID나 권한을 확인해주세요")
                else:
                    print(f"Confluence API 호출 실패: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"Confluence API 호출 오류: {str(e)}")
            return None
    
    def _extract_page_id_from_url(self, url: str) -> Optional[str]:
        """URL에서 Confluence 페이지 ID 추출"""
        try:
            # 패턴 1: /pages/123456/
            match = re.search(r'/pages/(\d+)/', url)
            if match:
                return match.group(1)
            
            # 패턴 2: pageId=123456
            match = re.search(r'pageId=(\d+)', url)
            if match:
                return match.group(1)
            
            # 패턴 3: URL의 마지막 숫자 부분
            match = re.search(r'/(\d+)(?:/|$)', url)
            if match:
                return match.group(1)
                
            return None
            
        except Exception:
            return None
    
    def _process_confluence_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Confluence API 응답 데이터 처리"""
        try:
            title = data.get("title", "")
            
            # 본문 내용 추출
            content = ""
            if "body" in data and "storage" in data["body"]:
                content = data["body"]["storage"].get("value", "")
            
            # HTML 태그 제거 및 텍스트 정리
            clean_content = self._clean_html_content(content)
            
            return {
                "title": title,
                "content": clean_content,
                "raw_data": data
            }
            
        except Exception as e:
            print(f"Confluence 응답 처리 오류: {str(e)}")
            return {"title": "", "content": "", "raw_data": data}
    
    def _process_mcp_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 응답 데이터 처리"""
        try:
            content = ""
            title = ""
            
            if isinstance(data, dict):
                # 메타데이터에서 제목 추출
                if "metadata" in data:
                    title = data["metadata"].get("title", "")
                
                # 콘텐츠 추출
                if "metadata" in data and "content" in data["metadata"]:
                    content_data = data["metadata"]["content"]
                    if isinstance(content_data, dict) and "value" in content_data:
                        content = content_data["value"]
                    elif isinstance(content_data, str):
                        content = content_data
                elif "content" in data:
                    if isinstance(data["content"], dict) and "value" in data["content"]:
                        content = data["content"]["value"]
                    elif isinstance(data["content"], str):
                        content = data["content"]
            
            # HTML 태그 제거 및 텍스트 정리
            clean_content = self._clean_html_content(content)
            
            return {
                "title": title,
                "content": clean_content,
                "raw_data": data
            }
            
        except Exception as e:
            print(f"MCP 응답 처리 오류: {str(e)}")
            return {"title": "", "content": "", "raw_data": data}
    
    def _clean_html_content(self, html_content: str) -> str:
        """HTML 콘텐츠에서 텍스트 추출 및 정리"""
        try:
            # HTML 태그 제거
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # 특수 HTML 엔티티 변환
            replacements = {
                '&nbsp;': ' ',
                '&amp;': '&',
                '&lt;': '<',
                '&gt;': '>',
                '&quot;': '"',
                '&#39;': "'",
            }
            
            for entity, char in replacements.items():
                clean_text = clean_text.replace(entity, char)
            
            # 여러 공백을 하나로 변경
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # 앞뒤 공백 제거
            clean_text = clean_text.strip()
            
            return clean_text
            
        except Exception:
            return html_content