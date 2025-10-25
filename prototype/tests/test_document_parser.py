"""
文档解析器测试
"""
import pytest
import tempfile
import os
from pathlib import Path
from backend.app.services.document_parser import DocumentParser, PatentDocument

class TestDocumentParser:
    
    def setup_method(self):
        """测试前准备"""
        self.parser = DocumentParser()
    
    def test_supported_formats(self):
        """测试支持的文件格式"""
        expected_formats = ['.pdf', '.doc', '.docx', '.txt']
        assert self.parser.supported_formats == expected_formats
    
    def test_parse_text_document(self):
        """测试解析纯文本文档"""
        # 创建测试文本文件
        test_content = """
        申请号：202123456789.0
        申请日：2021年12月15日
        发明名称：一种新型螺栓结构
        申请人：测试公司
        发明人：张三
        
        技术领域
        本实用新型涉及紧固件技术领域，具体涉及一种新型螺栓结构。
        
        背景技术
        现有的螺栓结构存在松动问题。
        
        发明内容
        本实用新型的目的是提供一种防松螺栓结构。
        
        权利要求书
        1. 一种新型螺栓结构，包括螺栓头和螺栓杆，其特征在于：所述螺栓头设有防松槽。
        2. 根据权利要求1所述的螺栓结构，其特征在于：所述防松槽为六边形。
        
        摘要
        本实用新型公开了一种新型螺栓结构，具有防松效果。
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # 解析文档
            patent_doc, metadata = self.parser.parse_document(temp_file)
            
            # 验证解析结果
            assert isinstance(patent_doc, PatentDocument)
            assert patent_doc.application_number == "202123456789.0"
            assert "2021" in patent_doc.application_date
            assert patent_doc.title == "一种新型螺栓结构"
            assert patent_doc.applicant == "测试公司"
            assert patent_doc.inventor == "张三"
            assert "紧固件技术领域" in patent_doc.technical_field
            assert len(patent_doc.claims) == 2
            assert "防松效果" in patent_doc.abstract
            
            # 验证元数据
            assert metadata["file_type"] == "Text"
            assert metadata["parsing_method"] == "text"
            
        finally:
            # 清理临时文件
            os.unlink(temp_file)
    
    def test_validate_document_complete(self):
        """测试完整文档验证"""
        patent_doc = PatentDocument(
            application_number="202123456789.0",
            title="测试发明",
            applicant="测试公司",
            claims=["权利要求1", "权利要求2"],
            abstract="测试摘要"
        )
        
        validation_result = self.parser.validate_document(patent_doc)
        
        assert len(validation_result["errors"]) == 0
        assert len(validation_result["warnings"]) == 0
    
    def test_validate_document_missing_required(self):
        """测试缺少必需字段的文档验证"""
        patent_doc = PatentDocument(
            application_number="202123456789.0"
            # 缺少title, applicant, claims
        )
        
        validation_result = self.parser.validate_document(patent_doc)
        
        assert "缺少发明名称" in validation_result["errors"]
        assert "缺少申请人信息" in validation_result["errors"]
        assert "缺少权利要求书" in validation_result["errors"]
    
    def test_validate_document_warnings(self):
        """测试文档验证警告"""
        patent_doc = PatentDocument(
            title="这是一个非常长的发明名称超过了建议的25个字符限制用于测试警告功能",
            applicant="测试公司",
            claims=["权利要求1"],
            application_number="12345"  # 格式不正确
        )
        
        validation_result = self.parser.validate_document(patent_doc)
        
        assert len(validation_result["errors"]) == 0
        assert "发明名称过长" in str(validation_result["warnings"])
        assert "申请号格式可能不正确" in str(validation_result["warnings"])
    
    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_document("/path/to/nonexistent/file.pdf")
    
    def test_parse_unsupported_format(self):
        """测试解析不支持的文件格式"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="不支持的文件格式"):
                self.parser.parse_document(temp_file)
        finally:
            os.unlink(temp_file)

if __name__ == "__main__":
    pytest.main([__file__])