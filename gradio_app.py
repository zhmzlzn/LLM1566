#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gradio在线问答评测系统
支持实时问答、模型轮流裁判、累计统计等功能
"""

import gradio as gr
import asyncio
import json
import os
import time
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 导入现有模块
from model_api import ModelAPIClient, ModelConfig
from question_bank import QuestionBank

class OnlineCompetitionDB:
    """在线竞技数据库管理"""
    
    def __init__(self, db_path: str = "online_competition.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建问答记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                judge_model TEXT NOT NULL,
                participant_models TEXT NOT NULL,
                answers TEXT NOT NULL,
                rankings TEXT NOT NULL,
                judge_reasoning TEXT
            )
        """)
        
        # 创建模型得分表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                total_score INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建详细得分记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS score_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qa_record_id INTEGER,
                model_name TEXT NOT NULL,
                rank_position INTEGER NOT NULL,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (qa_record_id) REFERENCES qa_records (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_qa_record(self, question: str, judge_model: str, participant_models: List[str], 
                     answers: Dict[str, str], rankings: List[Tuple[str, int]], 
                     judge_reasoning: str) -> int:
        """添加问答记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO qa_records (question, judge_model, participant_models, answers, rankings, judge_reasoning)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            question,
            judge_model,
            json.dumps(participant_models),
            json.dumps(answers),
            json.dumps(rankings),
            judge_reasoning
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def update_model_scores(self, rankings: List[Tuple[str, int]], record_id: int):
        """更新模型得分"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算得分规则：第1名3分，第2名2分，第3名1分，其他0分
        score_rules = {1: 3, 2: 2, 3: 1}
        
        for rank_pos, (model_name, _) in enumerate(rankings, 1):
            score = score_rules.get(rank_pos, 0)
            
            # 更新或插入模型总分
            cursor.execute("""
                INSERT OR REPLACE INTO model_scores (model_name, total_score, total_questions, last_updated)
                VALUES (
                    ?,
                    COALESCE((SELECT total_score FROM model_scores WHERE model_name = ?), 0) + ?,
                    COALESCE((SELECT total_questions FROM model_scores WHERE model_name = ?), 0) + 1,
                    CURRENT_TIMESTAMP
                )
            """, (model_name, model_name, score, model_name))
            
            # 添加详细得分记录
            cursor.execute("""
                INSERT INTO score_details (qa_record_id, model_name, rank_position, score)
                VALUES (?, ?, ?, ?)
            """, (record_id, model_name, rank_pos, score))
        
        conn.commit()
        conn.close()
    
    def get_model_rankings(self) -> List[Dict[str, Any]]:
        """获取模型排行榜"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT model_name, total_score, total_questions,
                   ROUND(CAST(total_score AS FLOAT) / total_questions, 2) as avg_score
            FROM model_scores
            WHERE total_questions > 0
            ORDER BY total_score DESC, avg_score DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'model_name': row[0],
                'total_score': row[1],
                'total_questions': row[2],
                'avg_score': row[3]
            })
        
        conn.close()
        return results
    
    def get_recent_qa_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的问答记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, question, timestamp, judge_model, rankings, judge_reasoning
            FROM qa_records
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'question': row[1],
                'timestamp': row[2],
                'judge_model': row[3],
                'rankings': json.loads(row[4]),
                'judge_reasoning': row[5]
            })
        
        conn.close()
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总问题数
        cursor.execute("SELECT COUNT(*) FROM qa_records")
        total_questions = cursor.fetchone()[0]
        
        # 参与模型数
        cursor.execute("SELECT COUNT(DISTINCT model_name) FROM model_scores")
        total_models = cursor.fetchone()[0]
        
        # 最活跃模型
        cursor.execute("""
            SELECT model_name, total_questions
            FROM model_scores
            ORDER BY total_questions DESC
            LIMIT 1
        """)
        most_active = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_questions': total_questions,
            'total_models': total_models,
            'most_active_model': most_active[0] if most_active else None,
            'most_active_count': most_active[1] if most_active else 0
        }

class OnlineCompetitionSystem:
    """在线竞技系统"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.db = OnlineCompetitionDB()
        self.api_client = ModelAPIClient()
        self.question_bank = QuestionBank()
        self.models = []
        self.current_judge_index = 0
        
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.models = []
            for model_config in config['models']:
                if model_config.get('api_key') and model_config.get('api_key') != 'your_api_key_here':
                    self.models.append(ModelConfig(**model_config))
            
            if len(self.models) < 3:
                raise ValueError(f"至少需要3个有效模型，当前只有{len(self.models)}个")
            
            self.competition_settings = config.get('competition_settings', {})
            
        except Exception as e:
            raise Exception(f"配置加载失败: {e}")
    
    def get_next_judge(self) -> ModelConfig:
        """获取下一个裁判模型（轮流）"""
        judge = self.models[self.current_judge_index]
        self.current_judge_index = (self.current_judge_index + 1) % len(self.models)
        return judge
    
    def get_participants(self, judge: ModelConfig) -> List[ModelConfig]:
        """获取参赛模型（除了裁判）"""
        return [model for model in self.models if model.name != judge.name]
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """处理用户问题"""
        try:
            # 选择裁判和参赛者
            judge = self.get_next_judge()
            participants = self.get_participants(judge)
            
            # 收集所有参赛者的回答
            answers = {}
            for participant in participants:
                try:
                    answer = await self.api_client.call_model(participant, question)
                    answers[participant.name] = answer
                except Exception as e:
                    answers[participant.name] = f"回答失败: {str(e)}"
            
            # 构建裁判提示
            judge_prompt = self._build_judge_prompt(question, answers)
            
            # 获取裁判评价
            try:
                judge_response = await self.api_client.call_model(judge, judge_prompt)
                rankings, reasoning = self._parse_judge_response(judge_response, list(answers.keys()))
            except Exception as e:
                # 如果裁判失败，使用随机排名
                import random
                model_names = list(answers.keys())
                random.shuffle(model_names)
                rankings = [(name, i+1) for i, name in enumerate(model_names)]
                reasoning = f"裁判评价失败: {str(e)}，使用随机排名"
            
            # 保存到数据库
            record_id = self.db.add_qa_record(
                question=question,
                judge_model=judge.name,
                participant_models=[p.name for p in participants],
                answers=answers,
                rankings=rankings,
                judge_reasoning=reasoning
            )
            
            # 更新得分
            self.db.update_model_scores(rankings, record_id)
            
            return {
                'success': True,
                'judge': judge.name,
                'answers': answers,
                'rankings': rankings,
                'reasoning': reasoning,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_judge_prompt(self, question: str, answers: Dict[str, str]) -> str:
        """构建裁判提示"""
        prompt = f"""请作为一个公正的裁判，对以下问题的多个回答进行评价和排名。

问题：{question}

回答：
"""
        
        for i, (model_name, answer) in enumerate(answers.items(), 1):
            prompt += f"\n{i}. {model_name}的回答：\n{answer}\n"
        
        prompt += """
请按照以下格式给出评价：

排名：
1. [模型名称] - [简短评价]
2. [模型名称] - [简短评价]
3. [模型名称] - [简短评价]
...

评价理由：
[详细说明你的评价标准和理由]

请确保评价公正、客观，考虑回答的准确性、完整性、逻辑性和实用性。
"""
        
        return prompt
    
    def _parse_judge_response(self, response: str, model_names: List[str]) -> Tuple[List[Tuple[str, int]], str]:
        """解析裁判回应"""
        try:
            lines = response.strip().split('\n')
            rankings = []
            reasoning_start = -1
            
            # 查找排名部分
            for i, line in enumerate(lines):
                line = line.strip()
                if '排名：' in line or '排名:' in line:
                    continue
                elif '评价理由：' in line or '评价理由:' in line:
                    reasoning_start = i
                    break
                elif line and (line[0].isdigit() or line.startswith('第')):
                    # 尝试解析排名行
                    for model_name in model_names:
                        if model_name in line:
                            rank = len(rankings) + 1
                            rankings.append((model_name, rank))
                            break
            
            # 提取评价理由
            if reasoning_start > 0:
                reasoning = '\n'.join(lines[reasoning_start+1:]).strip()
            else:
                reasoning = response
            
            # 确保所有模型都有排名
            ranked_models = {name for name, _ in rankings}
            for model_name in model_names:
                if model_name not in ranked_models:
                    rankings.append((model_name, len(rankings) + 1))
            
            return rankings, reasoning
            
        except Exception as e:
            # 解析失败，使用默认排名
            rankings = [(name, i+1) for i, name in enumerate(model_names)]
            reasoning = f"解析失败，使用默认排名。原始回应：{response}"
            return rankings, reasoning

# 全局系统实例
competition_system = None

def init_system():
    """初始化系统"""
    global competition_system
    try:
        competition_system = OnlineCompetitionSystem()
        return "✅ 系统初始化成功", True
    except Exception as e:
        return f"❌ 系统初始化失败: {str(e)}", False

async def process_user_question(question: str):
    """处理用户问题"""
    if not competition_system:
        return "❌ 系统未初始化", "", "", ""
    
    if not question.strip():
        return "❌ 请输入问题", "", "", ""
    
    try:
        # 显示处理状态
        yield "🤔 正在处理您的问题...", "", "", ""
        
        result = await competition_system.process_question(question.strip())
        
        if result['success']:
            # 格式化回答
            answers_text = "## 📝 各模型回答\n\n"
            for model_name, answer in result['answers'].items():
                answers_text += f"### {model_name}\n{answer}\n\n"
            
            # 格式化排名
            rankings_text = f"## 🏆 排名结果（裁判：{result['judge']}）\n\n"
            for i, (model_name, rank) in enumerate(result['rankings']):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "🏅"
                rankings_text += f"{medal} **第{rank}名**: {model_name}\n"
            
            # 格式化评价理由
            reasoning_text = f"## 💭 评价理由\n\n{result['reasoning']}"
            
            status = f"✅ 问题处理完成 ({result['timestamp']})"
            
            yield status, answers_text, rankings_text, reasoning_text
        else:
            yield f"❌ 处理失败: {result['error']}", "", "", ""
            
    except Exception as e:
        yield f"❌ 处理异常: {str(e)}", "", "", ""

def get_model_rankings():
    """获取模型排行榜"""
    if not competition_system:
        return "❌ 系统未初始化"
    
    try:
        rankings = competition_system.db.get_model_rankings()
        
        if not rankings:
            return "📊 暂无排名数据"
        
        # 创建排行榜表格
        df = pd.DataFrame(rankings)
        df.index = df.index + 1  # 从1开始编号
        
        # 格式化表格
        table_html = df.to_html(
            columns=['model_name', 'total_score', 'total_questions', 'avg_score'],
            table_id='rankings-table',
            classes='table table-striped',
            escape=False
        )
        
        # 添加样式
        styled_table = f"""
        <style>
        #rankings-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        #rankings-table th, #rankings-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        #rankings-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        #rankings-table tr:hover {{
            background-color: #f5f5f5;
        }}
        </style>
        
        <h3>🏆 模型排行榜</h3>
        {table_html}
        """
        
        return styled_table
        
    except Exception as e:
        return f"❌ 获取排名失败: {str(e)}"

def get_recent_qa_records():
    """获取最近的问答记录"""
    if not competition_system:
        return "❌ 系统未初始化"
    
    try:
        records = competition_system.db.get_recent_qa_records(10)
        
        if not records:
            return "📝 暂无问答记录"
        
        html_content = "<h3>📝 最近问答记录</h3>\n"
        
        for record in records:
            html_content += f"""
            <div style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px;">
                <h4>问题 #{record['id']}</h4>
                <p><strong>时间:</strong> {record['timestamp']}</p>
                <p><strong>问题:</strong> {record['question']}</p>
                <p><strong>裁判:</strong> {record['judge_model']}</p>
                <p><strong>排名:</strong> 
            """
            
            for i, (model_name, rank) in enumerate(record['rankings']):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "🏅"
                html_content += f"{medal} {model_name} "
            
            html_content += "</p></div>\n"
        
        return html_content
        
    except Exception as e:
        return f"❌ 获取记录失败: {str(e)}"

def get_statistics_chart():
    """获取统计图表"""
    if not competition_system:
        return None
    
    try:
        rankings = competition_system.db.get_model_rankings()
        
        if not rankings:
            return None
        
        # 创建得分分布图
        df = pd.DataFrame(rankings)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('总分排名', '平均分排名', '参与问题数', '得分分布'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "histogram"}]]
        )
        
        # 总分排名
        fig.add_trace(
            go.Bar(x=df['model_name'], y=df['total_score'], name='总分'),
            row=1, col=1
        )
        
        # 平均分排名
        fig.add_trace(
            go.Bar(x=df['model_name'], y=df['avg_score'], name='平均分'),
            row=1, col=2
        )
        
        # 参与问题数
        fig.add_trace(
            go.Bar(x=df['model_name'], y=df['total_questions'], name='问题数'),
            row=2, col=1
        )
        
        # 得分分布
        fig.add_trace(
            go.Histogram(x=df['total_score'], name='得分分布'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="模型竞技统计",
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"图表生成失败: {e}")
        return None

def create_gradio_interface():
    """创建Gradio界面"""
    
    # 初始化系统
    init_status, init_success = init_system()
    
    with gr.Blocks(title="大模型在线竞技系统", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🤖 大模型在线竞技系统
        
        欢迎使用大模型在线竞技系统！您可以提问任何问题，系统会让多个大模型回答并进行排名。
        """)
        
        # 显示初始化状态
        gr.Markdown(f"**系统状态:** {init_status}")
        
        with gr.Tabs():
            # 问答页面
            with gr.TabItem("💬 问答页面"):
                with gr.Row():
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="请输入您的问题",
                            placeholder="例如：请解释什么是人工智能？",
                            lines=3
                        )
                        submit_btn = gr.Button("🚀 提交问题", variant="primary")
                        
                        status_output = gr.Textbox(
                            label="处理状态",
                            interactive=False
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("""
                        ### 📋 使用说明
                        1. 在左侧输入框中输入您的问题
                        2. 点击"提交问题"按钮
                        3. 系统会自动选择裁判和参赛模型
                        4. 查看各模型的回答和排名结果
                        5. 结果会自动保存到统计页面
                        """)
                
                # 回答展示区域
                with gr.Row():
                    answers_output = gr.Markdown(label="模型回答")
                
                with gr.Row():
                    with gr.Column():
                        rankings_output = gr.Markdown(label="排名结果")
                    with gr.Column():
                        reasoning_output = gr.Markdown(label="评价理由")
                
                # 绑定提交事件
                submit_btn.click(
                    fn=process_user_question,
                    inputs=[question_input],
                    outputs=[status_output, answers_output, rankings_output, reasoning_output]
                )
            
            # 统计页面
            with gr.TabItem("📊 统计信息"):
                with gr.Row():
                    refresh_btn = gr.Button("🔄 刷新数据", variant="secondary")
                
                with gr.Row():
                    with gr.Column():
                        rankings_display = gr.HTML(label="模型排行榜")
                    with gr.Column():
                        records_display = gr.HTML(label="最近问答记录")
                
                with gr.Row():
                    stats_chart = gr.Plot(label="统计图表")
                
                # 绑定刷新事件
                def refresh_all():
                    return (
                        get_model_rankings(),
                        get_recent_qa_records(),
                        get_statistics_chart()
                    )
                
                refresh_btn.click(
                    fn=refresh_all,
                    outputs=[rankings_display, records_display, stats_chart]
                )
                
                # 页面加载时自动刷新
                app.load(
                    fn=refresh_all,
                    outputs=[rankings_display, records_display, stats_chart]
                )
    
    return app

if __name__ == "__main__":
    # 创建并启动Gradio应用
    app = create_gradio_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )