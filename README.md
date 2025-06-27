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
git clone https://github.com/nyaaaq/ai-.git
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

# OCR配置
TESSERACT_CMD=D:\tessera ocr\tesseract.exe


```

### 5. 安装Tesseract OCR（用于图片文字识别）

- Windows: 下载并安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- macOS: `brew install tesseract tesseract-lang`

### 6. 启动应用

```bash
python app.py
```

访问 http://localhost:5000 即可使用系统。
