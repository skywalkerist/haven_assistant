#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试改进后的记忆树检索算法
验证多粒度文本表示和双层匹配的效果
"""

import sys
import os

# 添加路径以导入所需模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from semantic_memory import MemoryTree, MemoryNode

def test_enhanced_memory_search():
    """测试增强的记忆搜索功能"""
    
    print("=" * 60)
    print("测试增强的记忆搜索算法")
    print("=" * 60)
    
    # 初始化记忆树
    embedding_config = {
        'APPID': 'b32f165e',
        'APISecret': 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
        'APIKEY': 'bf4caffa0bd087acc04cd63d0ee27fc5'
    }
    
    memory_tree = MemoryTree(embedding_config=embedding_config)
    
    print("1. 创建测试记忆点...")
    
    # 添加一些测试记忆点
    test_memories = [
        "用户询问了关于高血压的饮食注意事项，特别关心能否吃咸菜，我建议减少钠盐摄入，多吃新鲜蔬菜水果",
        "用户提到他最近血压有点高，医生建议控制饮食，他想知道具体应该怎么做",
        "用户说他喜欢摄影，特别是风景摄影，最近想买一台新相机",
        "给用户推荐了索尼A7相机，因为它在风景摄影方面表现很好",
        "用户询问Python编程学习资源，我推荐了一些在线教程和书籍",
        "用户对机器学习很感兴趣但觉得数学基础有点薄弱，建议从基础开始",
        "用户提到他在学习深度学习，但对反向传播算法理解有困难",
        "用户询问关于糖尿病患者的运动建议，我建议适量有氧运动"
    ]
    
    # 批量添加记忆点
    for i, memory_text in enumerate(test_memories):
        print(f"  添加记忆点 {i+1}: {memory_text[:30]}...")
        memory_tree.add_memory(memory_text)
    
    print(f"\n✓ 成功添加了 {len(test_memories)} 个记忆点")
    
    print("\n2. 测试不同查询的匹配效果...")
    
    # 测试查询
    test_queries = [
        "我能吃腌制食品吗？",           # 应该匹配高血压饮食相关的记忆
        "推荐一款相机",               # 应该匹配摄影和相机推荐
        "如何学习编程？",             # 应该匹配编程学习资源
        "机器学习难吗？",             # 应该匹配机器学习相关记忆
        "糖尿病人可以运动吗？",       # 应该匹配糖尿病运动建议
        "神经网络怎么训练？",         # 应该匹配深度学习相关记忆
    ]
    
    for query in test_queries:
        print(f"\n" + "="*50)
        print(f"查询: {query}")
        print("="*50)
        
        # 执行搜索
        results = memory_tree.search(query, similarity_threshold=0.5, max_results=3)
        
        if results:
            print(f"找到 {len(results)} 个相关记忆:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. 记忆内容: {result['summary']}")
                print(f"   关键词: {', '.join(result['keywords'])}")
                print(f"   关键词相似度: {result['keywords_similarity']:.3f}")
                print(f"   摘要相似度: {result['summary_similarity']:.3f}")
                print(f"   综合相似度: {result['composite_similarity']:.3f}")
                print(f"   时间衰减因子: {result['decay_factor']:.3f}")
                print(f"   最终得分: {result['composite_score']:.3f}")
        else:
            print("❌ 没有找到相关记忆")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    
    return memory_tree

def test_keywords_extraction():
    """测试关键词提取功能"""
    print("\n" + "="*60)
    print("测试关键词提取功能")
    print("="*60)
    
    memory_tree = MemoryTree()
    
    test_texts = [
        "用户询问了关于高血压的饮食注意事项，特别关心能否吃咸菜",
        "我建议减少钠盐摄入，多吃新鲜蔬菜水果",
        "用户说他喜欢摄影，特别是风景摄影，最近想买一台新相机",
        "给用户推荐了索尼A7相机，因为它在风景摄影方面表现很好",
        "用户对机器学习很感兴趣但觉得数学基础有点薄弱"
    ]
    
    for text in test_texts:
        keywords = memory_tree._extract_keywords(text)
        print(f"\n原文: {text}")
        print(f"关键词: {', '.join(keywords)}")

def compare_similarity_distributions():
    """比较新旧相似度分布差异"""
    print("\n" + "="*60)
    print("比较相似度分布差异")
    print("="*60)
    
    # 这里可以加载现有的记忆数据进行对比测试
    print("提示: 运行完整对话后，观察新的相似度分布是否有改善")
    print("- 旧算法: 相似度集中在 0.94-0.96")
    print("- 新算法: 期望有更大的区分度范围")

if __name__ == "__main__":
    try:
        # 测试关键词提取
        test_keywords_extraction()
        
        # 测试增强搜索
        memory_tree = test_enhanced_memory_search()
        
        # 比较相似度分布
        compare_similarity_distributions()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()