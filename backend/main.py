"""
ConfluSum FastAPI Backend Server
AI 기반 개인화 Confluence 요약 서비스
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from models import URLValidationRequest, SummarizationRequest, FeedbackRequest
from services.confluence_service import ConfluenceService
from services.claude_service import ClaudeService
from services.feedback_service import FeedbackService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ConfluSum API",
    description="AI 기반 개인화 Confluence 문서 요약 서비스",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP - should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
confluence_service = ConfluenceService()
claude_service = ClaudeService()
feedback_service = FeedbackService()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ConfluSum API"}

@app.post("/api/validate-url")
async def validate_url(request: URLValidationRequest):
    """
    Confluence URL 유효성 검증
    """
    try:
        result = await confluence_service.validate_url(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/summarize")
async def summarize_document(request: SummarizationRequest):
    """
    Confluence 문서 AI 요약 생성
    """
    try:
        # 1. Confluence 문서 콘텐츠 가져오기
        document_content = await confluence_service.get_document_content(request.url)
        
        # 2. Claude AI로 페르소나별 요약 생성
        summary = await claude_service.generate_summary(
            content=document_content["content"],
            persona=request.persona,
            title=document_content.get("title", "")
        )
        
        return {
            "summary": summary,
            "title": document_content.get("title", ""),
            "url": request.url,
            "persona": request.persona
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    사용자 피드백 수집
    """
    try:
        result = await feedback_service.save_feedback(
            url=request.url,
            persona=request.persona,
            feedback=request.feedback
        )
        return {"message": "피드백이 저장되었습니다.", "id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """
    기본 통계 정보 (개발용)
    """
    try:
        stats = await feedback_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (React frontend) - AFTER API routes
react_build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "react-app", "build")
if os.path.exists(react_build_path):
    app.mount("/static", StaticFiles(directory=os.path.join(react_build_path, "static")), name="static")
    
# Mount the React app itself - LAST
if os.path.exists(react_build_path):
    app.mount("/", StaticFiles(directory=react_build_path, html=True), name="react-app")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )