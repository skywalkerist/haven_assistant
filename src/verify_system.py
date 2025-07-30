#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级智能体语音唤醒模式验证脚本
"""

import os
import sys

def check_prerequisites():
    """检查系统先决条件"""
    print("🔍 检查系统先决条件...")
    
    checks = []
    
    # 检查唤醒词模型文件
    model_path = "/home/xuanwu/haven_ws/src/resources/haven.pmdl"
    if os.path.exists(model_path):
        checks.append(("✅", f"唤醒词模型文件存在: {model_path}"))
    else:
        checks.append(("❌", f"唤醒词模型文件不存在: {model_path}"))
    
    # 检查招呼语音文件
    greeting_path = "/home/xuanwu/haven_ws/config/greeting.wav"
    if os.path.exists(greeting_path):
        checks.append(("✅", f"招呼语音文件存在: {greeting_path}"))
    else:
        checks.append(("⚠️", f"招呼语音文件不存在: {greeting_path} (可选)"))
    
    # 检查面部数据库
    face_db_path = "/home/xuanwu/taskAgent/config/face_db.json"
    if os.path.exists(face_db_path):
        checks.append(("✅", f"面部数据库存在: {face_db_path}"))
    else:
        checks.append(("❌", f"面部数据库不存在: {face_db_path}"))
    
    # 检查snowboy模块
    try:
        sys.path.append('/home/xuanwu/haven_ws/src')
        sys.path.append('/home/xuanwu/snowboy/snowboy-master/examples/Python3')
        import snowboydecoder
        checks.append(("✅", "snowboydecoder模块可用"))
    except ImportError:
        checks.append(("❌", "snowboydecoder模块不可用"))
    
    # 检查其他依赖
    dependencies = ['flask', 'requests', 'openai']
    for dep in dependencies:
        try:
            __import__(dep)
            checks.append(("✅", f"{dep}模块可用"))
        except ImportError:
            checks.append(("❌", f"{dep}模块不可用"))
    
    # 显示检查结果
    print("\n📋 检查结果:")
    for status, message in checks:
        print(f"  {status} {message}")
    
    # 统计
    success_count = sum(1 for status, _ in checks if status == "✅")
    total_count = len([c for c in checks if c[0] in ["✅", "❌"]])  # 排除警告
    
    print(f"\n📊 检查统计: {success_count}/{total_count} 项通过")
    
    if success_count == total_count:
        print("🎉 所有必要条件都满足！")
        return True
    else:
        print("⚠️ 部分条件不满足，可能影响系统运行")
        return False

def show_system_info():
    """显示系统信息"""
    print("\n🏗️ 系统架构:")
    print("┌─────────────────────┐    HTTP API    ┌──────────────────────┐")
    print("│   面部识别服务       │ ◄──────────── │   超级智能体主程序    │")
    print("│   (face环境)        │               │   (base环境)         │")
    print("│                    │               │                     │")
    print("│ - 人脸识别          │               │ - 语音唤醒监听       │")
    print("│ - 机械臂控制        │               │ - 状态管理           │")
    print("│ - 相机处理          │               │ - 对话系统           │")
    print("└─────────────────────┘               │ - 记忆管理           │")
    print("                                      └──────────────────────┘")
    
    print("\n🔄 工作流程:")
    print("1. 🎧 语音监听 '小助小助'")
    print("2. 🔊 播放招呼语音")
    print("3. 👁️ 面部识别（扫描/搜索）")
    print("4. 🤖 个性化问候")
    print("5. 💬 智能对话")
    print("6. 🔄 返回监听状态")

def show_usage_instructions():
    """显示使用说明"""
    print("\n📖 使用说明:")
    print("=" * 50)
    
    print("\n1. 启动系统:")
    print("   cd /home/xuanwu/haven_ws/src")
    print("   python start_system.py")
    
    print("\n2. 语音交互:")
    print("   • 说 '小助小助' 唤醒智能体")
    print("   • 系统会自动识别用户身份")
    print("   • 听到个性化问候后开始对话")
    print("   • 对话结束后自动返回监听状态")
    
    print("\n3. 故障排除:")
    print("   • 确保麦克风工作正常")
    print("   • 检查face环境服务是否运行")
    print("   • 确认相机和机械臂连接正常")
    
    print("\n4. 测试建议:")
    print("   • 首先运行: python mock_face_service.py (模拟模式)")
    print("   • 再运行超级智能体进行测试")

def main():
    """主函数"""
    print("🚀 超级智能体语音唤醒模式 - 系统验证")
    print("=" * 60)
    
    # 检查先决条件
    all_good = check_prerequisites()
    
    # 显示系统信息
    show_system_info()
    
    # 显示使用说明
    show_usage_instructions()
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ 系统验证完成，可以启动超级智能体！")
        print("🎯 运行命令: python start_system.py")
    else:
        print("⚠️ 系统验证发现问题，请先解决依赖问题")
        print("💡 可以先运行模拟模式进行测试")
    print("=" * 60)

if __name__ == "__main__":
    main()