"""
审查功能API
"""
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db, PatentApplication, ExaminationRecord
from ..services.document_parser import document_parser
from ..services.rule_engine import rule_engine, RuleType
from ..services.ai_service import ai_service

router = APIRouter()

class ExaminationRequest(BaseModel):
    """审查请求模型"""
    application_id: int
    examination_type: str = "formal"  # formal, substantive, comprehensive
    rule_types: Optional[List[str]] = None

@router.post("/start")
async def start_examination(
    request: ExaminationRequest,
    db: Session = Depends(get_db)
):
    """
    开始审查
    """
    # 获取专利申请
    application = db.query(PatentApplication).filter(
        PatentApplication.id == request.application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="专利申请不存在")
    
    try:
        # 解析文档获取完整数据
        if not application.file_path:
            raise HTTPException(status_code=400, detail="文档文件不存在")
        
        patent_doc, metadata = document_parser.parse_document(application.file_path)
        
        # 准备审查数据
        patent_data = {
            "application_number": patent_doc.application_number,
            "title": patent_doc.title,
            "applicant": patent_doc.applicant,
            "inventor": patent_doc.inventor,
            "technical_field": patent_doc.technical_field,
            "background_art": patent_doc.background_art,
            "invention_content": patent_doc.invention_content,
            "claims": patent_doc.claims,
            "description": patent_doc.description,
            "abstract": patent_doc.abstract
        }
        
        # 确定要执行的规则类型
        rule_types_to_execute = None
        if request.rule_types:
            rule_types_to_execute = [RuleType(rt) for rt in request.rule_types]
        elif request.examination_type == "formal":
            rule_types_to_execute = [RuleType.FORMAL]
        elif request.examination_type == "substantive":
            rule_types_to_execute = [RuleType.NOVELTY, RuleType.INVENTIVENESS, RuleType.UTILITY]
        # comprehensive 执行所有规则
        
        # 执行规则检查
        rule_results = rule_engine.execute_rules(patent_data, rule_types_to_execute)
        rule_summary = rule_engine.get_summary(rule_results)
        
        # 创建审查记录
        examination_record = ExaminationRecord(
            application_id=request.application_id,
            examination_type=request.examination_type,
            examination_step="rule_based_check",
            status="completed",
            result=json.dumps({
                "rule_results": [
                    {
                        "rule_name": r.rule_name,
                        "rule_type": r.rule_type.value,
                        "result": r.result.value,
                        "confidence": r.confidence,
                        "message": r.message,
                        "details": r.details,
                        "execution_time": r.execution_time
                    }
                    for r in rule_results
                ],
                "summary": rule_summary
            }, ensure_ascii=False),
            confidence_score=str(rule_summary["overall_confidence"])
        )
        
        db.add(examination_record)
        db.commit()
        db.refresh(examination_record)
        
        return {
            "success": True,
            "message": "审查完成",
            "data": {
                "examination_id": examination_record.id,
                "examination_type": request.examination_type,
                "rule_results": [
                    {
                        "rule_name": r.rule_name,
                        "rule_type": r.rule_type.value,
                        "result": r.result.value,
                        "confidence": r.confidence,
                        "message": r.message,
                        "execution_time": r.execution_time
                    }
                    for r in rule_results
                ],
                "summary": rule_summary
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"审查执行失败: {str(e)}"
        )

@router.post("/ai-analysis")
async def ai_analysis(
    request: ExaminationRequest,
    db: Session = Depends(get_db)
):
    """
    AI智能分析
    """
    # 获取专利申请
    application = db.query(PatentApplication).filter(
        PatentApplication.id == request.application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="专利申请不存在")
    
    try:
        # 检查AI服务可用性
        availability = ai_service.check_model_availability()
        
        # 解析文档
        patent_doc, metadata = document_parser.parse_document(application.file_path)
        
        # 准备分析文本
        analysis_text = ""
        if patent_doc.title:
            analysis_text += f"发明名称: {patent_doc.title}\n"
        if patent_doc.technical_field:
            analysis_text += f"技术领域: {patent_doc.technical_field}\n"
        if patent_doc.invention_content:
            analysis_text += f"发明内容: {patent_doc.invention_content}\n"
        if patent_doc.claims:
            analysis_text += f"权利要求: {' '.join(patent_doc.claims[:3])}\n"  # 只取前3项
        
        # 执行AI分析
        ai_response = ai_service.analyze_patent_document(
            analysis_text, 
            request.examination_type
        )
        
        # 创建审查记录
        examination_record = ExaminationRecord(
            application_id=request.application_id,
            examination_type=f"ai_{request.examination_type}",
            examination_step="ai_analysis",
            status="completed" if ai_response.success else "failed",
            result=json.dumps({
                "ai_analysis": {
                    "success": ai_response.success,
                    "content": ai_response.content,
                    "confidence": ai_response.confidence,
                    "processing_time": ai_response.processing_time,
                    "model_used": ai_response.model_used,
                    "error_message": ai_response.error_message
                },
                "model_availability": availability
            }, ensure_ascii=False),
            confidence_score=str(ai_response.confidence)
        )
        
        db.add(examination_record)
        db.commit()
        db.refresh(examination_record)
        
        return {
            "success": ai_response.success,
            "message": "AI分析完成" if ai_response.success else "AI分析失败",
            "data": {
                "examination_id": examination_record.id,
                "ai_analysis": {
                    "content": ai_response.content,
                    "confidence": ai_response.confidence,
                    "processing_time": ai_response.processing_time,
                    "model_used": ai_response.model_used
                },
                "model_availability": availability,
                "error_message": ai_response.error_message
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI分析失败: {str(e)}"
        )

@router.get("/history/{application_id}")
async def get_examination_history(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    获取审查历史
    """
    records = db.query(ExaminationRecord).filter(
        ExaminationRecord.application_id == application_id
    ).order_by(ExaminationRecord.created_at.desc()).all()
    
    return {
        "success": True,
        "data": {
            "application_id": application_id,
            "examination_history": [
                {
                    "id": record.id,
                    "examination_type": record.examination_type,
                    "examination_step": record.examination_step,
                    "status": record.status,
                    "confidence_score": record.confidence_score,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                    "result_summary": json.loads(record.result) if record.result else None
                }
                for record in records
            ]
        }
    }

@router.get("/rules")
async def get_examination_rules():
    """
    获取审查规则列表
    """
    return {
        "success": True,
        "data": {
            "rules": [
                {
                    "name": rule.name,
                    "type": rule.rule_type.value,
                    "priority": rule.priority,
                    "is_active": rule.is_active
                }
                for rule in rule_engine.rules
            ],
            "rule_types": [rt.value for rt in RuleType]
        }
    }

@router.get("/ai/status")
async def get_ai_status():
    """
    获取AI服务状态
    """
    availability = ai_service.check_model_availability()
    
    return {
        "success": True,
        "data": {
            "ai_service_status": availability,
            "recommendations": {
                "ollama_service": "请确保Ollama服务正在运行" if not availability["ollama_service"] else "服务正常",
                "primary_model": "请下载主要模型" if not availability["primary_model"] else "模型可用",
                "backup_model": "建议下载备用模型" if not availability["backup_model"] else "备用模型可用"
            }
        }
    }