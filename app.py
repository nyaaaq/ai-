from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import os
import json
import time
from werkzeug.utils import secure_filename
from config import Config
from modules.api_client import DeepSeekClient
from modules.content_processor import ContentProcessor
from modules.generators import MindMapGenerator, NoteGenerator, QuizGenerator
from modules.security import SecurityManager
from modules.file_handler import FileHandler
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# 初始化模块
api_client = DeepSeekClient(Config.API_KEY, Config.API_BASE_URL)
content_processor = ContentProcessor()
security_manager = SecurityManager()
file_handler = FileHandler(Config.UPLOAD_FOLDER)
mindmap_generator = MindMapGenerator()
note_generator = NoteGenerator()
quiz_generator = QuizGenerator()

# 确保上传文件夹存在
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 保存文件
        file_path = file_handler.save_file(file)
        
        # 提取文件内容
        content = file_handler.extract_content(file_path)
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': file.filename
        })
    
    except Exception as e:
        logger.error(f"文件上传错误: {str(e)}")
        return jsonify({'error': f'文件处理失败: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_content():
    """处理内容并生成结果"""
    try:
        data = request.json
        content = data.get('content', '')
        task_type = data.get('task_type', 'notes')  # notes, mindmap, quiz
        difficulty = data.get('difficulty', 'medium')  # easy, medium, hard, mixed
        
        # 安全检查
        if not security_manager.validate_input(content):
            return jsonify({'error': '输入内容包含不允许的内容'}), 400
        
        # 预处理内容
        processed_content = content_processor.preprocess(content)
        
        def generate():
            """生成流式响应"""
            try:
                # 根据任务类型构建提示词
                if task_type == 'mindmap':
                    prompt = mindmap_generator.build_prompt(processed_content)
                    processor = mindmap_generator
                elif task_type == 'quiz':
                    prompt = quiz_generator.build_prompt(processed_content, difficulty)
                    processor = quiz_generator
                else:  # notes
                    prompt = note_generator.build_prompt(processed_content)
                    processor = note_generator
                
                # 获取流式响应
                for chunk in api_client.stream_completion(prompt):
                    if chunk:
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # 生成最终结果
                if task_type == 'mindmap':
                    # 收集完整响应后生成思维导图
                    full_response = api_client.get_completion(prompt)
                    image_path = processor.generate_mindmap_image(full_response)
                    yield f"data: {json.dumps({'type': 'mindmap_complete', 'image_url': image_path})}\n\n"
                
                yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                
            except Exception as e:
                logger.error(f"生成过程错误: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    except Exception as e:
        logger.error(f"处理请求错误: {str(e)}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)