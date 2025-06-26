import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置"""
    # API配置 - 从环境变量读取
    API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.siliconflow.cn/v1')
    MODEL_NAME = os.getenv('MODEL_NAME', 'deepseek-ai/DeepSeek-R1')
    
    # 验证API Key是否存在
    if not API_KEY:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'pptx', 'png', 'jpg', 'jpeg'}
    
    # 安全配置
    SENSITIVE_WORDS = [
        # 在这里添加敏感词列表
    ]
    
    # 流式响应配置
    STREAM_TIMEOUT = int(os.getenv('STREAM_TIMEOUT', '60'))  # 秒
    RETRY_TIMES = int(os.getenv('RETRY_TIMES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))  # 秒
    
    # 生成配置
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # 思维导图配置
    MINDMAP_WIDTH = int(os.getenv('MINDMAP_WIDTH', '1200'))
    MINDMAP_HEIGHT = int(os.getenv('MINDMAP_HEIGHT', '800'))
    MINDMAP_FONT = os.getenv('MINDMAP_FONT', 'SimHei')  # 中文字体
    
    # Tesseract OCR配置
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', r'D:\tessera ocr\tesseract.exe')
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'