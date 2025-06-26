import requests
import json
import time
import logging
from typing import Generator, Optional
from config import Config

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def stream_completion(self, prompt: str, retry_times: int = 3) -> Generator[str, None, None]:
        """流式获取补全结果"""
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": Config.MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是一个专业的学习助手，帮助学生整理知识、创建思维导图和生成复习题。"},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "temperature": Config.TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS
        }
        
        for attempt in range(retry_times):
            try:
                response = self.session.post(
                    url, 
                    json=data, 
                    stream=True,
                    timeout=Config.STREAM_TIMEOUT
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]
                            if line == '[DONE]':
                                break
                            try:
                                chunk = json.loads(line)
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                logger.warning(f"无法解析JSON: {line}")
                                continue
                break
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求失败 (尝试 {attempt + 1}/{retry_times}): {str(e)}")
                if attempt < retry_times - 1:
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))
                else:
                    raise Exception(f"API请求失败: {str(e)}")
    
    def get_completion(self, prompt: str, retry_times: int = 3) -> str:
        """获取完整的补全结果"""
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": Config.MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是一个专业的学习助手，帮助学生整理知识、创建思维导图和生成复习题。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": Config.TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS
        }
        
        for attempt in range(retry_times):
            try:
                response = self.session.post(url, json=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if 'choices' in result and result['choices']:
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception("API返回格式错误")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求失败 (尝试 {attempt + 1}/{retry_times}): {str(e)}")
                if attempt < retry_times - 1:
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))
                else:
                    raise Exception(f"API请求失败: {str(e)}")