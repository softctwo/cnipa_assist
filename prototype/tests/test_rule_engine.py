"""
规则引擎测试
"""
import pytest
from backend.app.services.rule_engine import (
    RuleEngine, 
    DocumentCompletenessRule, 
    SubjectMatterRule, 
    ClaimsFormatRule,
    RuleResult,
    RuleType
)

class TestRuleEngine:
    
    def setup_method(self):
        """测试前准备"""
        self.rule_engine = RuleEngine()
    
    def test_rule_engine_initialization(self):
        """测试规则引擎初始化"""
        assert len(self.rule_engine.rules) > 0
        
        # 检查默认规则
        rule_names = [rule.name for rule in self.rule_engine.rules]
        assert "文档完整性检查" in rule_names
        assert "保护客体判断" in rule_names
        assert "权利要求书格式检查" in rule_names
    
    def test_document_completeness_rule_pass(self):
        """测试文档完整性检查 - 通过"""
        rule = DocumentCompletenessRule()
        
        patent_data = {
            "title": "测试发明",
            "applicant": "测试公司",
            "claims": ["权利要求1", "权利要求2"],
            "description": "详细说明",
            "abstract": "摘要",
            "technical_field": "技术领域",
            "background_art": "背景技术",
            "invention_content": "发明内容"
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.PASS
        assert result.confidence > 0.8
        assert "通过" in result.message
        assert len(result.details["missing_required"]) == 0
        assert len(result.details["missing_recommended"]) == 0
    
    def test_document_completeness_rule_fail(self):
        """测试文档完整性检查 - 失败"""
        rule = DocumentCompletenessRule()
        
        patent_data = {
            "title": "测试发明"
            # 缺少必需字段
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.FAIL
        assert result.confidence > 0.9
        assert "缺少必需文件" in result.message
        assert "applicant" in result.details["missing_required"]
        assert "claims" in result.details["missing_required"]
    
    def test_document_completeness_rule_warning(self):
        """测试文档完整性检查 - 警告"""
        rule = DocumentCompletenessRule()
        
        patent_data = {
            "title": "测试发明",
            "applicant": "测试公司",
            "claims": ["权利要求1"],
            "description": "详细说明"
            # 缺少推荐字段
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.WARNING
        assert "缺少推荐文件" in result.message
        assert "abstract" in result.details["missing_recommended"]
    
    def test_subject_matter_rule_pass(self):
        """测试保护客体判断 - 通过"""
        rule = SubjectMatterRule()
        
        patent_data = {
            "title": "一种新型螺栓结构",
            "claims": ["一种螺栓，包括螺栓头和螺栓杆，其特征在于螺栓头的形状为六边形"],
            "invention_content": "本发明涉及一种具有特殊构造的紧固装置"
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.PASS
        assert "符合实用新型保护客体" in result.message
        assert len(result.details["positive_matches"]) >= 2
    
    def test_subject_matter_rule_fail(self):
        """测试保护客体判断 - 失败"""
        rule = SubjectMatterRule()
        
        patent_data = {
            "title": "一种制造方法",
            "claims": ["一种制造步骤，包括以下工艺流程"],
            "invention_content": "本发明提供一种新的制造工艺和处理方法"
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.FAIL
        assert "不属于实用新型保护客体" in result.message
        assert len(result.details["negative_matches"]) > 0
    
    def test_claims_format_rule_pass(self):
        """测试权利要求书格式检查 - 通过"""
        rule = ClaimsFormatRule()
        
        patent_data = {
            "claims": [
                "1. 一种螺栓，包括螺栓头和螺栓杆，其特征在于：螺栓头为六边形。",
                "2. 根据权利要求1所述的螺栓，其特征在于：螺栓杆表面设有螺纹。"
            ]
        }
        
        result = rule.execute(patent_data)
        
        assert result.result in [RuleResult.PASS, RuleResult.WARNING]
        assert result.details["claims_count"] == 2
        assert 1 in result.details["independent_claims"]
        assert 2 in result.details["dependent_claims"]
    
    def test_claims_format_rule_fail(self):
        """测试权利要求书格式检查 - 失败"""
        rule = ClaimsFormatRule()
        
        patent_data = {
            "claims": []  # 空的权利要求
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.FAIL
        assert "缺少权利要求书" in result.message
        assert result.details["claims_count"] == 0
    
    def test_claims_format_rule_format_issues(self):
        """测试权利要求书格式问题"""
        rule = ClaimsFormatRule()
        
        patent_data = {
            "claims": [
                "一种螺栓，没有编号",  # 缺少编号
                "2 根据权利要求1所述的螺栓"  # 编号格式错误
            ]
        }
        
        result = rule.execute(patent_data)
        
        assert result.result == RuleResult.FAIL
        assert len(result.details["issues"]) > 0
    
    def test_rule_engine_execute_all_rules(self):
        """测试执行所有规则"""
        patent_data = {
            "title": "一种新型螺栓结构",
            "applicant": "测试公司",
            "claims": [
                "1. 一种螺栓，包括螺栓头和螺栓杆，其特征在于：螺栓头为六边形。"
            ],
            "description": "详细说明",
            "invention_content": "本发明涉及紧固件结构改进"
        }
        
        results = self.rule_engine.execute_rules(patent_data)
        
        assert len(results) > 0
        
        # 检查每个结果都有必要的属性
        for result in results:
            assert hasattr(result, 'rule_name')
            assert hasattr(result, 'result')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'message')
    
    def test_rule_engine_execute_specific_rule_types(self):
        """测试执行特定类型的规则"""
        patent_data = {
            "title": "测试发明",
            "applicant": "测试公司",
            "claims": ["权利要求1"]
        }
        
        # 只执行形式审查规则
        results = self.rule_engine.execute_rules(
            patent_data, 
            rule_types=[RuleType.FORMAL]
        )
        
        # 验证只返回形式审查规则的结果
        for result in results:
            assert result.rule_type == RuleType.FORMAL
    
    def test_rule_engine_get_summary(self):
        """测试获取执行结果摘要"""
        patent_data = {
            "title": "一种新型螺栓结构",
            "applicant": "测试公司",
            "claims": [
                "1. 一种螺栓，包括螺栓头和螺栓杆，其特征在于：螺栓头为六边形。"
            ],
            "description": "详细说明"
        }
        
        results = self.rule_engine.execute_rules(patent_data)
        summary = self.rule_engine.get_summary(results)
        
        assert "total_rules" in summary
        assert "passed" in summary
        assert "failed" in summary
        assert "warnings" in summary
        assert "overall_confidence" in summary
        assert "overall_recommendation" in summary
        
        assert summary["total_rules"] == len(results)
        assert isinstance(summary["overall_confidence"], float)
    
    def test_add_remove_rules(self):
        """测试添加和移除规则"""
        initial_count = len(self.rule_engine.rules)
        
        # 添加新规则
        new_rule = DocumentCompletenessRule()
        new_rule.name = "测试规则"
        self.rule_engine.add_rule(new_rule)
        
        assert len(self.rule_engine.rules) == initial_count + 1
        
        # 移除规则
        self.rule_engine.remove_rule("测试规则")
        
        assert len(self.rule_engine.rules) == initial_count

if __name__ == "__main__":
    pytest.main([__file__])