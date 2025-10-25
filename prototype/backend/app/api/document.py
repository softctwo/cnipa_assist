"""
文档处理API
"""
import os
import json
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db, PatentApplication
from ..services.document_parser import document_parser, PatentDocument

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传并解析专利文档
    """
    # 检查文件格式
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_extension}。支持的格式: {', '.join(allowed_extensions)}"
        )
    
    # 检查文件大小 (50MB限制)
    max_size = 50 * 1024 * 1024  # 50MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持50MB"
        )
    
    try:
        # 保存文件
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 解析文档
        patent_doc, metadata = document_parser.parse_document(str(file_path))
        
        # 验证文档
        validation_result = document_parser.validate_document(patent_doc)
        
        # 保存到数据库
        db_application = PatentApplication(
            application_number=patent_doc.application_number or "未识别",
            application_date=patent_doc.application_date or "未识别",
            title=patent_doc.title or "未识别",
            applicant=patent_doc.applicant or "未识别",
            inventor=patent_doc.inventor,
            file_path=str(file_path)
        )
        
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        return {
            "success": True,
            "message": "文档上传和解析成功",
            "data": {
                "application_id": db_application.id,
                "patent_info": {
                    "application_number": patent_doc.application_number,
                    "application_date": patent_doc.application_date,
                    "title": patent_doc.title,
                    "applicant": patent_doc.applicant,
                    "inventor": patent_doc.inventor,
                    "technical_field": patent_doc.technical_field,
                    "claims_count": len(patent_doc.claims) if patent_doc.claims else 0,
                    "has_abstract": bool(patent_doc.abstract)
                },
                "metadata": metadata,
                "validation": validation_result
            }
        }
        
    except Exception as e:
        # 清理上传的文件
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"文档处理失败: {str(e)}"
        )

@router.get("/list")
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取文档列表
    """
    applications = db.query(PatentApplication).offset(skip).limit(limit).all()
    total = db.query(PatentApplication).count()
    
    return {
        "success": True,
        "data": {
            "applications": [
                {
                    "id": app.id,
                    "application_number": app.application_number,
                    "title": app.title,
                    "applicant": app.applicant,
                    "status": app.status,
                    "created_at": app.created_at.isoformat() if app.created_at else None
                }
                for app in applications
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    }

@router.get("/{application_id}")
async def get_document_detail(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    获取文档详细信息
    """
    application = db.query(PatentApplication).filter(
        PatentApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    try:
        # 重新解析文档获取完整信息
        if application.file_path and Path(application.file_path).exists():
            patent_doc, metadata = document_parser.parse_document(application.file_path)
            
            return {
                "success": True,
                "data": {
                    "application_info": {
                        "id": application.id,
                        "application_number": application.application_number,
                        "application_date": application.application_date,
                        "title": application.title,
                        "applicant": application.applicant,
                        "inventor": application.inventor,
                        "status": application.status,
                        "created_at": application.created_at.isoformat() if application.created_at else None
                    },
                    "patent_content": {
                        "technical_field": patent_doc.technical_field,
                        "background_art": patent_doc.background_art,
                        "invention_content": patent_doc.invention_content,
                        "claims": patent_doc.claims,
                        "description": patent_doc.description,
                        "abstract": patent_doc.abstract
                    },
                    "metadata": metadata
                }
            }
        else:
            raise HTTPException(status_code=404, detail="原始文件不存在")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文档详情失败: {str(e)}"
        )

@router.delete("/{application_id}")
async def delete_document(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    删除文档
    """
    application = db.query(PatentApplication).filter(
        PatentApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    try:
        # 删除文件
        if application.file_path and Path(application.file_path).exists():
            Path(application.file_path).unlink()
        
        # 删除数据库记录
        db.delete(application)
        db.commit()
        
        return {
            "success": True,
            "message": "文档删除成功"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除文档失败: {str(e)}"
        )