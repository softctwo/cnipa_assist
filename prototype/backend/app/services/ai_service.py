"""
AI服务模块 - 集成本地AI模型
"""
import json
import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class AIModelType(Enum):
    """AI模型类型"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    LOCAL = "local"

@dataclass
class AIResponse:
    """AI响应数据结构"""
    success: bool
    content: str
    confidence: float
    processing_time: float
    model_used: str
    error_message: Optional[str] = None

class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        self.default_model = "qwen2.5:7b"
        self.backup_model = "llama2:7b"
        self.timeout = 120  # 2分钟超时
        
    def check_model_availability(self) -> Dict[str, bool]:
        """检查AI模型可用性"""
        availability = {
            "ollama_service": False,
            "primary_model": False,
            "backup_model": False
        }
        
        try:
            # 检查Ollama服务
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                availability["ollama_service"] = True
                
                # 检查模型是否已下载
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                availability["primary_model"] = self.default_model in model_names
                availability["backup_model"] = self.backup_model in model_names
                
        except Exception as e:
            print(f"检查模型可用性失败: {e}")
            
        return availability
    
    def analyze_patent_document(self, patent_text: str, analysis_type: str = "comprehensive") -> AIResponse:
        """
        分析专利文档
        
        Args:
            patent_text: 专利文档文本
            analysis_type: 分析类型 ('comprehensive', 'novelty', 'inventiveness', 'utility')
            
        Returns:
            AIResponse: AI分析结果
        """
        start_time = time.time()
        
        # 构建提示词
        prompt = self._build_analysis_prompt(patent_text, analysis_type)
        
        try:
            # 尝试使用主模型
            response = self._call_ollama_model(self.default_model, prompt)
            if response.success:
                response.processing_time = time.time() - start_time
                return response
            
            # 主模型失败，尝试备用模型
            print("主模型调用失败，尝试备用模型")
            response = self._call_ollama_model(self.backup_model, prompt)
            if response.success:
                response.processing_time = time.time() - start_time
                return response
            
            # 所有模型都失败，返回基于规则的分析
            return self._fallback_analysis(patent_text, analysis_type, start_time)
            
        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                model_used="none",
                error_message=f"AI分析失败: {str(e)}"
            )
    
    def _build_analysis_prompt(self, patent_text: str, analysis_type: str) -> str:
        """构建分析提示词"""
        base_prompt = """你是一名资深的实用新型专利审查员，请根据《专利法》《专利法实施细则》《专利审查指南》对以下专利申请进行分析。

专利申请内容：
{patent_text}

请按照以下要求进行分析："""

        if analysis_type == "comprehensive":
            specific_prompt = """
1. 保护客体分析：判断是否属于实用新型保护范围
2. 形式审查：检查文档完整性和格式规范性
3. 新颖性初步评估：识别关键技术特征
4. 创造性初步评估：分析技术方案的创新性
5. 实用性评估：判断技术方案的可实施性

请以JSON格式输出分析结果：
{
    "subject_matter": {"compliant": true/false, "reason": "原因"},
    "formal_examination": {"compliant": true/false, "issues": ["问题列表"]},
    "novelty": {"assessment": "评估结果", "key_features": ["关键特征"]},
    "inventiveness": {"assessment": "评估结果", "innovation_points": ["创新点"]},
    "utility": {"compliant": true/false, "reason": "原因"},
    "overall_recommendation": "总体建议",
    "confidence": 0.85
}"""
        elif analysis_type == "novelty":
            specific_prompt = """
专门进行新颖性分析：
1. 提取权利要求的技术特征
2. 识别关键技术特征和区别特征
3. 评估新颖性风险
4. 提供检索建议

请以JSON格式输出：
{
    "technical_features": ["技术特征列表"],
    "key_features": ["关键特征"],
    "novelty_risk": "high/medium/low",
    "search_suggestions": ["检索建议"],
    "confidence": 0.80
}"""
        elif analysis_type == "inventiveness":
            specific_prompt = """
专门进行创造性分析：
1. 识别技术问题和技术效果
2. 分析技术方案的创新性
3. 评估显而易见性
4. 提供创造性评估意见

请以JSON格式输出：
{
    "technical_problem": "技术问题",
    "technical_effect": "技术效果",
    "innovation_analysis": "创新性分析",
    "obviousness_risk": "high/medium/low",
    "recommendation": "建议",
    "confidence": 0.75
}"""
        else:  # utility
            specific_prompt = """
专门进行实用性分析：
1. 检查技术方案完整性
2. 评估可制造性和可实施性
3. 分析技术效果的真实性
4. 判断是否违背自然规律

请以JSON格式输出：
{
    "completeness": {"compliant": true/false, "issues": ["问题"]},
    "manufacturability": {"feasible": true/false, "reason": "原因"},
    "technical_effect": {"credible": true/false, "analysis": "分析"},
    "natural_law": {"compliant": true/false, "reason": "原因"},
    "overall_utility": true/false,
    "confidence": 0.90
}"""
        
        return base_prompt.format(patent_text=patent_text[:4000]) + specific_prompt  # 限制文本长度
    
    def _call_ollama_model(self, model_name: str, prompt: str) -> AIResponse:
        """调用Ollama模型"""
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # 降低随机性，提高一致性
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "")
                
                # 尝试解析JSON响应
                confidence = self._extract_confidence(content)
                
                return AIResponse(
                    success=True,
                    content=content,
                    confidence=confidence,
                    processing_time=0,  # 将在调用处设置
                    model_used=model_name
                )
            else:
                return AIResponse(
                    success=False,
                    content="",
                    confidence=0.0,
                    processing_time=0,
                    model_used=model_name,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            return AIResponse(
                success=False,
                content="",
                confidence=0.0,
                processing_time=0,
                model_used=model_name,
                error_message="请求超时"
            )
        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                confidence=0.0,
                processing_time=0,
                model_used=model_name,
                error_message=str(e)
            )
    
    def _extract_confidence(self, content: str) -> float:
        """从AI响应中提取置信度"""
        try:
            # 尝试解析JSON
            if content.strip().startswith('{'):
                data = json.loads(content)
                return float(data.get("confidence", 0.5))
        except:
            pass
        
        # 如果无法解析，返回默认置信度
        return 0.6
    
    def _fallback_analysis(self, patent_text: str, analysis_type: str, start_time: float) -> AIResponse:
        """降级分析方法（基于规则）"""
        print("使用降级分析方法")
        
        # 基于关键词的简单分析
        analysis_result = {
            "method": "rule_based_fallback",
            "analysis_type": analysis_type,
            "summary": "由于AI模型不可用，使用基于规则的分析方法",
            "recommendations": [
                "建议手动进行详细审查",
                "检查文档完整性",
                "进行现有技术检索"
            ]
        }
        
        # 简单的关键词检测
        keywords_found = []
        patent_keywords = ["发明", "实用新型", "技术方案", "权利要求", "技术效果"]
        for keyword in patent_keywords:
            if keyword in patent_text:
                keywords_found.append(keyword)
        
        analysis_result["keywords_found"] = keywords_found
        analysis_result["basic_check"] = len(keywords_found) >= 3
        
        return AIResponse(
            success=True,
            content=json.dumps(analysis_result, ensure_ascii=False, indent=2),
            confidence=0.3,  # 降级方法置信度较低
            processing_time=time.time() - start_time,
            model_used="rule_based"
        )
    
    def generate_examination_opinion(self, analysis_result: str, opinion_type: str = "notice") -> AIResponse:
        """
        生成审查意见
        
        Args:
            analysis_result: AI分析结果
            opinion_type: 意见类型 ('notice', 'grant', 'rejection')
            
        Returns:
            AIResponse: 生成的审查意见
        """
        start_time = time.time()
        
        prompt = f"""基于以下分析结果，生成标准的专利审查意见书：

分析结果：
{analysis_result}

请生成{opinion_type}类型的审查意见，要求：
1. 严格按照国家知识产权局的格式
2. 引用准确的法律条款
3. 逻辑清晰，理由充分
4. 语言专业、客观

请以JSON格式输出：
{{
    "opinion_type": "{opinion_type}",
    "main_content": "审查意见正文",
    "legal_basis": ["法律依据"],
    "recommendations": ["修改建议"],
    "deadline": "答复期限",
    "confidence": 0.80
}}"""
        
        try:
            response = self._call_ollama_model(self.default_model, prompt)
            if response.success:
                response.processing_time = time.time() - start_time
                return response
            else:
                # 降级到模板生成
                return self._generate_template_opinion(opinion_type, start_time)
                
        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                model_used="none",
                error_message=f"审查意见生成失败: {str(e)}"
            )
    
    def _generate_template_opinion(self, opinion_type: str, start_time: float) -> AIResponse:
        """生成模板化审查意见"""
        templates = {
            "notice": {
                "main_content": "经审查，该实用新型专利申请存在以下问题需要修改：\n1. 请补充完善技术方案的具体实施方式\n2. 请明确权利要求的技术特征\n3. 请核实申请文件的格式规范性",
                "legal_basis": ["专利法第26条第3款", "专利法第26条第4款"],
                "recommendations": ["补充技术细节", "修改权利要求", "规范文档格式"],
                "deadline": "收到通知书之日起2个月内"
            },
            "grant": {
                "main_content": "经审查，该实用新型专利申请符合专利法的相关规定，决定授予实用新型专利权。",
                "legal_basis": ["专利法第22条", "专利法第26条"],
                "recommendations": ["办理登记手续", "缴纳相关费用"],
                "deadline": "收到通知书之日起2个月内办理登记手续"
            },
            "rejection": {
                "main_content": "经审查，该实用新型专利申请不符合专利法的相关规定，决定予以驳回。",
                "legal_basis": ["专利法第22条第2款", "专利法第22条第3款"],
                "recommendations": ["可在3个月内请求复审"],
                "deadline": "收到决定书之日起3个月内"
            }
        }
        
        template = templates.get(opinion_type, templates["notice"])
        result = {
            "opinion_type": opinion_type,
            "method": "template_based",
            **template,
            "confidence": 0.4
        }
        
        return AIResponse(
            success=True,
            content=json.dumps(result, ensure_ascii=False, indent=2),
            confidence=0.4,
            processing_time=time.time() - start_time,
            model_used="template"
        )

# 创建全局AI服务实例
ai_service = AIService()