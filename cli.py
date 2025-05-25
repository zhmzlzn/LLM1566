#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行界面
提供用户友好的交互式界面来运行大模型竞技
"""

import argparse
import asyncio
import json
import sys
from typing import List, Dict, Any
from llm_competition import LLMCompetition
from result_analyzer import analyze_competition_results
from question_bank import QuestionBank

def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 大模型竞技系统 🏆                      ║
║                  LLM Competition Platform                    ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_help():
    """打印帮助信息"""
    help_text = """
可用命令：
  run          - 运行完整的竞技流程
  config       - 查看或编辑配置
  questions    - 管理问题库
  analyze      - 分析竞技结果
  demo         - 运行演示模式
  help         - 显示帮助信息
  exit         - 退出程序

使用示例：
  python cli.py run --models 4 --questions 5
  python cli.py analyze --file results.json
  python cli.py questions --list
"""
    print(help_text)

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件 {config_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"❌ 配置文件 {config_path} 格式错误")
        return None

def save_config(config: Dict[str, Any], config_path: str = "config.json"):
    """保存配置文件"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✅ 配置已保存到 {config_path}")
    except Exception as e:
        print(f"❌ 保存配置失败：{e}")

def interactive_config_setup():
    """交互式配置设置"""
    print("\n🔧 配置设置向导")
    print("=" * 50)
    
    config = load_config()
    if not config:
        print("创建新的配置文件...")
        config = {
            "models": [],
            "competition_settings": {
                "min_models": 3,
                "question_generation": {
                    "enabled": True,
                    "count": 5,
                    "difficulty": "medium",
                    "topics": []
                },
                "scoring": {
                    "first_place": 3,
                    "second_place": 2,
                    "third_place": 1,
                    "other_place": 0
                }
            }
        }
    
    # 配置模型
    print("\n📋 当前配置的模型：")
    for i, model in enumerate(config['models']):
        print(f"  {i+1}. {model['name']} ({model['provider']})")
    
    while True:
        action = input("\n选择操作 [添加模型(a)/删除模型(d)/修改设置(s)/完成(f)]: ").lower()
        
        if action == 'a':
            add_model_interactive(config)
        elif action == 'd':
            remove_model_interactive(config)
        elif action == 's':
            modify_settings_interactive(config)
        elif action == 'f':
            break
        else:
            print("❌ 无效选择，请重试")
    
    save_config(config)
    return config

def add_model_interactive(config: Dict[str, Any]):
    """交互式添加模型"""
    print("\n➕ 添加新模型")
    
    name = input("模型名称: ")
    if not name:
        print("❌ 模型名称不能为空")
        return
    
    providers = ["openai", "anthropic", "google", "dashscope", "其他"]
    print("\n可选提供商:")
    for i, provider in enumerate(providers):
        print(f"  {i+1}. {provider}")
    
    try:
        provider_idx = int(input("选择提供商 (1-5): ")) - 1
        if provider_idx < 0 or provider_idx >= len(providers):
            raise ValueError()
        provider = providers[provider_idx]
    except ValueError:
        print("❌ 无效选择")
        return
    
    if provider == "其他":
        provider = input("请输入自定义提供商名称: ")
    
    api_key = input("API Key: ")
    base_url = input("Base URL: ")
    model = input("模型名称 (如 gpt-4, claude-3-opus): ")
    
    new_model = {
        "name": name,
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "provider": provider
    }
    
    config['models'].append(new_model)
    print(f"✅ 已添加模型: {name}")

def remove_model_interactive(config: Dict[str, Any]):
    """交互式删除模型"""
    if not config['models']:
        print("❌ 没有可删除的模型")
        return
    
    print("\n🗑️ 删除模型")
    for i, model in enumerate(config['models']):
        print(f"  {i+1}. {model['name']}")
    
    try:
        idx = int(input("选择要删除的模型 (输入序号): ")) - 1
        if idx < 0 or idx >= len(config['models']):
            raise ValueError()
        
        removed_model = config['models'].pop(idx)
        print(f"✅ 已删除模型: {removed_model['name']}")
    except ValueError:
        print("❌ 无效选择")

def modify_settings_interactive(config: Dict[str, Any]):
    """交互式修改设置"""
    print("\n⚙️ 修改竞技设置")
    settings = config['competition_settings']
    
    print(f"\n当前设置:")
    print(f"  最少模型数: {settings['min_models']}")
    print(f"  问题数量: {settings['question_generation']['count']}")
    print(f"  问题难度: {settings['question_generation']['difficulty']}")
    print(f"  问题主题: {', '.join(settings['question_generation']['topics']) if settings['question_generation']['topics'] else '全部'}")
    
    if input("\n是否修改最少模型数? (y/n): ").lower() == 'y':
        try:
            min_models = int(input(f"新的最少模型数 (当前: {settings['min_models']}): "))
            if min_models >= 3:
                settings['min_models'] = min_models
                print("✅ 已更新")
            else:
                print("❌ 最少模型数必须大于等于3")
        except ValueError:
            print("❌ 请输入有效数字")
    
    if input("是否修改问题数量? (y/n): ").lower() == 'y':
        try:
            count = int(input(f"新的问题数量 (当前: {settings['question_generation']['count']}): "))
            if count > 0:
                settings['question_generation']['count'] = count
                print("✅ 已更新")
            else:
                print("❌ 问题数量必须大于0")
        except ValueError:
            print("❌ 请输入有效数字")
    
    if input("是否修改问题难度? (y/n): ").lower() == 'y':
        difficulties = ["easy", "medium", "hard"]
        print("可选难度:")
        for i, diff in enumerate(difficulties):
            print(f"  {i+1}. {diff}")
        
        try:
            diff_idx = int(input("选择难度 (1-3): ")) - 1
            if 0 <= diff_idx < len(difficulties):
                settings['question_generation']['difficulty'] = difficulties[diff_idx]
                print("✅ 已更新")
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入有效数字")

async def run_competition_interactive(args):
    """交互式运行竞技"""
    print("\n🚀 启动大模型竞技")
    print("=" * 50)
    
    # 检查配置
    config = load_config()
    if not config:
        print("❌ 请先配置模型信息")
        return
    
    # 创建竞技实例
    try:
        competition = LLMCompetition()
        
        # 验证设置
        if not competition.validate_setup():
            print("❌ 设置验证失败，请检查配置")
            return
        
        print("\n📝 准备开始竞技...")
        print(f"参赛模型: {[model.name for model in competition.models]}")
        
        if not args or args.auto:
            confirm = input("\n确认开始竞技? (y/n): ")
            if confirm.lower() != 'y':
                print("❌ 竞技已取消")
                return
        
        # 运行竞技
        print("\n🏁 竞技开始！")
        result = await competition.run_competition()
        
        if 'error' in result:
            print(f"❌ 竞技失败: {result['error']}")
            return
        
        # 显示结果
        print("\n🏆 竞技结果")
        print("=" * 30)
        for i, (model_name, score) in enumerate(result['final_rankings']):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "🏅"
            print(f"{i+1}. {medal} {model_name}: {score} 分")
        
        # 保存结果
        competition.save_results()
        print("\n💾 结果已保存到 competition_results.json")
        
        # 询问是否生成分析报告
        if input("\n是否生成详细分析报告? (y/n): ").lower() == 'y':
            print("\n📊 生成分析报告...")
            analyze_competition_results()
            print("✅ 分析报告生成完成")
        
    except Exception as e:
        print(f"❌ 运行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def manage_questions_interactive(args):
    """交互式管理问题库"""
    print("\n📚 问题库管理")
    print("=" * 50)
    
    bank = QuestionBank()
    
    if args and args.list:
        # 列出所有问题
        stats = bank.get_statistics()
        print(f"\n📊 问题库统计:")
        print(f"总问题数: {stats['total_questions']}")
        print(f"主题分布: {stats['topics']}")
        print(f"难度分布: {stats['difficulties']}")
        
        print("\n📋 所有问题:")
        for question in bank.questions:
            print(f"{question.id}. [{question.topic}] [{question.difficulty}] {question.content[:80]}...")
        return
    
    while True:
        print("\n选择操作:")
        print("1. 查看问题统计")
        print("2. 按主题查看问题")
        print("3. 按难度查看问题")
        print("4. 随机获取问题")
        print("5. 添加新问题")
        print("6. 返回主菜单")
        
        choice = input("\n请选择 (1-6): ")
        
        if choice == '1':
            stats = bank.get_statistics()
            print(f"\n📊 问题库统计:")
            print(f"总问题数: {stats['total_questions']}")
            print(f"主题分布: {stats['topics']}")
            print(f"难度分布: {stats['difficulties']}")
        
        elif choice == '2':
            topics = bank.get_all_topics()
            print("\n可用主题:")
            for i, topic in enumerate(topics):
                print(f"  {i+1}. {topic}")
            
            try:
                topic_idx = int(input("选择主题 (输入序号): ")) - 1
                if 0 <= topic_idx < len(topics):
                    selected_topic = topics[topic_idx]
                    questions = bank.get_questions_by_topic(selected_topic)
                    print(f"\n📋 {selected_topic} 相关问题:")
                    for q in questions:
                        print(f"{q.id}. [{q.difficulty}] {q.content[:80]}...")
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效数字")
        
        elif choice == '3':
            difficulties = bank.get_all_difficulties()
            print("\n可用难度:")
            for i, diff in enumerate(difficulties):
                print(f"  {i+1}. {diff}")
            
            try:
                diff_idx = int(input("选择难度 (输入序号): ")) - 1
                if 0 <= diff_idx < len(difficulties):
                    selected_diff = difficulties[diff_idx]
                    questions = bank.get_questions_by_difficulty(selected_diff)
                    print(f"\n📋 {selected_diff} 难度问题:")
                    for q in questions:
                        print(f"{q.id}. [{q.topic}] {q.content[:80]}...")
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效数字")
        
        elif choice == '4':
            try:
                count = int(input("获取问题数量: "))
                questions = bank.get_random_questions(count)
                print(f"\n🎲 随机获取的 {len(questions)} 个问题:")
                for q in questions:
                    print(f"{q.id}. [{q.topic}] [{q.difficulty}] {q.content[:80]}...")
            except ValueError:
                print("❌ 请输入有效数字")
        
        elif choice == '5':
            print("\n➕ 添加新问题")
            content = input("问题内容: ")
            topic = input("问题主题: ")
            difficulty = input("问题难度 (easy/medium/hard): ")
            
            if content and topic and difficulty in ['easy', 'medium', 'hard']:
                from question_bank import Question
                new_question = Question(0, content, topic, difficulty)
                bank.add_question(new_question)
                print("✅ 问题已添加")
            else:
                print("❌ 请填写完整信息")
        
        elif choice == '6':
            break
        
        else:
            print("❌ 无效选择")

def run_demo_mode():
    """运行演示模式"""
    print("\n🎭 演示模式")
    print("=" * 50)
    print("演示模式将使用模拟数据运行一个简化的竞技流程")
    
    # 这里可以实现一个简化的演示
    print("\n📝 模拟竞技流程:")
    print("1. ✅ 加载配置文件")
    print("2. ✅ 验证模型设置")
    print("3. ✅ 生成测试问题")
    print("4. ✅ 模拟模型回答")
    print("5. ✅ 模拟裁判评分")
    print("6. ✅ 计算最终排名")
    
    print("\n🏆 模拟结果:")
    print("1. 🥇 GPT-4: 15 分")
    print("2. 🥈 Claude-3: 12 分")
    print("3. 🥉 Gemini-Pro: 10 分")
    print("4. 🏅 通义千问: 8 分")
    
    print("\n💡 提示: 配置真实的API密钥后可运行完整竞技")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='大模型竞技系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='运行竞技')
    run_parser.add_argument('--auto', action='store_true', help='自动运行，不询问确认')
    run_parser.add_argument('--models', type=int, help='参赛模型数量')
    run_parser.add_argument('--questions', type=int, help='问题数量')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('--setup', action='store_true', help='交互式配置设置')
    
    # questions 命令
    questions_parser = subparsers.add_parser('questions', help='问题库管理')
    questions_parser.add_argument('--list', action='store_true', help='列出所有问题')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析结果')
    analyze_parser.add_argument('--file', default='competition_results.json', help='结果文件路径')
    
    # demo 命令
    demo_parser = subparsers.add_parser('demo', help='演示模式')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == 'run':
        asyncio.run(run_competition_interactive(args))
    elif args.command == 'config':
        if args.setup:
            interactive_config_setup()
        else:
            config = load_config()
            if config:
                print("\n📋 当前配置:")
                print(json.dumps(config, ensure_ascii=False, indent=2))
    elif args.command == 'questions':
        manage_questions_interactive(args)
    elif args.command == 'analyze':
        print(f"\n📊 分析结果文件: {args.file}")
        analyze_competition_results(args.file)
    elif args.command == 'demo':
        run_demo_mode()
    else:
        # 交互式模式
        print("\n🎯 欢迎使用大模型竞技系统！")
        print("输入 'help' 查看可用命令")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'help':
                    print_help()
                elif command == 'run':
                    asyncio.run(run_competition_interactive(None))
                elif command == 'config':
                    interactive_config_setup()
                elif command == 'questions':
                    manage_questions_interactive(None)
                elif command == 'analyze':
                    analyze_competition_results()
                elif command == 'demo':
                    run_demo_mode()
                elif command in ['exit', 'quit', 'q']:
                    print("👋 再见！")
                    break
                else:
                    print("❌ 未知命令，输入 'help' 查看帮助")
            
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()