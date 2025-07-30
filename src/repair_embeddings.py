#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复记忆树中缺失embedding的脚本
用于修复由于API调用失败导致的空embedding问题
"""

from memory_agent import MemoryAgent

def main():
    print("=== 记忆树Embedding修复工具 ===")
    
    # 初始化智能体
    agent = MemoryAgent(
        deepseek_api_key="sk-a4ce2451fc534091aff7704e5498a698",
        deepseek_base_url="https://api.deepseek.com"
    )
    
    # 执行修复
    repaired_count = agent.repair_embeddings()
    
    print(f"\n修复结果:")
    if repaired_count > 0:
        print(f"✅ 成功修复了 {repaired_count} 个记忆点的embedding")
        print("📁 已保存到 data/memory_tree.json")
    else:
        print("ℹ️ 所有记忆点的embedding都正常，无需修复")
    
    print("\n可以重新运行搜索测试来验证修复效果")

if __name__ == "__main__":
    main()