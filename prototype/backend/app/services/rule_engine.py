"""
规则引擎服务
"""
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class RuleType(Enum):
    """规则类型"""
    FORMAL = "formal"           # 形式审查
    NOVELTY = "novelty"         # 新颖性
    INVENTIVENESS = "inventiveness"  # 创造性
    UTILITY = "utility"         # 实用性
    SUBJECT_MATTER = "subject_matter"  # 保护客体

class RuleResult(Enum):
    """规则执行结果"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

@dataclass
class RuleExecutionResult:
    """规则执行结果"""
    rule_name: str
    rule_type: RuleType
    result: RuleResult
    confidence: float
    message: str
    details: Dict[str, Any]
    execution_time: float

class ExaminationRule:
    """审查规则基类"""
    
    def __init__(self, name: str, rule_type: RuleType, priority: int = 0):
        self.name = name
        self.rule_type = rule_type
        self.priority = priority
        self.is_active = True
    
    def execute(self, patent_data: Dict[str, Any]) -> RuleExecutionResult:
        """执行规则"""
        raise NotImplementedError("子类必须实现execute方法")

class DocumentCompletenessRule(ExaminationRule):
    """文档完整性检查规则"""
    
    def __init__(self):
        super().__init__("文档完整性检查", RuleType.FORMAL, priority=1)
        self.required_fields = [
            "title",           # 发明名称
            "applicant",       # 申请人
            "claims",          # 权利要求书
            "description"      # 说明书
        ]
        self.recommended_fields = [
            "abstract",        # 摘要
            "technical_field", # 技术领域
            "background_art",  # 背景技术
            "invention_content" # 发明内容
        ]
    
    def execute(self, patent_data: Dict[str, Any]) -> RuleExecutionResult:
        start_time = datetime.now()
        
        missing_required = []
        missing_recommended = []
        
        # 检查必需字段
        for field in self.required_fields:
            if not patent_data.get(field):
                missing_required.append(field)
        
        # 检查推荐字段
        for field in self.recommended_fields:
            if not patent_data.get(field):
                missing_recommended.append(field)
        
        # 判断结果
        if missing_required:
            result = RuleResult.FAIL
            message = f"缺少必需文件: {', '.join(missing_required)}"
            confidence = 0.95
        elif missing_recommended:
            result = RuleResult.WARNING
            message = f"缺少推荐文件: {', '.join(missing_recommended)}"
            confidence = 0.80
        else:
            result = RuleResult.PASS
            message = "文档完整性检查通过"
            confidence = 0.90
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return RuleExecutionResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            result=result,
            confidence=confidence,
            message=message,
            details={
                "missing_required": missing_required,
                "missing_recommended": missing_recommended,
                "total_fields_checked": len(self.required_fields) + len(self.recommended_fields)
            },
            execution_time=execution_time
        )

class SubjectMatterRule(ExaminationRule):
    """保护客体判断规则"""
    
    def __init__(self):
        super().__init__("保护客体判断", RuleType.SUBJECT_MATTER, priority=2)
        
        # 符合实用新型的关键词
        self.positive_keywords = [
            "形状", "构造", "结构", "零件", "部件", "装置", "机构",
            "连接", "固定", "安装", "组合", "配合", "嵌入"
        ]
        
        # 不符合实用新型的关键词
        self.negative_keywords = [
            "方法", "工艺", "步骤", "流程", "算法", "软件", "程序",
            "配方", "组合物", "材料", "成分", "比例", "液体", "气体"
        ]
    
    def execute(self, patent_data: Dict[str, Any]) -> RuleExecutionResult:
        start_time = datetime.now()
        
        # 获取分析文本
        text_to_analyze = ""
        if patent_data.get("title"):
            text_to_analyze += patent_data["title"] + " "
        if patent_data.get("claims"):
            text_to_analyze += " ".join(patent_data["claims"]) + " "
        if patent_data.get("invention_content"):
            text_to_analyze += patent_data["invention_content"]
        
        # 关键词匹配
        positive_matches = []
        negative_matches = []
        
        for keyword in self.positive_keywords:
            if keyword in text_to_analyze:
                positive_matches.append(keyword)
        
        for keyword in self.negative_keywords:
            if keyword in text_to_analyze:
                negative_matches.append(keyword)
        
        # 判断逻辑
        positive_score = len(positive_matches)
        negative_score = len(negative_matches)
        
        if negative_score > positive_score:
            result = RuleResult.FAIL
            message = f"可能不属于实用新型保护客体，发现方法类特征: {', '.join(negative_matches)}"
            confidence = 0.75
        elif positive_score >= 2:
            result = RuleResult.PASS
            message = f"符合实用新型保护客体，涉及产品形状或构造: {', '.join(positive_matches)}"
            confidence = 0.80
        else:
            result = RuleResult.WARNING
            message = "保护客体需要进一步确认"
            confidence = 0.60
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return RuleExecutionResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            result=result,
            confidence=confidence,
            message=message,
            details={
                "positive_matches": positive_matches,
                "negative_matches": negative_matches,
                "positive_score": positive_score,
                "negative_score": negative_score
            },
            execution_time=execution_time
        )

class ClaimsFormatRule(ExaminationRule):
    """权利要求书格式检查规则"""
    
    def __init__(self):
        super().__init__("权利要求书格式检查", RuleType.FORMAL, priority=3)
    
    def execute(self, patent_data: Dict[str, Any]) -> RuleExecutionResult:
        start_time = datetime.now()
        
        claims = patent_data.get("claims", [])
        if not claims:
            return RuleExecutionResult(
                rule_name=self.name,
                rule_type=self.rule_type,
                result=RuleResult.FAIL,
                confidence=0.95,
                message="缺少权利要求书",
                details={"claims_count": 0},
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        
        issues = []
        warnings = []
        
        # 检查独立权利要求
        independent_claims = []
        dependent_claims = []
        
        for i, claim in enumerate(claims):
            claim_text = claim.strip()
            
            # 检查编号格式
            if not re.match(r'^\d+\.', claim_text):
                issues.append(f"权利要求{i+1}缺少正确的编号格式")
            
            # 判断独立/从属权利要求
            if "根据权利要求" in claim_text or "按照权利要求" in claim_text:
                dependent_claims.append(i+1)
            else:
                independent_claims.append(i+1)
            
            # 检查特征部分
            if "其特征在于" not in claim_text and "其特征是" not in claim_text:
                if i == 0:  # 第一项权利要求
                    warnings.append("独立权利要求建议包含'其特征在于'")
        
        # 检查独立权利要求数量
        if len(independent_claims) == 0:
            issues.append("缺少独立权利要求")
        elif len(independent_claims) > 1:
            warnings.append(f"包含{len(independent_claims)}项独立权利要求，需确认单一性")
        
        # 判断结果
        if issues:
            result = RuleResult.FAIL
            message = f"权利要求书格式存在问题: {'; '.join(issues)}"
            confidence = 0.85
        elif warnings:
            result = RuleResult.WARNING
            message = f"权利要求书格式建议改进: {'; '.join(warnings)}"
            confidence = 0.70
        else:
            result = RuleResult.PASS
            message = "权利要求书格式检查通过"
            confidence = 0.80
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return RuleExecutionResult(
            rule_name=self.name,
            rule_type=self.rule_type,
            result=result,
            confidence=confidence,
            message=message,
            details={
                "claims_count": len(claims),
                "independent_claims": independent_claims,
                "dependent_claims": dependent_claims,
                "issues": issues,
                "warnings": warnings
            },
            execution_time=execution_time
        )

class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: List[ExaminationRule] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """初始化默认规则"""
        self.rules = [
            DocumentCompletenessRule(),
            SubjectMatterRule(),
            ClaimsFormatRule()
        ]
        
        # 按优先级排序
        self.rules.sort(key=lambda x: x.priority)
    
    def add_rule(self, rule: ExaminationRule):
        """添加规则"""
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority)
    
    def remove_rule(self, rule_name: str):
        """移除规则"""
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
    
    def execute_rules(self, patent_data: Dict[str, Any], rule_types: Optional[List[RuleType]] = None) -> List[RuleExecutionResult]:
        """
        执行规则
        
        Args:
            patent_data: 专利数据
            rule_types: 要执行的规则类型，None表示执行所有规则
            
        Returns:
            List[RuleExecutionResult]: 规则执行结果列表
        """
        results = []
        
        for rule in self.rules:
            if not rule.is_active:
                continue
                
            if rule_types and rule.rule_type not in rule_types:
                continue
            
            try:
                result = rule.execute(patent_data)
                results.append(result)
            except Exception as e:
                # 规则执行失败
                error_result = RuleExecutionResult(
                    rule_name=rule.name,
                    rule_type=rule.rule_type,
                    result=RuleResult.SKIP,
                    confidence=0.0,
                    message=f"规则执行失败: {str(e)}",
                    details={"error": str(e)},
                    execution_time=0.0
                )
                results.append(error_result)
        
        return results
    
    def get_summary(self, results: List[RuleExecutionResult]) -> Dict[str, Any]:
        """获取执行结果摘要"""
        summary = {
            "total_rules": len(results),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "overall_confidence": 0.0,
            "critical_issues": [],
            "recommendations": []
        }
        
        confidence_sum = 0.0
        confidence_count = 0
        
        for result in results:
            if result.result == RuleResult.PASS:
                summary["passed"] += 1
            elif result.result == RuleResult.FAIL:
                summary["failed"] += 1
                summary["critical_issues"].append(result.message)
            elif result.result == RuleResult.WARNING:
                summary["warnings"] += 1
                summary["recommendations"].append(result.message)
            elif result.result == RuleResult.SKIP:
                summary["skipped"] += 1
            
            if result.confidence > 0:
                confidence_sum += result.confidence
                confidence_count += 1
        
        # 计算平均置信度
        if confidence_count > 0:
            summary["overall_confidence"] = confidence_sum / confidence_count
        
        # 总体建议
        if summary["failed"] > 0:
            summary["overall_recommendation"] = "需要修改后重新审查"
        elif summary["warnings"] > 0:
            summary["overall_recommendation"] = "建议完善相关内容"
        else:
            summary["overall_recommendation"] = "形式审查通过"
        
        return summary

# 创建全局规则引擎实例
rule_engine = RuleEngine()