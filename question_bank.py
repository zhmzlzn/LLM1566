#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题库模块
提供各种类型和难度的预设问题
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import random

@dataclass
class Question:
    """问题类"""
    id: int
    content: str
    topic: str
    difficulty: str
    expected_skills: List[str] = None

class QuestionBank:
    """问题库类"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
    
    def _initialize_questions(self) -> List[Question]:
        """初始化问题库"""
        questions = []
        
        # 逻辑推理类问题
        logic_questions = [
            Question(1, "有5个房子，每个房子颜色不同，住着不同国籍的人，养不同的宠物，喝不同的饮料，抽不同的烟。根据以下线索，请推断出谁养鱼？\n线索：1.英国人住红房子 2.瑞典人养狗 3.丹麦人喝茶 4.绿房子在白房子左边 5.绿房子主人喝咖啡 6.抽Pall Mall烟的人养鸟 7.黄房子主人抽Dunhill烟 8.住中间房子的人喝牛奶 9.挪威人住第一间房子 10.抽Blends烟的人住在养猫人的隔壁 11.养马的人住在抽Dunhill烟的人隔壁 12.抽Blue Master的人喝啤酒 13.德国人抽Prince烟 14.挪威人住在蓝房子隔壁 15.抽Blends烟的人有一个喝水的邻居", "逻辑推理", "hard", ["逻辑分析", "推理能力"]),
            Question(2, "三个盒子，一个装金币，一个装银币，一个装金银混合币。每个盒子的标签都贴错了。你只能从一个盒子里取出一枚硬币来确定所有盒子的正确内容。应该从哪个盒子取硬币？", "逻辑推理", "medium", ["逻辑分析", "策略思维"]),
            Question(3, "一个岛上有两种人：总是说真话的人和总是说假话的人。你遇到三个人A、B、C。A说：'B和C是同一类型的人'。B说：'A和C不是同一类型的人'。请判断A、B、C分别是哪种人？", "逻辑推理", "medium", ["逻辑分析", "真假判断"])
        ]
        
        # 数学计算类问题
        math_questions = [
            Question(4, "求解方程组：\n2x + 3y = 7\n4x - y = 1\n并验证答案的正确性。", "数学计算", "easy", ["代数运算", "方程求解"]),
            Question(5, "一个圆的半径为r，在圆内接一个正六边形。求正六边形的面积与圆面积的比值，并解释几何原理。", "数学计算", "medium", ["几何计算", "数学推理"]),
            Question(6, "证明：对于任意正整数n，1³ + 2³ + 3³ + ... + n³ = (1 + 2 + 3 + ... + n)²", "数学计算", "hard", ["数学证明", "归纳推理"])
        ]
        
        # 创意写作类问题
        creative_questions = [
            Question(7, "以'时间旅行者的日记'为题，写一篇500字左右的科幻短文。要求情节新颖，逻辑自洽。", "创意写作", "medium", ["创意思维", "文学表达"]),
            Question(8, "请为一个AI助手设计一个有趣的人格设定，包括性格特点、说话风格、兴趣爱好等，并写一段该AI的自我介绍。", "创意写作", "easy", ["角色设计", "创意表达"]),
            Question(9, "创作一首现代诗，主题为'数字时代的孤独'，要求运用至少三种修辞手法，体现深刻的思考。", "创意写作", "hard", ["诗歌创作", "文学技巧"])
        ]
        
        # 知识问答类问题
        knowledge_questions = [
            Question(10, "解释区块链技术的基本原理，并分析其在金融、供应链管理和数字身份验证中的应用前景。", "知识问答", "medium", ["技术理解", "应用分析"]),
            Question(11, "比较分析中国古代的科举制度与现代教育制度的异同，并评价其对社会发展的影响。", "知识问答", "hard", ["历史知识", "比较分析"]),
            Question(12, "什么是CRISPR-Cas9基因编辑技术？请说明其工作原理和在医学领域的应用潜力。", "知识问答", "medium", ["生物技术", "科学原理"])
        ]
        
        # 编程算法类问题
        programming_questions = [
            Question(13, "实现一个LRU（最近最少使用）缓存，支持get和put操作，时间复杂度要求O(1)。请提供完整的代码实现和测试用例。", "编程算法", "hard", ["数据结构", "算法设计"]),
            Question(14, "给定一个整数数组，找出其中两个数的和等于目标值的所有不重复组合。要求时间复杂度优于O(n²)。", "编程算法", "medium", ["算法优化", "数组操作"]),
            Question(15, "设计并实现一个简单的任务调度器，能够按优先级和时间顺序执行任务。", "编程算法", "medium", ["系统设计", "调度算法"])
        ]
        
        # 系统设计类问题
        system_design_questions = [
            Question(16, "设计一个支持百万用户的在线聊天系统，考虑高并发、消息持久化、实时性等要求。请画出系统架构图并说明关键技术选型。", "系统设计", "hard", ["架构设计", "高并发处理"]),
            Question(17, "如何设计一个分布式文件存储系统，确保数据的一致性、可用性和分区容错性？", "系统设计", "hard", ["分布式系统", "CAP理论"]),
            Question(18, "设计一个短URL服务（类似bit.ly），需要考虑URL编码、数据库设计、缓存策略等。", "系统设计", "medium", ["服务设计", "数据库设计"])
        ]
        
        # 商业分析类问题
        business_questions = [
            Question(19, "分析ChatGPT等大语言模型对传统搜索引擎业务的冲击，并提出搜索引擎公司的应对策略。", "商业分析", "medium", ["市场分析", "战略思维"]),
            Question(20, "如果你是一家传统零售企业的CEO，面对电商冲击，你会制定怎样的数字化转型策略？", "商业分析", "medium", ["战略规划", "数字化转型"]),
            Question(21, "评估人工智能在医疗诊断领域的商业价值和风险，并设计一个可行的商业模式。", "商业分析", "hard", ["商业模式", "风险评估"])
        ]
        
        # 合并所有问题
        all_questions = (
            logic_questions + math_questions + creative_questions + 
            knowledge_questions + programming_questions + 
            system_design_questions + business_questions
        )
        
        return all_questions
    
    def get_questions_by_topic(self, topic: str) -> List[Question]:
        """根据主题获取问题"""
        return [q for q in self.questions if q.topic == topic]
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Question]:
        """根据难度获取问题"""
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def get_random_questions(self, count: int, topics: List[str] = None, difficulty: str = None) -> List[Question]:
        """随机获取指定数量的问题"""
        filtered_questions = self.questions
        
        if topics:
            filtered_questions = [q for q in filtered_questions if q.topic in topics]
        
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q.difficulty == difficulty]
        
        if len(filtered_questions) < count:
            return filtered_questions
        
        return random.sample(filtered_questions, count)
    
    def get_all_topics(self) -> List[str]:
        """获取所有主题"""
        return list(set(q.topic for q in self.questions))
    
    def get_all_difficulties(self) -> List[str]:
        """获取所有难度等级"""
        return list(set(q.difficulty for q in self.questions))
    
    def add_question(self, question: Question):
        """添加新问题"""
        # 确保ID唯一
        max_id = max([q.id for q in self.questions]) if self.questions else 0
        question.id = max_id + 1
        self.questions.append(question)
    
    def get_question_by_id(self, question_id: int) -> Question:
        """根据ID获取问题"""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取问题库统计信息"""
        topics = {}
        difficulties = {}
        
        for question in self.questions:
            topics[question.topic] = topics.get(question.topic, 0) + 1
            difficulties[question.difficulty] = difficulties.get(question.difficulty, 0) + 1
        
        return {
            "total_questions": len(self.questions),
            "topics": topics,
            "difficulties": difficulties,
            "available_topics": self.get_all_topics(),
            "available_difficulties": self.get_all_difficulties()
        }

# 全局问题库实例
question_bank = QuestionBank()

if __name__ == "__main__":
    # 测试问题库
    bank = QuestionBank()
    stats = bank.get_statistics()
    
    print("问题库统计信息：")
    print(f"总问题数：{stats['total_questions']}")
    print(f"主题分布：{stats['topics']}")
    print(f"难度分布：{stats['difficulties']}")
    
    print("\n随机获取3个中等难度问题：")
    random_questions = bank.get_random_questions(3, difficulty="medium")
    for q in random_questions:
        print(f"{q.id}. [{q.topic}] {q.content[:50]}...")