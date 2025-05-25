# 🤖 LLM1566：大模型竞技系统
> 让英雄去查英雄，让好汉去查好汉

一个创新的大模型评测和竞技平台，通过轮流裁判机制实现公平、全面的模型能力评估。

## ✨ 特性

- 🏆 **轮流裁判机制**: 每个模型都有机会当裁判和参赛选手，确保评测公平性
- 🎯 **多维度评测**: 支持逻辑推理、数学计算、创意写作、知识问答、编程算法等多个领域
- 🔌 **多平台支持**: 兼容 OpenAI、Anthropic、Google、阿里云等主流大模型API
- 📊 **详细分析**: 提供丰富的统计分析和可视化报告
- 🎮 **交互式界面**: 友好的命令行界面，支持配置管理和实时监控
- 📚 **丰富题库**: 内置多种类型和难度的问题，支持自定义扩展

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置模型

运行配置向导：
```bash
python cli.py config --setup
```

或直接编辑 `config.json` 文件：
```json
{
  "models": [
    {
      "name": "GPT-4",
      "api_key": "your_openai_api_key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4",
      "provider": "openai"
    }
  ]
}
```

### 3. 运行竞技

```bash
# 交互式运行
python cli.py run

# 自动运行
python cli.py run --auto

# 或直接运行主程序
python llm_competition.py
```

### 4. 查看结果

```bash
# 生成分析报告
python cli.py analyze

# 或直接分析
python result_analyzer.py
```

## 📁 项目结构

```
LLM1566/
├── llm_competition.py    # 主竞技逻辑
├── model_api.py         # 大模型API调用
├── question_bank.py     # 问题库管理
├── result_analyzer.py   # 结果分析和可视化
├── cli.py              # 命令行界面
├── config.json         # 配置文件
├── requirements.txt    # 依赖包列表
└── README.md          # 项目说明
```

## 🎯 使用指南

### 命令行界面

```bash
# 查看帮助
python cli.py --help

# 运行竞技
python cli.py run [--auto] [--models N] [--questions N]

# 配置管理
python cli.py config [--setup]

# 问题库管理
python cli.py questions [--list]

# 结果分析
python cli.py analyze [--file results.json]

# 演示模式
python cli.py demo
```

### 交互式模式

直接运行 `python cli.py` 进入交互式模式，支持以下命令：
- `run` - 运行竞技
- `config` - 配置管理
- `questions` - 问题库管理
- `analyze` - 结果分析
- `demo` - 演示模式
- `help` - 帮助信息
- `exit` - 退出程序

## 🔧 配置说明

### 模型配置

支持以下大模型提供商：

#### OpenAI
```json
{
  "name": "GPT-4",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4",
  "provider": "openai"
}
```

#### Anthropic Claude
```json
{
  "name": "Claude-3",
  "api_key": "sk-ant-...",
  "base_url": "https://api.anthropic.com",
  "model": "claude-3-opus-20240229",
  "provider": "anthropic"
}
```

#### Google Gemini
```json
{
  "name": "Gemini-Pro",
  "api_key": "AIza...",
  "base_url": "https://generativelanguage.googleapis.com/v1",
  "model": "gemini-pro",
  "provider": "google"
}
```

#### 阿里云通义千问
```json
{
  "name": "通义千问",
  "api_key": "sk-...",
  "base_url": "https://dashscope.aliyuncs.com/api/v1",
  "model": "qwen-max",
  "provider": "dashscope"
}
```

### 竞技设置

```json
{
  "competition_settings": {
    "min_models": 3,
    "question_generation": {
      "enabled": true,
      "count": 10,
      "difficulty": "medium",
      "topics": ["逻辑推理", "数学计算", "创意写作"]
    },
    "scoring": {
      "first_place": 3,
      "second_place": 2,
      "third_place": 1,
      "other_place": 0
    }
  }
}
```

## 📊 结果分析

系统会生成以下分析文件：

- `competition_results.json` - 原始竞技结果
- `competition_report.md` - 详细分析报告
- `detailed_analysis.xlsx` - Excel格式的详细数据
- `charts/` - 可视化图表文件夹
  - `final_rankings.png` - 最终排名图
  - `score_distribution.png` - 得分分布图
  - `topic_heatmap.png` - 主题表现热力图
  - `judge_fairness.png` - 裁判公正性分析图

## 🎮 竞技机制

### 轮流裁判制度

1. **问题准备**: 从题库选择或AI生成问题
2. **轮流裁判**: 每个问题，所有模型轮流当裁判
3. **参赛回答**: 非裁判模型回答问题
4. **裁判评分**: 裁判模型对所有答案进行评分排名
5. **积分统计**: 根据排名给予相应积分
6. **最终排名**: 所有问题完成后统计总分

### 评分规则

- 🥇 第一名: 3分
- 🥈 第二名: 2分
- 🥉 第三名: 1分
- 其他: 0分

## 🧪 问题类型

内置问题库包含以下类型：

- 🧠 **逻辑推理**: 逻辑谜题、推理问题
- 🔢 **数学计算**: 代数、几何、证明题
- ✍️ **创意写作**: 故事创作、诗歌、角色设计
- 📚 **知识问答**: 科技、历史、文化知识
- 💻 **编程算法**: 算法设计、代码实现
- 🏗️ **系统设计**: 架构设计、技术方案
- 💼 **商业分析**: 战略分析、商业模式

每种类型都有 easy、medium、hard 三个难度等级。

## 🔍 高级功能

### 自定义问题

```python
from question_bank import Question, QuestionBank

# 添加自定义问题
bank = QuestionBank()
custom_question = Question(
    id=0,
    content="你的问题内容",
    topic="问题主题",
    difficulty="medium"
)
bank.add_question(custom_question)
```

### 扩展API支持

在 `model_api.py` 中添加新的提供商支持：

```python
async def _call_custom_provider(self, config: ModelConfig, prompt: str, **kwargs) -> str:
    # 实现自定义API调用逻辑
    pass
```

## 🤝 贡献指南

欢迎贡献代码、问题或建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 注意事项

1. **API密钥安全**: 请妥善保管API密钥，不要提交到版本控制系统
2. **费用控制**: 大模型API调用会产生费用，请注意控制使用量
3. **网络要求**: 需要稳定的网络连接访问各大模型API
4. **Python版本**: 建议使用 Python 3.8 或更高版本

## 🆘 常见问题

### Q: 如何添加新的大模型？
A: 在 `config.json` 中添加模型配置，如果是新的提供商，需要在 `model_api.py` 中实现相应的API调用方法。

### Q: 可以自定义评分规则吗？
A: 可以在 `config.json` 的 `scoring` 部分修改评分规则。

### Q: 如何增加问题数量？
A: 可以在 `question_bank.py` 中添加更多问题，或者启用AI生成问题功能。

### Q: 结果分析图表显示乱码怎么办？
A: 确保系统安装了中文字体，或在 `result_analyzer.py` 中修改字体设置。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发起 Discussion
- 邮件联系项目维护者

---

**让AI模型在公平的竞技场上展现真实实力！** 🚀
