#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Gradio在线竞技系统
"""

import os
import sys
import json
from pathlib import Path

def check_config():
    """检查配置文件"""
    config_path = "config.json"
    example_config_path = "config.example.json"
    
    if not os.path.exists(config_path):
        if os.path.exists(example_config_path):
            print("⚠️ 未找到config.json，正在从config.example.json复制...")
            import shutil
            shutil.copy(example_config_path, config_path)
            print("✅ 配置文件已复制")
            print("🔧 请编辑config.json文件，填入真实的API密钥")
            return False
        else:
            print("❌ 未找到配置文件，请先运行主程序生成配置")
            return False
    
    # 检查配置文件内容
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        valid_models = 0
        for model in config.get('models', []):
            if model.get('api_key') and model.get('api_key') != 'your_api_key_here':
                valid_models += 1
        
        if valid_models < 3:
            print(f"⚠️ 只有{valid_models}个模型配置了有效API密钥，至少需要3个")
            print("🔧 请编辑config.json文件，填入更多有效的API密钥")
            return False
        
        print(f"✅ 配置检查通过，发现{valid_models}个有效模型")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'gradio',
        'pandas',
        'plotly',
        'aiohttp',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("📦 请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def main():
    """主函数"""
    print("🚀 启动大模型在线竞技系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查配置
    if not check_config():
        print("\n💡 配置完成后，请重新运行此脚本")
        sys.exit(1)
    
    print("\n🌐 正在启动Gradio应用...")
    
    try:
        # 导入并启动Gradio应用
        from gradio_app import create_gradio_interface
        
        app = create_gradio_interface()
        
        print("\n" + "=" * 50)
        print("🎉 系统启动成功！")
        print("📱 访问地址: http://localhost:7860")
        print("🔗 如需外网访问，请在gradio_app.py中设置share=True")
        print("⏹️ 按 Ctrl+C 停止服务")
        print("=" * 50)
        
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n🔧 故障排除建议:")
        print("   1. 检查config.json配置是否正确")
        print("   2. 确认API密钥是否有效")
        print("   3. 检查网络连接")
        print("   4. 查看详细错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()