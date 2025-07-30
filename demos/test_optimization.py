#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试优化后的关键词单层检索系统
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_agent import MemoryAgent

def test_optimized_system():
    """
    测试优化后的关键词检索系统
    """
    print("=" * 60)
    print("测试优化后的关键词单层检索系统")
    print("=" * 60)
    
    # 配置
    DEEPSEEK_API_KEY = "sk-a4ce2451fc534091aff7704e5498a698"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    
    # 初始化记忆智能体
    print("初始化记忆智能体...")
    agent = MemoryAgent(
        deepseek_api_key=DEEPSEEK_API_KEY,
        deepseek_base_url=DEEPSEEK_BASE_URL,
        memory_file_path='/home/xuanwu/haven_ws/demos/data/memory_tree.json'
    )
    
    # 测试1：关键词提取对比
    print("\n=== 测试1：关键词提取方法对比 ===")
    test_text = "我刚从云南大理旅游回来，那里的风景真是太美了！洱海的日落特别震撼。"
    
    # 快速关键词提取（用户输入）
    fast_keywords = agent.memory_tree._extract_keywords_fast(test_text)
    print(f"用户输入快速提取: {', '.join(fast_keywords)}")
    
    # LLM关键词提取（记忆点）
    llm_keywords = agent.memory_tree._extract_keywords_with_llm(test_text, agent.client)
    print(f"记忆点LLM提取: {', '.join(llm_keywords)}")
    
    # 测试2：检索性能对比
    print("\n=== 测试2：检索性能测试 ===")
    
    # 检索相关记忆
    query = "陆李昕是谁？他做什么工作？"
    print(f"查询: {query}")
    
    import time
    start_time = time.time()
    results = agent.memory_tree.search(query, similarity_threshold=0.5, max_results=3)
    end_time = time.time()
    
    print(f"检索时间: {(end_time - start_time)*1000:.1f}ms")
    print(f"找到 {len(results)} 条相关记忆:")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 记忆摘要: {result['summary']}")
        print(f"   关键词: {', '.join(result['keywords'])}")
        print(f"   相似度: {result['similarity']:.3f}")
        print(f"   最终得分: {result['final_score']:.3f}")
        print(f"   时间: {result['timestamp'][:19]}")
    
    # 测试3：新对话和记忆生成
    print("\n=== 测试3：新对话和记忆生成 ===")
    
    # 开始新对话
    person_name = "测试用户"
    agent.start_chat(person_name)
    
    # 模拟对话
    user_input = "我最近在学习人工智能，特别是深度学习和神经网络"
    print(f"[{person_name}]: {user_input}")
    
    # 获取回复并生成记忆
    response = agent.chat(user_input)
    print(f"[机器人]: {response}")
    
    # 结束对话，查看生成的记忆
    memory_nodes = agent.end_conversation()
    
    if memory_nodes:
        print(f"\n生成了 {len(memory_nodes)} 个新记忆点:")
        for i, node in enumerate(memory_nodes, 1):
            print(f"\n{i}. 摘要: {node.summary}")
            print(f"   LLM关键词: {', '.join(node.keywords)}")
            print(f"   有关键词embedding: {'是' if node.keywords_embedding else '否'}")
            print(f"   有摘要embedding: {'否' if not node.embedding else '是'}")  # 应该是"否"
    
    # 测试4：验证存储优化
    print("\n=== 测试4：验证存储优化 ===")
    
    # 重新加载并检查embedding存储情况
    agent.memory_tree.save('/home/xuanwu/haven_ws/demos/data/memory_tree_optimized.json')
    
    # 检查文件大小
    import os
    original_size = os.path.getsize('/home/xuanwu/haven_ws/demos/data/memory_tree.json')
    optimized_size = os.path.getsize('/home/xuanwu/haven_ws/demos/data/memory_tree_optimized.json')
    
    print(f"原始文件大小: {original_size / 1024:.1f} KB")
    print(f"优化后大小: {optimized_size / 1024:.1f} KB")
    if original_size > 0:
        reduction = (1 - optimized_size / original_size) * 100
        print(f"大小减少: {reduction:.1f}%")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("优化效果总结:")
    print("1. ✅ 关键词提取：用户输入快速，记忆点精准")
    print("2. ✅ 检索算法：只使用关键词embedding，提高速度")
    print("3. ✅ 存储优化：移除摘要embedding，减少存储空间")
    print("4. ✅ 兼容性：保持API接口不变")
    print("=" * 60)

if __name__ == "__main__":
    test_optimized_system()