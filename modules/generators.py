import os
import json
import logging
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import networkx as nx
from config import Config
import time
import re

logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class MindMapGenerator:
    """思维导图生成器"""
    
    def build_prompt(self, content: str) -> str:
        """构建思维导图生成提示词"""
        return f"""请根据以下内容生成一个结构化的思维导图。

内容：
{content}

要求：
1. 提取核心主题作为中心节点
2. 识别主要分支（一级节点）
3. 为每个主要分支添加子节点（二级、三级节点）
4. 保持层次清晰，逻辑连贯
5. 每个节点的文字要简洁明了

请以JSON格式输出思维导图结构：
{{
    "title": "中心主题",
    "children": [
        {{
            "name": "一级节点1",
            "children": [
                {{"name": "二级节点1"}},
                {{"name": "二级节点2"}}
            ]
        }}
    ]
}}"""
    
    def parse_mindmap_structure(self, response: str) -> Dict:
        """解析思维导图结构"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
        
        # 如果解析失败，返回默认结构
        return {
            "title": "主题",
            "children": [
                {"name": "分支1", "children": []},
                {"name": "分支2", "children": []}
            ]
        }
    
    def generate_mindmap_image(self, response: str) -> str:
        """生成思维导图图片"""
        # 解析结构
        structure = self.parse_mindmap_structure(response)
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(Config.MINDMAP_WIDTH/100, Config.MINDMAP_HEIGHT/100))
        
        # 创建有向图
        G = nx.DiGraph()
        
        # 使用分层布局算法
        self._build_graph(G, structure)
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # 绘制思维导图
        # 绘制节点
        node_colors = self._get_node_colors(G)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
        
        # 绘制标签
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_family='SimHei')
        
        ax.axis('off')
        
        # 保存图片
        timestamp = str(int(time.time()))
        filename = f"mindmap_{timestamp}.png"
        filepath = os.path.join(Config.OUTPUT_FOLDER, filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return f"/outputs/{filename}"
    
    def _build_graph(self, G, node, parent=None, level=0):
        """递归构建图"""
        # 确定节点ID和标签
        if parent is None:
            node_id = "root"
            label = node.get('title', '主题')
        else:
            node_id = f"node_{len(G.nodes)}"
            label = node.get('name', '')
        
        # 添加节点
        G.add_node(node_id, label=label, level=level)
        
        # 添加边
        if parent:
            G.add_edge(parent, node_id)
        
        # 递归处理子节点
        if 'children' in node:
            for child in node['children']:
                self._build_graph(G, child, node_id, level + 1)
    
    def _get_node_colors(self, G):
        """根据节点层级获取颜色"""
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7']
        node_colors = []
        
        for node in G.nodes():
            level = G.nodes[node].get('level', 0)
            color = colors[level % len(colors)]
            node_colors.append(color)
        
        return node_colors


class NoteGenerator:
    """笔记生成器"""
    
    def build_prompt(self, content: str) -> str:
        """构建笔记生成提示词"""
        return f"""请根据以下内容生成详细的学习笔记。

内容：
{content}

要求：
1. 提取并整理关键概念和要点
2. 使用清晰的标题和子标题组织内容
3. 对重要概念进行解释和扩展
4. 添加总结和要点回顾
5. 使用Markdown格式，包括：
   - # 一级标题
   - ## 二级标题
   - **重点内容**
   - - 列表项
   - > 引用或重要提示

请生成结构化的学习笔记。"""
    
    def format_notes(self, response: str) -> str:
        """格式化笔记内容"""
        # 确保响应使用正确的Markdown格式
        # 这里可以添加额外的格式化逻辑
        return response


class QuizGenerator:
    """复习题生成器"""
    
    def build_prompt(self, content: str, difficulty: str = "medium") -> str:
        """构建复习题生成提示词"""
        difficulty_map = {
            "easy": "简单（基础概念理解）",
            "medium": "中等（概念应用和分析）",
            "hard": "困难（综合运用和深度思考）",
            "mixed": "混合（包含各种难度）"
        }
        
        difficulty_desc = difficulty_map.get(difficulty, "中等")
        
        return f"""请根据以下内容生成复习题。

内容：
{content}

要求：
1. 难度等级：{difficulty_desc}
2. 题目类型包括：
   - 选择题（单选/多选）
   - 判断题
   - 填空题
   - 简答题
   - 分析题（仅困难模式）
3. 每道题目都要提供答案和解析
4. 题目要覆盖内容的关键知识点

请按以下格式生成题目：

## 选择题

1. [题目内容]
   A. 选项1
   B. 选项2
   C. 选项3
   D. 选项4
   
   **答案**：B
   **解析**：[解释为什么选B]

## 判断题

1. [题目内容]（对/错）
   
   **答案**：对
   **解析**：[解释原因]

## 填空题

1. [题目内容，用____表示空白]
   
   **答案**：[填空答案]
   **解析**：[解释]

## 简答题

1. [题目内容]
   
   **参考答案**：[答案内容]
   **评分要点**：[关键点]

请生成5-10道高质量的复习题。"""
    
    def format_quiz(self, response: str) -> str:
        """格式化复习题"""
        # 可以添加额外的格式化逻辑
        return response