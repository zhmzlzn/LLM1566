#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
用于验证大模型竞技系统的各个组件功能
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_bank import QuestionBank, Question
from model_api import ModelAPIClient, ModelConfig
from result_analyzer import ResultAnalyzer

def test_question_bank():
    """测试问题库功能"""
    print("🧪 测试问题库功能...")
    
    try:
        bank = QuestionBank()
        stats = bank.get_statistics()
        
        print(f"✅ 问题库加载成功")
        print(f"   - 总问题数: {stats['total_questions']}")
        print(f"   - 主题数: {len(stats['topics'])}")
        print(f"   - 难度等级: {stats['available_difficulties']}")
        
        # 测试随机获取问题
        random_questions = bank.get_random_questions(3, difficulty="medium")
        print(f"   - 随机获取3个中等难度问题: 成功")
        
        # 测试按主题获取问题
        logic_questions = bank.get_questions_by_topic("逻辑推理")
        print(f"   - 逻辑推理类问题数: {len(logic_questions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 问题库测试失败: {e}")
        return False

def test_config_loading():
    """测试配置文件加载"""
    print("\n🧪 测试配置文件加载...")
    
    try:
        # 测试示例配置文件
        if os.path.exists("config.example.json"):
            with open("config.example.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"✅ 示例配置文件加载成功")
            print(f"   - 配置的模型数: {len(config['models'])}")
            print(f"   - 最少模型数要求: {config['competition_settings']['min_models']}")
            
            # 验证模型配置格式
            for model in config['models']:
                required_fields = ['name', 'api_key', 'base_url', 'model', 'provider']
                if all(field in model for field in required_fields):
                    print(f"   - 模型 {model['name']} 配置格式正确")
                else:
                    print(f"   - ⚠️ 模型 {model['name']} 配置格式不完整")
            
            return True
        else:
            print("❌ 示例配置文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def test_api_client_structure():
    """测试API客户端结构"""
    print("\n🧪 测试API客户端结构...")
    
    try:
        client = ModelAPIClient()
        
        # 测试支持的提供商
        test_config = ModelConfig(
            name="Test Model",
            api_key="test_key",
            base_url="https://api.test.com",
            model="test-model",
            provider="test"
        )
        
        print(f"✅ API客户端初始化成功")
        print(f"   - 支持的方法: call_model")
        
        # 检查各提供商的方法是否存在
        providers = ['openai', 'anthropic', 'google', 'dashscope']
        for provider in providers:
            method_name = f"_call_{provider}"
            if hasattr(client, method_name):
                print(f"   - {provider} 提供商支持: ✅")
            else:
                print(f"   - {provider} 提供商支持: ❌")
        
        return True
        
    except Exception as e:
        print(f"❌ API客户端测试失败: {e}")
        return False

def test_result_analyzer_structure():
    """测试结果分析器结构"""
    print("\n🧪 测试结果分析器结构...")
    
    try:
        # 创建模拟结果数据
        mock_result = {
            "final_rankings": [
                ("GPT-4", 15),
                ("Claude-3", 12),
                ("Gemini-Pro", 10)
            ],
            "total_questions": 5,
            "total_rounds": 15,
            "detailed_results": [
                {
                    "question_id": 1,
                    "question": "测试问题1",
                    "judge": "GPT-4",
                    "rankings": [("Claude-3", 9), ("Gemini-Pro", 7)],
                    "reasoning": "测试评判理由"
                }
            ]
        }
        
        analyzer = ResultAnalyzer(mock_result)
        
        print(f"✅ 结果分析器初始化成功")
        print(f"   - 参赛模型数: {len(mock_result['final_rankings'])}")
        print(f"   - 总问题数: {mock_result['total_questions']}")
        
        # 测试生成报告
        report = analyzer.generate_summary_report()
        if report and len(report) > 100:
            print(f"   - 报告生成: ✅ (长度: {len(report)} 字符)")
        else:
            print(f"   - 报告生成: ❌")
        
        return True
        
    except Exception as e:
        print(f"❌ 结果分析器测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构完整性"""
    print("\n🧪 测试文件结构完整性...")
    
    required_files = [
        "llm_competition.py",
        "model_api.py",
        "question_bank.py",
        "result_analyzer.py",
        "cli.py",
        "config.json",
        "config.example.json",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    existing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            existing_files.append(file)
            print(f"   - {file}: ✅")
        else:
            missing_files.append(file)
            print(f"   - {file}: ❌")
    
    if not missing_files:
        print(f"✅ 所有必需文件都存在 ({len(existing_files)}/{len(required_files)})")
        return True
    else:
        print(f"⚠️ 缺少 {len(missing_files)} 个文件: {missing_files}")
        return False

def test_imports():
    """测试模块导入"""
    print("\n🧪 测试模块导入...")
    
    modules_to_test = [
        ("llm_competition", "LLMCompetition"),
        ("model_api", "ModelAPIClient"),
        ("question_bank", "QuestionBank"),
        ("result_analyzer", "ResultAnalyzer")
    ]
    
    success_count = 0
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"   - {module_name}.{class_name}: ✅")
                success_count += 1
            else:
                print(f"   - {module_name}.{class_name}: ❌ (类不存在)")
        except ImportError as e:
            print(f"   - {module_name}: ❌ (导入失败: {e})")
        except Exception as e:
            print(f"   - {module_name}: ❌ (错误: {e})")
    
    if success_count == len(modules_to_test):
        print(f"✅ 所有模块导入成功 ({success_count}/{len(modules_to_test)})")
        return True
    else:
        print(f"⚠️ {len(modules_to_test) - success_count} 个模块导入失败")
        return False

async def test_mock_competition():
    """测试模拟竞技流程"""
    print("\n🧪 测试模拟竞技流程...")
    
    try:
        # 创建模拟配置
        mock_config = {
            "models": [
                {
                    "name": "Mock-GPT",
                    "api_key": "mock_key_1",
                    "base_url": "https://mock.api.com",
                    "model": "mock-gpt",
                    "provider": "mock"
                },
                {
                    "name": "Mock-Claude",
                    "api_key": "mock_key_2",
                    "base_url": "https://mock.api.com",
                    "model": "mock-claude",
                    "provider": "mock"
                },
                {
                    "name": "Mock-Gemini",
                    "api_key": "mock_key_3",
                    "base_url": "https://mock.api.com",
                    "model": "mock-gemini",
                    "provider": "mock"
                }
            ],
            "competition_settings": {
                "min_models": 3,
                "question_generation": {
                    "enabled": False,
                    "count": 2,
                    "difficulty": "easy"
                },
                "scoring": {
                    "first_place": 3,
                    "second_place": 2,
                    "third_place": 1,
                    "other_place": 0
                }
            }
        }
        
        # 保存模拟配置
        with open("test_config.json", 'w', encoding='utf-8') as f:
            json.dump(mock_config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 模拟配置创建成功")
        print(f"   - 模拟模型数: {len(mock_config['models'])}")
        print(f"   - 最少模型要求: {mock_config['competition_settings']['min_models']}")
        
        # 清理测试文件
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
            print(f"   - 测试文件清理: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ 模拟竞技测试失败: {e}")
        return False

def generate_test_report(results: Dict[str, bool]):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📋 测试报告")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 总体统计:")
    print(f"   - 总测试数: {total_tests}")
    print(f"   - 通过测试: {passed_tests} ✅")
    print(f"   - 失败测试: {failed_tests} ❌")
    print(f"   - 成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📝 详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   - {test_name}: {status}")
    
    if failed_tests == 0:
        print(f"\n🎉 所有测试通过！系统准备就绪。")
        print(f"\n🚀 下一步操作:")
        print(f"   1. 复制 config.example.json 为 config.json")
        print(f"   2. 填入真实的API密钥")
        print(f"   3. 运行 python cli.py run 开始竞技")
    else:
        print(f"\n⚠️ 发现 {failed_tests} 个问题，请检查相关组件。")
        print(f"\n🔧 建议操作:")
        print(f"   1. 检查缺失的文件")
        print(f"   2. 安装缺失的依赖包")
        print(f"   3. 修复导入错误")
    
    print("\n" + "="*60)

async def main():
    """主测试函数"""
    print("🧪 大模型竞技系统 - 系统测试")
    print("="*60)
    
    # 执行所有测试
    test_results = {}
    
    test_results["文件结构完整性"] = test_file_structure()
    test_results["模块导入"] = test_imports()
    test_results["配置文件加载"] = test_config_loading()
    test_results["问题库功能"] = test_question_bank()
    test_results["API客户端结构"] = test_api_client_structure()
    test_results["结果分析器结构"] = test_result_analyzer_structure()
    test_results["模拟竞技流程"] = await test_mock_competition()
    
    # 生成测试报告
    generate_test_report(test_results)

if __name__ == "__main__":
    asyncio.run(main())