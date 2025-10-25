"""
API路由模块
"""
from fastapi import APIRouter
from .document import router as document_router
from .examination import router as examination_router
from .ai import router as ai_router

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(document_router, prefix="/documents", tags=["documents"])
router.include_router(examination_router, prefix="/examination", tags=["examination"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])