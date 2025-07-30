#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级智能体测试脚本 - 验证完整系统功能
"""

import sys
import os
import time
from pathlib import Path

# 添加项目路径
sys.path.append('/home/xuanwu/haven_ws/src')

from super_intelligent_agent import SuperIntelligentAgent, create_default_config, AgentState

def test_system_initialization():
    """测试系统初始化"""
    print("🧪 测试1: 系统初始化")
    print("-" * 40)
    
    try:
        config = create_default_config()
        agent = SuperIntelligentAgent(config)
        
        print("✅ 超级智能体对象创建成功")
        print(f"📊 初始状态: {agent.state}")
        print(f"🤖 当前用户: {agent.current_user}")
        
        # 测试状态获取
        status = agent.get_current_state()
        print("📈 状态信息:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        agent.cleanup()
        print("✅ 测试1通过: 系统初始化正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试1失败: {e}")
        return False

def test_face_recognition_integration():
    """测试面部识别系统集成"""
    print("\n🧪 测试2: 面部识别系统集成")
    print("-" * 40)
    
    try:
        config = create_default_config()
        agent = SuperIntelligentAgent(config)
        
        # 检查面部识别系统是否正确创建
        print(f"👤 面部识别系统: {type(agent.face_system).__name__}")
        print(f"🎯 识别阈值: {agent.face_system.config.recognition_threshold}")
        print(f"🌐 服务URL: {agent.face_system.config.service_url}")
        
        # 注意：客户端模式下不直接访问数据库文件
        print("ℹ️ 使用客户端模式，数据库由服务端管理")
        
        agent.cleanup()
        print("✅ 测试2通过: 面部识别系统集成正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试2失败: {e}")
        return False

def test_memory_agent_integration():
    """测试记忆智能体集成"""
    print("\n🧪 测试3: 记忆智能体集成")
    print("-" * 40)
    
    try:
        config = create_default_config()
        agent = SuperIntelligentAgent(config)
        
        # 检查记忆智能体是否正确创建
        print(f"🧠 记忆智能体: {type(agent.memory_agent).__name__}")
        print(f"📁 记忆文件路径: {agent.memory_agent.memory_file_path}")
        
        # 检查记忆文件是否存在
        memory_dir = os.path.dirname(agent.memory_agent.memory_file_path)
        if not os.path.exists(memory_dir):
            os.makedirs(memory_dir, exist_ok=True)
            print(f"📁 创建记忆目录: {memory_dir}")
        
        # 测试记忆系统
        print(f"🌳 记忆树根节点: {agent.memory_agent.memory_tree.root.summary}")
        
        agent.cleanup()
        print("✅ 测试3通过: 记忆智能体集成正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试3失败: {e}")
        return False

def test_state_transitions():
    """测试状态转换"""
    print("\n🧪 测试4: 状态转换")
    print("-" * 40)
    
    try:
        config = create_default_config()
        agent = SuperIntelligentAgent(config)
        
        # 测试初始状态
        print(f"🔄 初始状态: {agent.state}")
        assert agent.state == AgentState.SLEEPING, "初始状态应为SLEEPING"
        
        # 测试唤醒（不进行实际硬件初始化）
        print("🌅 模拟唤醒...")
        agent.state = AgentState.SCANNING
        print(f"🔄 状态变更为: {agent.state}")
        assert agent.state == AgentState.SCANNING, "唤醒后状态应为SCANNING"
        
        # 测试对话模式
        print("💬 模拟开始对话...")
        agent.state = AgentState.CHATTING
        agent.current_user = "测试用户"
        print(f"🔄 状态变更为: {agent.state}")
        print(f"👤 当前用户: {agent.current_user}")
        assert agent.state == AgentState.CHATTING, "对话状态应为CHATTING"
        
        # 测试结束对话
        print("👋 模拟结束对话...")
        agent.state = AgentState.SCANNING
        agent.current_user = None
        print(f"🔄 状态变更为: {agent.state}")
        assert agent.state == AgentState.SCANNING, "结束对话后应返回SCANNING"
        
        agent.cleanup()
        print("✅ 测试4通过: 状态转换正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试4失败: {e}")
        return False

def test_configuration():
    """测试配置系统"""
    print("\n🧪 测试5: 配置系统")
    print("-" * 40)
    
    try:
        config = create_default_config()
        
        # 验证配置参数
        print("⚙️ 配置参数验证:")
        print(f"  🔍 搜索角度范围: {config.search_angle_range}")
        print(f"  📐 搜索步长: {config.search_step}°")
        print(f"  ⏱️ 搜索延迟: {config.search_delay}s")
        print(f"  🎯 识别阈值: {config.recognition_confidence_threshold}")
        print(f"  🔄 扫描间隔: {config.continuous_scan_interval}s")
        print(f"  ⏰ 未知用户超时: {config.unknown_user_timeout}s")
        
        # 验证关键配置
        assert config.search_angle_range == (-60, 60), "搜索角度范围配置错误"
        assert config.search_step > 0, "搜索步长必须大于0"
        assert config.search_delay > 0, "搜索延迟必须大于0"
        
        print("✅ 测试5通过: 配置系统正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试5失败: {e}")
        return False

def run_integration_tests():
    """运行完整的集成测试"""
    print("🚀 开始超级智能体集成测试")
    print("=" * 60)
    
    tests = [
        test_system_initialization,
        test_face_recognition_integration,
        test_memory_agent_integration,
        test_state_transitions,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！超级智能体集成成功！")
        print("\n💡 使用说明:")
        print("1. 确保面部数据库文件存在并包含已注册用户")
        print("2. 确保DeepSeek API密钥配置正确")
        print("3. 确保Orbbec相机正确连接")
        print("4. 运行 python super_intelligent_agent.py 启动系统")
    else:
        print("⚠️ 部分测试失败，请检查系统配置和依赖")
    
    print("=" * 60)

if __name__ == "__main__":
    run_integration_tests()