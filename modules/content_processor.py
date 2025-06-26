import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class ContentProcessor:
    """内容预处理器"""
    
    def __init__(self):
        self.max_length = 10000  # 最大字符长度
    
    def preprocess(self, content: str) -> str:
        """预处理内容"""
        # 清理内容
        content = self.clean_text(content)
        
        # 截断过长内容
        if len(content) > self.max_length:
            logger.warning(f"内容过长，截断至 {self.max_length} 字符")
            content = content[:self.max_length] + "..."
        
        return content
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊控制字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 规范化换行
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def extract_key_points(self, content: str) -> List[str]:
        """提取关键点"""
        # 按段落分割
        paragraphs = content.split('\n\n')
        
        # 过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 提取每段的第一句作为关键点（简单实现）
        key_points = []
        for para in paragraphs[:10]:  # 最多提取10个关键点
            sentences = re.split(r'[。！？]', para)
            if sentences and sentences[0]:
                key_points.append(sentences[0].strip())
        
        return key_points
    
    def summarize_content(self, content: str, max_length: int = 500) -> str:
        """简单的内容摘要"""
        if len(content) <= max_length:
            return content
        
        # 提取前几个段落
        paragraphs = content.split('\n\n')
        summary = []
        current_length = 0
        
        for para in paragraphs:
            if current_length + len(para) > max_length:
                break
            summary.append(para)
            current_length += len(para)
        
        return '\n\n'.join(summary) + '...'