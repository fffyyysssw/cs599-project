from fastapi import APIRouter

from app.ai.workflow import analyze_text
from app.schemas.ai import AnalyzeRequest
from app.schemas.common import success_response


router = APIRouter(prefix="/ai", tags=["AI 分析"])


@router.post("/analyze")
async def analyze(payload: AnalyzeRequest):
    result = analyze_text(payload.text)
    return success_response(result, message="分析成功")
