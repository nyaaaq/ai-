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
    
    # 安全配置 - 敏感词列表
    SENSITIVE_WORDS = [
        # 政治敏感词
        '反动', '颠覆', '煽动', '暴乱', '分裂', '恐怖主义', '极端主义',
        
        # 暴力相关
        '杀人', '爆炸', '武器', '毒品', '暴力', '血腥', '自杀', '自残',
        
        # 色情相关
        '色情', '淫秽', '裸体', '性交', '强奸', '卖淫', '嫖娼',
        
        # 赌博相关
        '赌博', '赌场', '博彩', '六合彩', '赌球', '赌马',
        
        # 诈骗相关
        '诈骗', '传销', '洗钱', '非法集资', '庞氏骗局',
        
        # 违法信息
        '假证', '假发票', '走私', '贩毒', '黑客', '病毒', '木马',
        
        # 人身攻击
        '侮辱', '诽谤', '人身攻击', '歧视', '仇恨言论',
        
        # 其他不当内容
        '邪教', '迷信', '谣言', '虚假信息', '违禁品',
        
        # 学术不端
        '代写', '抄袭', '作弊', '泄题', '买卖答案', '论文代写',
        
        # 隐私相关
        '个人隐私', '身份证号', '银行卡号', '密码', '泄露隐私'
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