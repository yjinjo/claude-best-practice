"""
Pydantic 모델 정의
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal

class URLValidationRequest(BaseModel):
    """URL 검증 요청 모델"""
    url: str

class URLValidationResponse(BaseModel):
    """URL 검증 응답 모델"""
    valid: bool
    title: Optional[str] = None
    message: Optional[str] = None

class SummarizationRequest(BaseModel):
    """요약 생성 요청 모델"""
    url: str
    persona: Literal["developer", "product_manager", "designer"]

class SummarizationResponse(BaseModel):
    """요약 생성 응답 모델"""
    summary: str
    title: str
    url: str
    persona: str

class FeedbackRequest(BaseModel):
    """피드백 요청 모델"""
    url: str
    persona: str
    feedback: Literal["positive", "negative"]

class DocumentContent(BaseModel):
    """문서 콘텐츠 모델"""
    title: str
    content: str
    url: str
    page_id: Optional[str] = None

class PersonaPrompt(BaseModel):
    """페르소나 프롬프트 모델"""
    persona: str
    description: str
    prompt_template: str
    focus_areas: list[str]