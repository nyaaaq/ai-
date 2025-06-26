
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
import matplotlib

logger = logging.getLogger(__name__)

# 配置matplotlib以支持LaTeX和中文
matplotlib.rcParams['text.usetex'] = False  # 使用matplotlib的数学渲染而不是完整的LaTeX
matplotlib.rcParams['mathtext.fontset'] = 'cm'  # 使用Computer Modern字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

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
6. 如果涉及数学公式，请保留原始的LaTeX格式（用$符号包围）

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
        except Exception as e:
            logger.error(f"解析JSON失败: {e}")
        
        # 如果解析失败，返回默认结构
        return {
            "title": "主题",
            "children": [
                {"name": "分支1", "children": []},
                {"name": "分支2", "children": []}
            ]
        }
    
    def process_math_text(self, text: str) -> tuple:
        """处理包含数学公式的文本，返回处理后的文本和是否包含数学公式"""
        # 检查是否包含数学公式
        has_math = '$' in text
        
        if not has_math:
            return text, False
        
        # 保持数学公式格式，matplotlib会自动处理
        return text, True
    
    def wrap_text(self, text: str, max_width: int = 15) -> str:
        """智能换行文本，考虑数学公式"""
        # 如果文本包含数学公式，特殊处理
        if '$' in text:
            # 分割数学公式和普通文本
            parts = re.split(r'(\$[^$]+\$)', text)
            result_parts = []
            
            for part in parts:
                if part.startswith('$') and part.endswith('$'):
                    # 数学公式不换行
                    result_parts.append(part)
                else:
                    # 普通文本按长度换行
                    if len(part) > max_width:
                        wrapped = '\n'.join([part[i:i+max_width] for i in range(0, len(part), max_width)])
                        result_parts.append(wrapped)
                    else:
                        result_parts.append(part)
            
            return ''.join(result_parts)
        else:
            # 普通文本直接换行
            if len(text) > max_width:
                return '\n'.join([text[i:i+max_width] for i in range(0, len(text), max_width)])
            return text
    
    def generate_mindmap_image(self, response: str) -> str:
        """生成思维导图图片"""
        try:
            # 解析结构
            structure = self.parse_mindmap_structure(response)
            
            # 创建图形，增大图形尺寸以容纳更多内容
            fig = plt.figure(figsize=(20, 16))
            ax = fig.add_subplot(111)
            
            # 创建有向图
            G = nx.Graph()
            
            # 递归构建图
            node_info = {}  # 存储节点的额外信息
            self._build_graph(G, structure, node_info)
            
            # 使用分层布局
            pos = self._hierarchical_layout(G, structure)
            
            # 设置节点大小和颜色
            node_sizes = []
            node_colors = []
            for node in G.nodes():
                level = G.nodes[node].get('level', 0)
                # 根据层级设置大小
                size = 8000 - level * 1200
                node_sizes.append(max(size, 3000))
                # 根据层级设置颜色
                colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7', '#fd79a8']
                node_colors.append(colors[level % len(colors)])
            
            # 绘制边
            nx.draw_networkx_edges(G, pos, edge_color='#ddd', width=2, alpha=0.6, ax=ax)
            
            # 绘制节点
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, ax=ax)
            
            # 绘制标签（支持数学公式）
            labels = nx.get_node_attributes(G, 'label')
            for node, (x, y) in pos.items():
                label = labels[node]
                has_math = '$' in label
                
                # 智能换行
                wrapped_label = self.wrap_text(label, max_width=20)
                
                # 根据节点层级调整字体大小
                level = G.nodes[node].get('level', 0)
                fontsize = 14 - level * 2
                fontsize = max(fontsize, 8)
                
                # 绘制文本
                if has_math:
                    # 包含数学公式的文本
                    ax.text(x, y, wrapped_label, 
                           horizontalalignment='center',
                           verticalalignment='center',
                           fontsize=fontsize,
                           fontfamily='SimHei',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                           wrap=True)
                else:
                    # 普通文本
                    ax.text(x, y, wrapped_label,
                           horizontalalignment='center',
                           verticalalignment='center',
                           fontsize=fontsize,
                           fontfamily='SimHei',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                           wrap=True)
            
            # 设置图形属性
            ax.set_xlim(min(x for x, y in pos.values()) - 2, max(x for x, y in pos.values()) + 2)
            ax.set_ylim(min(y for x, y in pos.values()) - 2, max(y for x, y in pos.values()) + 2)
            ax.axis('off')
            
            # 添加标题（如果有的话）
            if 'title' in structure:
                fig.suptitle(structure['title'], fontsize=20, fontfamily='SimHei', y=0.98)
            
            plt.tight_layout()
            
            # 保存图片
            timestamp = str(int(time.time()))
            filename = f"mindmap_{timestamp}.png"
            filepath = os.path.join(Config.OUTPUT_FOLDER, filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none',
                       pad_inches=0.5)
            plt.close()
            
            logger.info(f"思维导图已保存到: {filepath}")
            return f"/outputs/{filename}"
            
        except Exception as e:
            logger.error(f"生成思维导图失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _build_graph(self, G, node, node_info, parent=None, level=0):
        """递归构建图"""
        # 确定节点ID和标签
        if parent is None:
            node_id = "root"
            label = node.get('title', '主题')
        else:
            node_id = f"node_{len(G.nodes)}"
            label = node.get('name', '')
        
        # 处理数学公式
        processed_label, has_math = self.process_math_text(label)
        
        # 添加节点
        G.add_node(node_id, label=processed_label, level=level, has_math=has_math)
        node_info[node_id] = {'has_math': has_math}
        
        # 添加边
        if parent:
            G.add_edge(parent, node_id)
        
        # 递归处理子节点
        if 'children' in node and node['children']:
            for child in node['children']:
                self._build_graph(G, child, node_info, node_id, level + 1)
    
    def _hierarchical_layout(self, G, root_structure):
        """创建分层布局"""
        pos = {}
        
        def _assign_positions(node_id, structure, x=0, y=0, layer=0, parent_x=0, sibling_index=0, num_siblings=1):
            pos[node_id] = (x, y)
            
            children = structure.get('children', [])
            if not children:
                return
            
            # 计算子节点的间距
            num_children = len(children)
            if num_children == 0:
                return
            
            # 根据层级调整水平间距
            if layer == 0:
                h_spacing = 6.0
            elif layer == 1:
                h_spacing = 3.0
            else:
                h_spacing = 1.5
            
            # 计算子节点的起始x位置
            total_width = (num_children - 1) * h_spacing
            start_x = x - total_width / 2
            
            # 递归处理子节点
            for i, child in enumerate(children):
                child_x = start_x + i * h_spacing
                child_y = y - 2.0  # 垂直间距
                child_id = f"node_{len(pos)}"
                _assign_positions(child_id, child, child_x, child_y, layer + 1, x, i, num_children)
        
        # 从根节点开始分配位置
        _assign_positions("root", root_structure)
        
        return pos


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
6. 如果有数学公式，请使用LaTeX格式，用$...$包围行内公式，用$$...$$包围独立公式

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
5. 如果题目涉及数学公式，请使用LaTeX格式，用$...$包围行内公式，用$$...$$包围独立公式

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