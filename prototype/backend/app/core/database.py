"""
数据库配置和初始化
"""
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent.parent / "data" / "patent_examination.db"
DB_PATH.parent.mkdir(exist_ok=True)

# SQLAlchemy配置
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 数据模型定义
class PatentApplication(Base):
    """专利申请表"""
    __tablename__ = "patent_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(50), unique=True, index=True)
    application_date = Column(String(20))
    title = Column(String(500))
    applicant = Column(String(500))
    inventor = Column(String(500))
    status = Column(String(50), default="pending")
    file_path = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExaminationRecord(Base):
    """审查记录表"""
    __tablename__ = "examination_records"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("patent_applications.id"))
    examination_type = Column(String(50))  # 'formal', 'substantive'
    examination_step = Column(String(100))
    status = Column(String(50), default="pending")
    result = Column(Text)  # JSON格式存储结果
    confidence_score = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class ExaminationRule(Base):
    """审查规则表"""
    __tablename__ = "examination_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(200))
    rule_type = Column(String(50))  # 'formal', 'novelty', 'inventiveness'
    rule_content = Column(Text)  # JSON格式存储规则内容
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    
    # 插入默认规则
    db = SessionLocal()
    try:
        # 检查是否已有规则
        existing_rules = db.query(ExaminationRule).count()
        if existing_rules == 0:
            default_rules = [
                ExaminationRule(
                    rule_name="文档完整性检查",
                    rule_type="formal",
                    rule_content='{"check_items": ["请求书", "权利要求书", "说明书", "附图"]}',
                    priority=1
                ),
                ExaminationRule(
                    rule_name="保护客体判断",
                    rule_type="substantive",
                    rule_content='{"criteria": ["产品形状", "产品构造", "形状构造结合"]}',
                    priority=2
                ),
                ExaminationRule(
                    rule_name="新颖性检查",
                    rule_type="novelty",
                    rule_content='{"search_databases": ["CNABS", "CNPAT"], "time_limit": "申请日之前"}',
                    priority=3
                )
            ]
            for rule in default_rules:
                db.add(rule)
            db.commit()
            print("默认审查规则已插入")
    finally:
        db.close()

def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()