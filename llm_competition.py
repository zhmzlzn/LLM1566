#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型竞技算法主程序
实现多个大模型轮流当裁判和参赛选手的竞技机制
"""

import json
import random
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import asyncio
import logging

# 导入自定义模块
from model_api import ModelAPIClient, ModelConfig
from question_bank import QuestionBank, Question

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Answer:
    """答案类"""
    model_name: str
    content: str
    timestamp: float

@dataclass
class JudgmentResult:
    """裁判结果类"""
    question_id: int
    judge_model: str
    rankings: List[Tuple[str, int]]  # (model_name, score)
    reasoning: str

class LLMCompetition:
    """大模型竞技主类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化竞技系统"""
        self.config = self._load_config(config_path)
        self.models = self._parse_models()
        self.api_client = ModelAPIClient()
        self.question_bank = QuestionBank()
        self.questions = []
        self.results = []
        self.final_scores = defaultdict(int)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件 {config_path} 不存在")
            raise
        except json.JSONDecodeError:
            logger.error(f"配置文件 {config_path} 格式错误")
            raise
    
    def _parse_models(self) -> List[ModelConfig]:
        """解析模型配置"""
        models = []
        for model_data in self.config['models']:
            models.append(ModelConfig(**model_data))
        return models
    
    def validate_setup(self) -> bool:
        """验证竞技设置"""
        min_models = self.config['competition_settings']['min_models']
        if len(self.models) < min_models:
            logger.error(f"参赛模型数量不足，至少需要 {min_models} 个模型，当前只有 {len(self.models)} 个")
            return False
        
        logger.info(f"验证通过：共有 {len(self.models)} 个模型参赛")
        for model in self.models:
            logger.info(f"  - {model.name} ({model.provider})")
        return True
    
    async def generate_questions(self) -> List[Question]:
        """生成或加载问题"""
        settings = self.config['competition_settings']['question_generation']
        
        if settings['enabled']:
            logger.info("开始生成问题...")
            questions = await self._generate_questions_by_llm(settings)
        else:
            logger.info("从预设问题库加载问题...")
            questions = self._load_predefined_questions()
        
        self.questions = questions
        logger.info(f"共准备了 {len(questions)} 个问题")
        return questions
    
    async def _generate_questions_by_llm(self, settings: Dict[str, Any]) -> List[Question]:
        """使用大模型生成问题"""
        # 选择第一个模型作为问题生成器
        generator_model = self.models[0]
        
        prompt = f"""
请生成 {settings['count']} 个用于大模型竞技的问题。

要求：
- 难度等级：{settings['difficulty']}
- 涵盖主题：{', '.join(settings['topics'])}
- 每个问题应该有一定的挑战性，能够区分不同模型的能力
- 问题应该客观、公平，便于评判

请按以下JSON格式返回：
[
  {{
    "content": "问题内容",
    "topic": "问题主题",
    "difficulty": "难度等级"
  }}
]
"""
        
        try:
            response = await self._call_model(generator_model, prompt)
            questions_data = json.loads(response)
            
            questions = []
            for i, q_data in enumerate(questions_data):
                questions.append(Question(
                    id=i + 1,
                    content=q_data['content'],
                    topic=q_data['topic'],
                    difficulty=q_data['difficulty']
                ))
            
            return questions
        except Exception as e:
            logger.error(f"生成问题失败：{e}")
            return self._get_fallback_questions()
    
    def _load_predefined_questions(self) -> List[Question]:
        """加载预设问题"""
        settings = self.config['competition_settings']['question_generation']
        topics = settings.get('topics', [])
        difficulty = settings.get('difficulty', 'medium')
        count = settings.get('count', 5)
        
        if topics:
            questions = self.question_bank.get_random_questions(count, topics=topics, difficulty=difficulty)
        else:
            questions = self.question_bank.get_random_questions(count, difficulty=difficulty)
        
        return questions if questions else self._get_fallback_questions()
    
    def _get_fallback_questions(self) -> List[Question]:
        """获取备用问题"""
        fallback_questions = [
            Question(1, "请解释量子计算的基本原理，并说明它与经典计算的主要区别。", "科学技术", "medium"),
            Question(2, "如果你是一家初创公司的CEO，面临资金短缺的困境，你会采取哪些策略来解决这个问题？", "商业管理", "medium"),
            Question(3, "编写一个Python函数，实现快速排序算法，并分析其时间复杂度。", "编程算法", "medium"),
            Question(4, "分析莎士比亚《哈姆雷特》中'生存还是毁灭'这句话的深层含义。", "文学艺术", "hard"),
            Question(5, "设计一个可持续发展的城市交通系统，考虑环保、效率和成本因素。", "创新设计", "hard")
        ]
        return fallback_questions
    
    async def run_competition(self) -> Dict[str, Any]:
        """运行完整的竞技流程"""
        logger.info("=== 大模型竞技开始 ===")
        
        # 验证设置
        if not self.validate_setup():
            return {"error": "设置验证失败"}
        
        # 生成问题
        await self.generate_questions()
        
        # 对每个问题进行竞技
        for question in self.questions:
            logger.info(f"\n--- 问题 {question.id}: {question.content[:50]}... ---")
            
            # 轮流让每个模型当裁判
            for judge_idx, judge_model in enumerate(self.models):
                logger.info(f"裁判：{judge_model.name}")
                
                # 其他模型作为参赛选手
                contestants = [m for i, m in enumerate(self.models) if i != judge_idx]
                
                # 收集所有选手的答案
                answers = await self._collect_answers(question, contestants)
                
                # 裁判评分
                judgment = await self._judge_answers(question, answers, judge_model)
                
                # 记录结果
                self.results.append(judgment)
                
                # 更新总分
                self._update_scores(judgment)
                
                logger.info(f"本轮排名：{judgment.rankings}")
        
        # 生成最终结果
        final_result = self._generate_final_result()
        
        logger.info("=== 大模型竞技结束 ===")
        return final_result
    
    async def _collect_answers(self, question: Question, contestants: List[ModelConfig]) -> List[Answer]:
        """收集所有参赛选手的答案"""
        logger.info(f"收集 {len(contestants)} 个模型的答案...")
        
        tasks = []
        for model in contestants:
            task = self._get_model_answer(question, model)
            tasks.append(task)
        
        answers = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_answers = []
        for i, answer in enumerate(answers):
            if isinstance(answer, Exception):
                logger.error(f"模型 {contestants[i].name} 回答失败：{answer}")
                # 添加默认答案
                valid_answers.append(Answer(
                    model_name=contestants[i].name,
                    content="抱歉，我无法回答这个问题。",
                    timestamp=time.time()
                ))
            else:
                valid_answers.append(answer)
        
        return valid_answers
    
    async def _get_model_answer(self, question: Question, model: ModelConfig) -> Answer:
        """获取单个模型的答案"""
        prompt = f"请回答以下问题：\n\n{question.content}\n\n请提供详细、准确的答案。"
        
        try:
            response = await self._call_model(model, prompt)
            return Answer(
                model_name=model.name,
                content=response,
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"模型 {model.name} 回答问题失败：{e}")
            raise
    
    async def _judge_answers(self, question: Question, answers: List[Answer], judge_model: ModelConfig) -> JudgmentResult:
        """裁判对答案进行评分排名"""
        # 构建裁判提示词
        answers_text = "\n\n".join([
            f"答案 {i+1} (来自 {answer.model_name}):\n{answer.content}"
            for i, answer in enumerate(answers)
        ])
        
        prompt = f"""
作为公正的裁判，请对以下问题的各个答案进行评分和排名。

问题：{question.content}

答案列表：
{answers_text}

评分标准：
1. 准确性：答案是否正确、准确
2. 完整性：答案是否全面、详细
3. 逻辑性：答案是否逻辑清晰、条理分明
4. 创新性：答案是否有独特见解或创新思路

请按以下JSON格式返回评判结果：
{{
  "rankings": [
    {{"model_name": "模型名称", "score": 分数, "rank": 排名}}
  ],
  "reasoning": "详细的评判理由"
}}

注意：分数范围1-10，排名从1开始（1为最佳）。
"""
        
        try:
            response = await self._call_model(judge_model, prompt)
            judgment_data = json.loads(response)
            
            # 转换为标准格式
            rankings = [(item['model_name'], item['score']) for item in judgment_data['rankings']]
            
            return JudgmentResult(
                question_id=question.id,
                judge_model=judge_model.name,
                rankings=rankings,
                reasoning=judgment_data['reasoning']
            )
        except Exception as e:
            logger.error(f"裁判 {judge_model.name} 评分失败：{e}")
            # 返回随机排名作为备用
            random.shuffle(answers)
            rankings = [(answer.model_name, random.randint(5, 8)) for answer in answers]
            return JudgmentResult(
                question_id=question.id,
                judge_model=judge_model.name,
                rankings=rankings,
                reasoning="评分系统出现错误，使用随机排名。"
            )
    
    def _update_scores(self, judgment: JudgmentResult):
        """更新总分"""
        scoring = self.config['competition_settings']['scoring']
        
        # 按分数排序
        sorted_rankings = sorted(judgment.rankings, key=lambda x: x[1], reverse=True)
        
        for rank, (model_name, score) in enumerate(sorted_rankings):
            if rank == 0:
                self.final_scores[model_name] += scoring['first_place']
            elif rank == 1:
                self.final_scores[model_name] += scoring['second_place']
            elif rank == 2:
                self.final_scores[model_name] += scoring['third_place']
            else:
                self.final_scores[model_name] += scoring['other_place']
    
    def _generate_final_result(self) -> Dict[str, Any]:
        """生成最终结果"""
        # 按总分排序
        final_rankings = sorted(self.final_scores.items(), key=lambda x: x[1], reverse=True)
        
        result = {
            "final_rankings": final_rankings,
            "total_questions": len(self.questions),
            "total_rounds": len(self.results),
            "detailed_results": [
                {
                    "question_id": r.question_id,
                    "question": next(q.content for q in self.questions if q.id == r.question_id),
                    "judge": r.judge_model,
                    "rankings": r.rankings,
                    "reasoning": r.reasoning
                }
                for r in self.results
            ]
        }
        
        return result
    
    async def _call_model(self, model: ModelConfig, prompt: str) -> str:
        """调用大模型API"""
        try:
            return await self.api_client.call_model(model, prompt)
        except Exception as e:
            logger.error(f"调用模型 {model.name} 失败: {e}")
            # 返回错误提示而不是模拟数据
            return f"抱歉，{model.name} 暂时无法响应。错误信息：{str(e)}"
    
    def save_results(self, filename: str = "competition_results.json"):
        """保存竞技结果"""
        result = self._generate_final_result()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存到 {filename}")

# 主程序入口
if __name__ == "__main__":
    async def main():
        competition = LLMCompetition()
        result = await competition.run_competition()
        
        print("\n=== 最终排名 ===")
        for i, (model_name, score) in enumerate(result['final_rankings']):
            print(f"{i+1}. {model_name}: {score} 分")
        
        competition.save_results()
    
    asyncio.run(main())