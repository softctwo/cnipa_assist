"""
AI服务API
"""
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.ai_service import ai_service

router = APIRouter()

class AIAnalysisRequest(BaseModel):
    """AI分析请求模型"""
    text: str
    analysis_type: str = "comprehensive"

class OpinionGenerationRequest(BaseModel):
    """审查意见生成请求模型"""
    analysis_result: str
    opinion_type: str = "notice"

@router.get("/status")
async def get_ai_status():
    """
    获取AI服务状态
    """
    try:
        availability = ai_service.check_model_availability()
        
        return {
            "success": True,
            "data": {
                "service_status": "available" if availability["ollama_service"] else "unavailable",
                "model_availability": availability,
                "default_model": ai_service.default_model,
                "backup_model": ai_service.backup_model,
                "recommendations": _get_status_recommendations(availability)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取AI状态失败: {str(e)}",
            "data": {
                "service_status": "error",
                "error": str(e)
            }
        }

@router.post("/analyze")
async def analyze_text(request: AIAnalysisRequest):
    """
    AI文本分析
    """
    try:
        # 验证分析类型
        valid_types = ["comprehensive", "novelty", "inventiveness", "utility"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"无效的分析类型。支持的类型: {', '.join(valid_types)}"
            )
        
        # 执行AI分析
        ai_response = ai_service.analyze_patent_document(
            request.text,
            request.analysis_type
        )
        
        return {
            "success": ai_response.success,
            "message": "AI分析完成" if ai_response.success else "AI分析失败",
            "data": {
                "analysis_result": ai_response.content,
                "confidence": ai_response.confidence,
                "processing_time": ai_response.processing_time,
                "model_used": ai_response.model_used,
                "analysis_type": request.analysis_type
            },
            "error_message": ai_response.error_message
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI分析失败: {str(e)}"
        )

@router.post("/generate-opinion")
async def generate_opinion(request: OpinionGenerationRequest):
    """
    生成审查意见
    """
    try:
        # 验证意见类型
        valid_types = ["notice", "grant", "rejection"]
        if request.opinion_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"无效的意见类型。支持的类型: {', '.join(valid_types)}"
            )
        
        # 生成审查意见
        ai_response = ai_service.generate_examination_opinion(
            request.analysis_result,
            request.opinion_type
        )
        
        return {
            "success": ai_response.success,
            "message": "审查意见生成完成" if ai_response.success else "审查意见生成失败",
            "data": {
                "opinion_content": ai_response.content,
                "confidence": ai_response.confidence,
                "processing_time": ai_response.processing_time,
                "model_used": ai_response.model_used,
                "opinion_type": request.opinion_type
            },
            "error_message": ai_response.error_message
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"审查意见生成失败: {str(e)}"
        )

@router.post("/test-connection")
async def test_ai_connection():
    """
    测试AI连接
    """
    try:
        # 使用简单文本测试连接
        test_text = "这是一个测试文本，用于验证AI服务连接。"
        
        ai_response = ai_service.analyze_patent_document(
            test_text,
            "comprehensive"
        )
        
        return {
            "success": ai_response.success,
            "message": "AI连接测试完成",
            "data": {
                "connection_status": "connected" if ai_response.success else "failed",
                "response_time": ai_response.processing_time,
                "model_used": ai_response.model_used,
                "test_response": ai_response.content[:200] if ai_response.content else None  # 只返回前200字符
            },
            "error_message": ai_response.error_message
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"AI连接测试失败: {str(e)}",
            "data": {
                "connection_status": "error",
                "error": str(e)
            }
        }

def _get_status_recommendations(availability: Dict[str, bool]) -> Dict[str, str]:
    """获取状态建议"""
    recommendations = {}
    
    if not availability["ollama_service"]:
        recommendations["ollama_service"] = "请启动Ollama服务: ollama serve"
    else:
        recommendations["ollama_service"] = "Ollama服务运行正常"
    
    if not availability["primary_model"]:
        recommendations["primary_model"] = f"请下载主要模型: ollama pull {ai_service.default_model}"
    else:
        recommendations["primary_model"] = "主要模型可用"
    
    if not availability["backup_model"]:
        recommendations["backup_model"] = f"建议下载备用模型: ollama pull {ai_service.backup_model}"
    else:
        recommendations["backup_model"] = "备用模型可用"
    
    return recommendations