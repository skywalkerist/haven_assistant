#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关键词提取算法
"""

from semantic_memory import MemoryTree

def test_keyword_extraction():
    # 创建记忆树实例
    memory_tree = MemoryTree()
    
    # 用户提供的测试文本
    test_text = "我刚从云南大理旅游回来，那里的风景真是太美了！洱海的日落特别震撼"
    
    print(f"原始文本: {test_text}")
    print("-" * 50)
    
    # 测试快速关键词提取
    keywords = memory_tree._extract_keywords_fast(test_text, max_keywords=8)
    print(f"快速提取的关键词: {keywords}")
    print(f"关键词数量: {len(keywords)}")
    print("-" * 50)
    
    # 预期的关键词应该是
    expected_keywords = ["云南大理", "旅游", "风景", "洱海", "日落", "震撼"]
    print(f"期望的关键词: {expected_keywords}")
    
    # 检查是否匹配
    matches = []
    for expected in expected_keywords:
        for actual in keywords:
            if expected in actual or actual in expected:
                matches.append((expected, actual))
    
    print(f"匹配情况: {matches}")

if __name__ == "__main__":
    test_keyword_extraction()
