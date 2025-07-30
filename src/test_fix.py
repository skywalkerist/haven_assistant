#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试对话系统修复结果
"""

import sys
import os
sys.path.append('/home/xuanwu/haven_ws/src')

from memory_agent import MemoryAgent

def test_start_chat():
    """测试start_chat方法是否正确返回值"""
    print("🧪 测试对话系统启动修复...")
    
    try:
        # 创建记忆智能体
        agent = MemoryAgent(
            deepseek_api_key="sk-test",  # 测试用的假密钥
            deepseek_base_url="https://api.deepseek.com",
            memory_file_path="/tmp/test_memory.json"
        )
        
        # 测试start_chat方法
        result = agent.start_chat("TestUser")
        
        print(f"start_chat返回值: {result}")
        print(f"返回值类型: {type(result)}")
        
        if result is True:
            print("✅ start_chat方法修复成功，正确返回True")
            print("✅ 对话系统现在可以正常启动")
        elif result is False:
            print("❌ start_chat方法返回False，可能有异常")
        else:
            print(f"⚠️ start_chat方法返回了意外的值: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 对话系统修复验证")
    print("=" * 40)
    
    # 测试start_chat修复
    success = test_start_chat()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 修复验证成功！")
        print("💡 现在超级智能体的对话系统应该可以正常启动了")
        print("🔄 建议重新运行超级智能体进行测试")
    else:
        print("⚠️ 修复验证失败，可能还有其他问题")
    print("=" * 40)

if __name__ == "__main__":
    main()