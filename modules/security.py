import re
import logging
from typing import List
from config import Config

logger = logging.getLogger(__name__)

class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.sensitive_words = Config.SENSITIVE_WORDS
        self.injection_patterns = [
            r'(?i)(ignore|forget|disregard).*previous.*instructions',
            r'(?i)you.*are.*now',
            r'(?i)pretend.*to.*be',
            r'(?i)act.*as.*if',
            r'(?i)system.*prompt',
            r'(?i)reveal.*instructions',
            r'(?i)<script.*?>.*?</script>',
            r'(?i)(javascript|eval|exec)\s*\(',
        ]
    
    def validate_input(self, content: str) -> bool:
        """验证输入内容"""
        # 检查内容是否为空
        if not content or not content.strip():
            return False
        
        # 检查内容长度
        if len(content) > 50000:  # 50K字符限制
            logger.warning("输入内容过长")
            return False
        
        # 检查敏感词
        if self.contains_sensitive_words(content):
            logger.warning("输入包含敏感词")
            return False
        
        # 检查指令注入
        if self.detect_injection(content):
            logger.warning("检测到潜在的指令注入")
            return False
        
        return True
    
    def contains_sensitive_words(self, content: str) -> bool:
        """检查是否包含敏感词"""
        content_lower = content.lower()
        for word in self.sensitive_words:
            if word.lower() in content_lower:
                return True
        return False
    
    def detect_injection(self, content: str) -> bool:
        """检测指令注入"""
        for pattern in self.injection_patterns:
            if re.search(pattern, content):
                return True
        return False
    
    def sanitize_output(self, content: str) -> str:
        """清理输出内容"""
        # 移除潜在的HTML/JavaScript
        content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<.*?>', '', content)
        
        # 转义特殊字符
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        content = content.replace('"', '&quot;')
        content = content.replace("'", '&#39;')
        
        return content
    
    def filter_response(self, response: str) -> str:
        """过滤响应内容"""
        # 移除任何敏感词
        for word in self.sensitive_words:
            if word in response:
                response = response.replace(word, '[已过滤]')
        
        return response