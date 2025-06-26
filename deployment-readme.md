# 学生学习助手系统 - 部署指南

## 项目概述

基于多模态大语言模型的智能学习助手系统，支持自动生成思维导图、学习笔记和复习题。

### 核心特性
- 🚀 支持多种文件格式（PDF、Word、PPT、图片）
- 🎯 智能生成思维导图、笔记和复习题
- 💬 流式响应，实时交互体验
- 🔒 完善的安全防护机制
- 📊 支持数学公式渲染

## 系统要求

- Python 3.8+
- 操作系统：Windows/Linux/macOS
- 内存：至少4GB RAM
- 存储：至少2GB可用空间

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/student-learning-assistant.git
cd student-learning-assistant
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件并配置以下内容：

```env
# API配置
DEEPSEEK_API_KEY=your_api_key_here
API_BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME=deepseek-ai/DeepSeek-R1

# 文件配置
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs

# 安全配置
SECRET_KEY=your-secret-key-here

# OCR配置（可选）
TESSERACT_CMD=D:\tessera ocr\tesseract.exe

# 调试模式
FLASK_DEBUG=False
```

### 5. 安装Tesseract OCR（可选，用于图片文字识别）

- Windows: 下载并安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- macOS: `brew install tesseract tesseract-lang`

### 6. 启动应用

```bash
python app.py
```

访问 http://localhost:5000 即可使用系统。

## Docker部署（推荐）

### 1. 构建Docker镜像

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要的目录
RUN mkdir -p uploads outputs

EXPOSE 5000

CMD ["python", "app.py"]
```

### 2. 使用docker-compose部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - API_BASE_URL=https://api.siliconflow.cn/v1
      - MODEL_NAME=deepseek-ai/DeepSeek-R1
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    restart: unless-stopped
```

启动服务：

```bash
docker-compose up -d
```

## 云服务部署

### 部署到阿里云/腾讯云

1. 创建云服务器实例（推荐配置：2核4G）
2. 安装Docker和docker-compose
3. 克隆项目并配置环境变量
4. 使用docker-compose启动服务
5. 配置安全组规则，开放5000端口
6. （可选）配置Nginx反向代理和SSL证书

### 部署到Vercel（仅前端）

如需部署纯前端版本，可以将前端代码部署到Vercel，后端API部署到云函数。

## 使用说明

### 基本操作流程

1. **选择输入方式**
   - 文本输入：直接在文本框输入学习内容
   - 文件上传：支持PDF、Word、PPT、图片等格式

2. **选择生成类型**
   - 📝 学习笔记：生成结构化的学习笔记
   - 🗺️ 思维导图：生成可视化思维导图
   - 📋 复习题：生成个性化复习题目

3. **调整参数**（可选）
   - 对于复习题，可选择难度等级

4. **生成内容**
   - 点击"开始生成"按钮
   - 等待流式响应完成

5. **保存结果**
   - 复制：一键复制生成内容
   - 下载：保存为文本文件

### API参数说明

系统支持以下参数调整：

- `temperature`: 控制输出的创造性（0.0-2.0，默认0.7）
- `max_tokens`: 最大输出长度（默认2000）
- `stream`: 是否启用流式响应（默认True）

## 故障排除

### 常见问题

1. **API连接失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看日志文件排查具体错误

2. **文件上传失败**
   - 检查文件大小（限制16MB）
   - 确认文件格式支持
   - 检查uploads目录权限

3. **思维导图生成失败**
   - 确保matplotlib字体配置正确
   - 检查outputs目录写入权限

4. **OCR识别失败**
   - 确认Tesseract已正确安装
   - 检查TESSERACT_CMD路径配置

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# Docker环境查看日志
docker-compose logs -f
```

## 性能优化

### 1. 使用Redis缓存

安装Redis并配置缓存：

```python
# 在config.py添加
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
```

### 2. 使用CDN加速

将静态资源部署到CDN，修改index.html中的资源引用。

### 3. 负载均衡

使用Nginx配置多实例负载均衡：

```nginx
upstream app {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
}

server {
    listen 80;
    location / {
        proxy_pass http://app;
    }
}
```

## 安全建议

1. **生产环境配置**
   - 关闭DEBUG模式
   - 使用强密码的SECRET_KEY
   - 启用HTTPS

2. **API密钥管理**
   - 不要在代码中硬编码密钥
   - 使用环境变量或密钥管理服务
   - 定期轮换API密钥

3. **访问控制**
   - 可添加用户认证功能
   - 限制API调用频率
   - 监控异常访问

## 监控与维护

### 健康检查

访问 `/health` 端点检查系统状态：

```bash
curl http://localhost:5000/health
```

### 定期维护

1. 清理临时文件：
```bash
# 清理超过24小时的上传文件
find uploads -type f -mtime +1 -delete
```

2. 备份重要数据
3. 更新依赖包
4. 监控API使用量

## 技术支持

- 项目文档：[完整文档链接]
- 问题反馈：[GitHub Issues]
- 技术交流：[微信群/Discord]

## 许可证

MIT License

---

**注意**：请确保在部署前仔细阅读并理解所有配置项，特别是安全相关的设置。