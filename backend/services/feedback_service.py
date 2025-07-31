"""
피드백 서비스
사용자 피드백 수집 및 통계 관리
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import uuid

class FeedbackService:
    def __init__(self):
        self.feedback_file = "feedback_data.json"
        self.feedback_data = self._load_feedback_data()

    def _load_feedback_data(self) -> List[Dict[str, Any]]:
        """저장된 피드백 데이터 로드"""
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _save_feedback_data(self) -> None:
        """피드백 데이터 저장"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"피드백 저장 오류: {e}")

    async def save_feedback(self, url: str, persona: str, feedback: str) -> str:
        """
        피드백 저장
        """
        try:
            feedback_id = str(uuid.uuid4())
            
            feedback_entry = {
                "id": feedback_id,
                "url": url,
                "persona": persona,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.feedback_data.append(feedback_entry)
            self._save_feedback_data()
            
            return feedback_id
            
        except Exception as e:
            raise Exception(f"피드백 저장 실패: {str(e)}")

    async def get_stats(self) -> Dict[str, Any]:
        """
        피드백 통계 조회
        """
        try:
            total_feedback = len(self.feedback_data)
            
            if total_feedback == 0:
                return {
                    "total_feedback": 0,
                    "positive_rate": 0,
                    "negative_rate": 0,
                    "persona_stats": {},
                    "recent_feedback": []
                }
            
            # 긍정/부정 피드백 수 계산
            positive_count = sum(1 for f in self.feedback_data if f.get("feedback") == "positive")
            negative_count = sum(1 for f in self.feedback_data if f.get("feedback") == "negative")
            
            positive_rate = (positive_count / total_feedback) * 100
            negative_rate = (negative_count / total_feedback) * 100
            
            # 페르소나별 통계
            persona_stats = {}
            for feedback in self.feedback_data:
                persona = feedback.get("persona", "unknown")
                if persona not in persona_stats:
                    persona_stats[persona] = {"positive": 0, "negative": 0, "total": 0}
                
                persona_stats[persona]["total"] += 1
                if feedback.get("feedback") == "positive":
                    persona_stats[persona]["positive"] += 1
                elif feedback.get("feedback") == "negative":
                    persona_stats[persona]["negative"] += 1
            
            # 페르소나별 긍정률 계산
            for persona in persona_stats:
                total = persona_stats[persona]["total"]
                positive = persona_stats[persona]["positive"]
                persona_stats[persona]["positive_rate"] = (positive / total * 100) if total > 0 else 0
            
            # 최근 피드백 (최대 10개)
            recent_feedback = sorted(
                self.feedback_data,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )[:10]
            
            return {
                "total_feedback": total_feedback,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "positive_rate": round(positive_rate, 1),
                "negative_rate": round(negative_rate, 1),
                "persona_stats": persona_stats,
                "recent_feedback": recent_feedback,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"통계 조회 실패: {str(e)}")

    async def get_feedback_by_persona(self, persona: str) -> List[Dict[str, Any]]:
        """특정 페르소나의 피드백 조회"""
        try:
            return [f for f in self.feedback_data if f.get("persona") == persona]
        except Exception as e:
            raise Exception(f"페르소나별 피드백 조회 실패: {str(e)}")

    async def get_recent_feedback(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 피드백 조회"""
        try:
            return sorted(
                self.feedback_data,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )[:limit]
        except Exception as e:
            raise Exception(f"최근 피드백 조회 실패: {str(e)}")

    def get_success_rate(self) -> float:
        """성공률 (긍정 피드백 비율) 계산"""
        try:
            if not self.feedback_data:
                return 0.0
            
            positive_count = sum(1 for f in self.feedback_data if f.get("feedback") == "positive")
            return (positive_count / len(self.feedback_data)) * 100
        except Exception:
            return 0.0

    def is_success_criteria_met(self) -> bool:
        """성공 기준 달성 여부 (70% 이상 긍정 피드백)"""
        return self.get_success_rate() >= 70.0