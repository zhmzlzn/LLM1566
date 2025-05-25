# 🔌 API使用指南

本文档介绍如何通过编程方式使用大模型竞技系统的各个组件。

## 📚 核心模块

### 1. 在线竞技系统 (OnlineCompetitionSystem)

```python
from gradio_app import OnlineCompetitionSystem

# 初始化系统
system = OnlineCompetitionSystem("config.json")

# 处理单个问题
result = await system.process_question("什么是人工智能？")
print(result)

# 结果格式
{
    'success': True,
    'judge': '裁判模型名称',
    'answers': {'模型1': '回答1', '模型2': '回答2'},
    'rankings': [('模型1', 1), ('模型2', 2)],
    'reasoning': '评判理由',
    'timestamp': '2024-01-01 12:00:00'
}
```

### 2. 数据库管理 (OnlineCompetitionDB)

```python
from gradio_app import OnlineCompetitionDB

# 初始化数据库
db = OnlineCompetitionDB("competition.db")

# 添加问答记录
record_id = db.add_qa_record(
    question="测试问题",
    judge_model="GPT-4",
    participant_models=["Claude-3", "Gemini-Pro"],
    answers={"Claude-3": "回答1", "Gemini-Pro": "回答2"},
    rankings=[("Claude-3", 1), ("Gemini-Pro", 2)],
    judge_reasoning="评判理由"
)

# 更新模型得分
db.update_model_scores([("Claude-3", 1), ("Gemini-Pro", 2)], record_id)

# 获取排行榜
rankings = db.get_model_rankings()
print(rankings)

# 获取最近记录
recent = db.get_recent_qa_records(5)
print(recent)

# 获取统计信息
stats = db.get_statistics()
print(stats)
```

### 3. 批量竞技系统 (LLMCompetition)

```python
from llm_competition import LLMCompetition

# 初始化竞技系统
competition = LLMCompetition("config.json")

# 运行完整竞技
result = await competition.run_competition()
print(result)

# 自定义问题竞技
custom_questions = [
    "解释量子计算的基本原理",
    "写一首关于春天的诗",
    "计算斐波那契数列的第20项"
]

result = await competition.run_competition(custom_questions=custom_questions)
print(result)
```

### 4. 模型API客户端 (ModelAPIClient)

```python
from model_api import ModelAPIClient, ModelConfig

# 创建模型配置
model_config = ModelConfig(
    name="GPT-4",
    api_key="your_api_key",
    base_url="https://api.openai.com/v1",
    model="gpt-4",
    provider="openai"
)

# 初始化API客户端
client = ModelAPIClient()

# 调用模型
response = await client.call_model(model_config, "你好，请介绍一下自己")
print(response)
```

### 5. 问题库管理 (QuestionBank)

```python
from question_bank import QuestionBank, Question

# 初始化问题库
bank = QuestionBank()

# 获取随机问题
questions = bank.get_random_questions(5, difficulty="medium")
for q in questions:
    print(f"{q.topic}: {q.question}")

# 按主题获取问题
logic_questions = bank.get_questions_by_topic("逻辑推理")
print(f"逻辑推理问题数量: {len(logic_questions)}")

# 添加自定义问题
custom_question = Question(
    id=999,
    question="什么是深度学习？",
    topic="人工智能",
    difficulty="easy",
    expected_answer="深度学习是机器学习的一个分支..."
)
bank.add_question(custom_question)

# 获取统计信息
stats = bank.get_statistics()
print(stats)
```

### 6. 结果分析器 (ResultAnalyzer)

```python
from result_analyzer import ResultAnalyzer

# 假设有竞技结果
result_data = {
    "final_rankings": [("GPT-4", 15), ("Claude-3", 12)],
    "total_questions": 5,
    "detailed_results": [...]
}

# 初始化分析器
analyzer = ResultAnalyzer(result_data)

# 生成报告
report = analyzer.generate_summary_report()
print(report)

# 生成图表
analyzer.create_visualizations("./charts/")

# 导出Excel
analyzer.export_to_excel("competition_results.xlsx")
```

## 🔧 高级用法

### 自定义评分规则

```python
# 修改配置文件中的评分规则
config = {
    "competition_settings": {
        "scoring": {
            "first_place": 5,    # 第一名5分
            "second_place": 3,   # 第二名3分
            "third_place": 1,    # 第三名1分
            "other_place": 0     # 其他0分
        }
    }
}
```

### 批量处理问题

```python
async def batch_process_questions(questions_list):
    system = OnlineCompetitionSystem()
    results = []
    
    for question in questions_list:
        result = await system.process_question(question)
        results.append(result)
        
        # 添加延迟避免API限制
        await asyncio.sleep(1)
    
    return results

# 使用示例
questions = [
    "什么是机器学习？",
    "解释区块链技术",
    "描述量子计算的优势"
]

results = await batch_process_questions(questions)
```

### 数据导出和分析

```python
import pandas as pd
from gradio_app import OnlineCompetitionDB

# 连接数据库
db = OnlineCompetitionDB()

# 导出所有数据
rankings = db.get_model_rankings()
records = db.get_recent_qa_records(100)  # 获取最近100条记录

# 转换为DataFrame进行分析
df_rankings = pd.DataFrame(rankings)
df_records = pd.DataFrame(records)

# 分析模型表现
print("平均得分最高的模型:")
print(df_rankings.nlargest(1, 'avg_score'))

# 分析问题类型分布
print("\n最近问题的长度分布:")
df_records['question_length'] = df_records['question'].str.len()
print(df_records['question_length'].describe())
```

### 实时监控

```python
import time
from gradio_app import OnlineCompetitionDB

def monitor_system():
    db = OnlineCompetitionDB()
    
    while True:
        stats = db.get_statistics()
        rankings = db.get_model_rankings()
        
        print(f"\n=== 系统状态 {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"总问题数: {stats['total_questions']}")
        print(f"参与模型数: {stats['total_models']}")
        
        if rankings:
            print(f"当前排名第一: {rankings[0]['model_name']} ({rankings[0]['total_score']}分)")
        
        time.sleep(60)  # 每分钟检查一次

# 在后台运行监控
# monitor_system()
```

## 🚨 注意事项

1. **API限制**: 注意各个模型提供商的API调用限制
2. **异步处理**: 大部分API调用都是异步的，需要使用`await`
3. **错误处理**: 建议在生产环境中添加完善的错误处理
4. **数据备份**: 定期备份SQLite数据库文件
5. **配置安全**: 不要在代码中硬编码API密钥

## 📞 技术支持

如果在使用过程中遇到问题，请：

1. 查看系统日志
2. 运行 `python test_system.py` 进行诊断
3. 检查配置文件格式
4. 确认API密钥有效性