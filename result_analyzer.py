#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果分析模块
用于分析竞技结果并生成详细报告
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Any
from collections import defaultdict
import seaborn as sns
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ResultAnalyzer:
    """结果分析器"""
    
    def __init__(self, result_data: Dict[str, Any]):
        """初始化分析器"""
        self.result_data = result_data
        self.final_rankings = result_data.get('final_rankings', [])
        self.detailed_results = result_data.get('detailed_results', [])
        self.total_questions = result_data.get('total_questions', 0)
        self.total_rounds = result_data.get('total_rounds', 0)
    
    def generate_summary_report(self) -> str:
        """生成总结报告"""
        report = []
        report.append("# 大模型竞技结果分析报告")
        report.append(f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n## 竞技概况")
        report.append(f"- 参赛模型数量：{len(self.final_rankings)}")
        report.append(f"- 总问题数：{self.total_questions}")
        report.append(f"- 总轮次数：{self.total_rounds}")
        
        # 最终排名
        report.append(f"\n## 最终排名")
        for i, (model_name, score) in enumerate(self.final_rankings):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "🏅"
            report.append(f"{i+1}. {medal} **{model_name}**: {score} 分")
        
        # 性能分析
        performance_analysis = self._analyze_performance()
        report.append(f"\n## 性能分析")
        report.append(f"- 平均得分：{performance_analysis['average_score']:.2f}")
        report.append(f"- 得分标准差：{performance_analysis['score_std']:.2f}")
        report.append(f"- 最高得分：{performance_analysis['max_score']}")
        report.append(f"- 最低得分：{performance_analysis['min_score']}")
        
        # 各模型表现分析
        model_analysis = self._analyze_model_performance()
        report.append(f"\n## 各模型详细表现")
        for model_name, stats in model_analysis.items():
            report.append(f"\n### {model_name}")
            report.append(f"- 总得分：{stats['total_score']}")
            report.append(f"- 平均单题得分：{stats['avg_score']:.2f}")
            report.append(f"- 最佳表现：{stats['best_performance']}")
            report.append(f"- 擅长领域：{', '.join(stats['strong_topics'])}")
            report.append(f"- 作为裁判的公正性评分：{stats['judge_fairness']:.2f}")
        
        # 问题难度分析
        topic_analysis = self._analyze_by_topic()
        report.append(f"\n## 问题主题分析")
        for topic, stats in topic_analysis.items():
            report.append(f"\n### {topic}")
            report.append(f"- 问题数量：{stats['count']}")
            report.append(f"- 平均得分：{stats['avg_score']:.2f}")
            report.append(f"- 表现最佳模型：{stats['best_model']}")
        
        return "\n".join(report)
    
    def _analyze_performance(self) -> Dict[str, float]:
        """分析整体性能"""
        scores = [score for _, score in self.final_rankings]
        return {
            'average_score': sum(scores) / len(scores) if scores else 0,
            'score_std': pd.Series(scores).std() if len(scores) > 1 else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0
        }
    
    def _analyze_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """分析各模型表现"""
        model_stats = {}
        
        # 初始化统计数据
        for model_name, total_score in self.final_rankings:
            model_stats[model_name] = {
                'total_score': total_score,
                'scores': [],
                'topics': defaultdict(list),
                'judge_scores': [],
                'best_performance': '',
                'strong_topics': []
            }
        
        # 收集详细数据
        for result in self.detailed_results:
            judge = result['judge']
            rankings = result['rankings']
            question = result['question']
            
            # 提取问题主题（简单方法）
            topic = self._extract_topic(question)
            
            for model_name, score in rankings:
                if model_name in model_stats:
                    model_stats[model_name]['scores'].append(score)
                    model_stats[model_name]['topics'][topic].append(score)
            
            # 分析裁判公正性（基于得分分布的方差）
            if judge in model_stats:
                scores = [score for _, score in rankings]
                score_variance = pd.Series(scores).var() if len(scores) > 1 else 0
                model_stats[judge]['judge_scores'].append(score_variance)
        
        # 计算统计指标
        for model_name, stats in model_stats.items():
            scores = stats['scores']
            stats['avg_score'] = sum(scores) / len(scores) if scores else 0
            
            # 找出最佳表现
            if scores:
                max_score_idx = scores.index(max(scores))
                stats['best_performance'] = f"第{max_score_idx + 1}题得分{max(scores)}"
            
            # 找出擅长领域
            topic_avgs = {}
            for topic, topic_scores in stats['topics'].items():
                if topic_scores:
                    topic_avgs[topic] = sum(topic_scores) / len(topic_scores)
            
            if topic_avgs:
                sorted_topics = sorted(topic_avgs.items(), key=lambda x: x[1], reverse=True)
                stats['strong_topics'] = [topic for topic, _ in sorted_topics[:2]]
            
            # 计算裁判公正性（方差越小越公正）
            judge_scores = stats['judge_scores']
            stats['judge_fairness'] = 10 - (sum(judge_scores) / len(judge_scores)) if judge_scores else 5
            stats['judge_fairness'] = max(0, min(10, stats['judge_fairness']))  # 限制在0-10范围
        
        return model_stats
    
    def _analyze_by_topic(self) -> Dict[str, Dict[str, Any]]:
        """按主题分析"""
        topic_stats = defaultdict(lambda: {
            'count': 0,
            'scores': [],
            'model_scores': defaultdict(list)
        })
        
        for result in self.detailed_results:
            question = result['question']
            rankings = result['rankings']
            topic = self._extract_topic(question)
            
            topic_stats[topic]['count'] += 1
            
            for model_name, score in rankings:
                topic_stats[topic]['scores'].append(score)
                topic_stats[topic]['model_scores'][model_name].append(score)
        
        # 计算统计指标
        final_topic_stats = {}
        for topic, stats in topic_stats.items():
            scores = stats['scores']
            model_scores = stats['model_scores']
            
            # 找出表现最佳的模型
            best_model = ''
            best_avg = 0
            for model_name, model_topic_scores in model_scores.items():
                if model_topic_scores:
                    avg_score = sum(model_topic_scores) / len(model_topic_scores)
                    if avg_score > best_avg:
                        best_avg = avg_score
                        best_model = model_name
            
            final_topic_stats[topic] = {
                'count': stats['count'],
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'best_model': best_model
            }
        
        return final_topic_stats
    
    def _extract_topic(self, question: str) -> str:
        """从问题中提取主题（简单的关键词匹配）"""
        topic_keywords = {
            '逻辑推理': ['推理', '逻辑', '推断', '判断'],
            '数学计算': ['计算', '数学', '方程', '几何', '证明'],
            '创意写作': ['写作', '创作', '文章', '故事', '诗歌'],
            '知识问答': ['解释', '分析', '什么是', '比较'],
            '编程算法': ['算法', '编程', '代码', '实现', '数据结构'],
            '系统设计': ['设计', '系统', '架构', '分布式'],
            '商业分析': ['商业', '策略', '分析', '市场', 'CEO']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in question for keyword in keywords):
                return topic
        
        return '其他'
    
    def generate_charts(self, output_dir: str = "./charts"):
        """生成图表"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 最终排名柱状图
        self._plot_final_rankings(output_dir)
        
        # 2. 各模型得分分布
        self._plot_score_distribution(output_dir)
        
        # 3. 主题表现热力图
        self._plot_topic_heatmap(output_dir)
        
        # 4. 裁判公正性分析
        self._plot_judge_fairness(output_dir)
    
    def _plot_final_rankings(self, output_dir: str):
        """绘制最终排名图"""
        models = [name for name, _ in self.final_rankings]
        scores = [score for _, score in self.final_rankings]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(models, scores, color=['gold', 'silver', '#CD7F32'] + ['skyblue'] * (len(models) - 3))
        plt.title('大模型竞技最终排名', fontsize=16, fontweight='bold')
        plt.xlabel('模型名称', fontsize=12)
        plt.ylabel('总得分', fontsize=12)
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(score), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/final_rankings.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_score_distribution(self, output_dir: str):
        """绘制得分分布图"""
        model_scores = defaultdict(list)
        
        for result in self.detailed_results:
            for model_name, score in result['rankings']:
                model_scores[model_name].append(score)
        
        plt.figure(figsize=(12, 8))
        
        for i, (model_name, scores) in enumerate(model_scores.items()):
            plt.subplot(2, 2, i + 1)
            plt.hist(scores, bins=10, alpha=0.7, color=f'C{i}')
            plt.title(f'{model_name} 得分分布')
            plt.xlabel('得分')
            plt.ylabel('频次')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/score_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_topic_heatmap(self, output_dir: str):
        """绘制主题表现热力图"""
        # 构建数据矩阵
        models = [name for name, _ in self.final_rankings]
        topics = set()
        model_topic_scores = defaultdict(lambda: defaultdict(list))
        
        for result in self.detailed_results:
            topic = self._extract_topic(result['question'])
            topics.add(topic)
            for model_name, score in result['rankings']:
                model_topic_scores[model_name][topic].append(score)
        
        topics = sorted(list(topics))
        
        # 计算平均得分矩阵
        score_matrix = []
        for model in models:
            model_row = []
            for topic in topics:
                scores = model_topic_scores[model][topic]
                avg_score = sum(scores) / len(scores) if scores else 0
                model_row.append(avg_score)
            score_matrix.append(model_row)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(score_matrix, 
                   xticklabels=topics, 
                   yticklabels=models,
                   annot=True, 
                   fmt='.1f', 
                   cmap='YlOrRd',
                   cbar_kws={'label': '平均得分'})
        plt.title('各模型在不同主题的表现热力图', fontsize=14, fontweight='bold')
        plt.xlabel('问题主题', fontsize=12)
        plt.ylabel('模型名称', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/topic_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_judge_fairness(self, output_dir: str):
        """绘制裁判公正性分析图"""
        judge_fairness = {}
        
        for result in self.detailed_results:
            judge = result['judge']
            rankings = result['rankings']
            scores = [score for _, score in rankings]
            
            # 计算得分方差作为公正性指标（方差越小越公正）
            score_variance = pd.Series(scores).var() if len(scores) > 1 else 0
            
            if judge not in judge_fairness:
                judge_fairness[judge] = []
            judge_fairness[judge].append(score_variance)
        
        # 计算平均公正性
        avg_fairness = {}
        for judge, variances in judge_fairness.items():
            avg_fairness[judge] = sum(variances) / len(variances)
        
        judges = list(avg_fairness.keys())
        fairness_scores = [10 - score for score in avg_fairness.values()]  # 转换为公正性得分
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(judges, fairness_scores, color='lightcoral')
        plt.title('各模型作为裁判的公正性评分', fontsize=14, fontweight='bold')
        plt.xlabel('裁判模型', fontsize=12)
        plt.ylabel('公正性得分 (0-10)', fontsize=12)
        plt.ylim(0, 10)
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for bar, score in zip(bars, fairness_scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/judge_fairness.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def export_detailed_data(self, filename: str = "detailed_analysis.xlsx"):
        """导出详细数据到Excel"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 最终排名
            ranking_df = pd.DataFrame(self.final_rankings, columns=['模型名称', '总得分'])
            ranking_df.to_excel(writer, sheet_name='最终排名', index=False)
            
            # 详细结果
            detailed_data = []
            for result in self.detailed_results:
                for model_name, score in result['rankings']:
                    detailed_data.append({
                        '问题ID': result['question_id'],
                        '问题内容': result['question'][:100] + '...',
                        '裁判模型': result['judge'],
                        '参赛模型': model_name,
                        '得分': score,
                        '主题': self._extract_topic(result['question'])
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='详细结果', index=False)
            
            # 模型表现统计
            model_stats = self._analyze_model_performance()
            stats_data = []
            for model_name, stats in model_stats.items():
                stats_data.append({
                    '模型名称': model_name,
                    '总得分': stats['total_score'],
                    '平均得分': stats['avg_score'],
                    '裁判公正性': stats['judge_fairness'],
                    '擅长领域': ', '.join(stats['strong_topics'])
                })
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='模型统计', index=False)

def analyze_competition_results(result_file: str = "competition_results.json"):
    """分析竞技结果的主函数"""
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        analyzer = ResultAnalyzer(result_data)
        
        # 生成报告
        report = analyzer.generate_summary_report()
        with open("competition_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 生成图表
        analyzer.generate_charts()
        
        # 导出详细数据
        analyzer.export_detailed_data()
        
        print("分析完成！生成的文件：")
        print("- competition_report.md: 详细分析报告")
        print("- charts/: 图表文件夹")
        print("- detailed_analysis.xlsx: 详细数据表格")
        
        return analyzer
        
    except FileNotFoundError:
        print(f"错误：找不到结果文件 {result_file}")
        return None
    except Exception as e:
        print(f"分析过程中出现错误：{e}")
        return None

if __name__ == "__main__":
    analyze_competition_results()