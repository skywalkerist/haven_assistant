#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
双人对话测试程序 - 测试记忆检索和联想功能
第一场：陆李昕介绍自己的基本信息
第二场：程一苓询问关于陆李昕的问题，测试检索功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_agent import MemoryAgent

def simulate_lulikun_conversation(agent):
    """
    模拟陆李昕的对话 - 建立基础记忆
    """
    person_name = "陆李昕"
    print(f"\n{'='*60}")
    print(f"第一场对话：与{person_name}的基础信息建立")
    print(f"{'='*60}")
    
    # 修复PersonProfile路径问题：使用绝对路径
    agent.start_chat(person_name)
    
    # 陆李昕的基础信息对话
    conversations = [
        "你好！我是陆李昕，我是这个机器人项目的创作者。很高兴见到你！",
        "我刚从云南大理旅游回来，那里的风景真是太美了！洱海的日落特别震撼，拍了很多照片。",
        "我平时很喜欢运动，特别是爬山和跑步。上周末我去爬了香山，虽然累但很有成就感。",
        "作为这个AI项目的创作者，我一直在思考如何让机器人更好地理解和帮助人类。",
        "下个月我计划去西藏旅行，准备挑战一下高原徒步。听说风景特别美，但有点担心高反。",
        "对了，我还特别喜欢摄影，尤其是风景摄影。大理洱海的照片我准备打印出来挂在办公室。"
    ]
    
    # 进行对话
    for i, user_input in enumerate(conversations, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"[{person_name}]: {user_input}")
        
        # 获取机器人回复
        assistant_response = agent.chat(user_input)
        print(f"[机器人]: {assistant_response}")
        
        # 短暂停顿
        import time
        time.sleep(0.5)
    
    # 结束对话，触发记忆整理
    print(f"\n--- 结束与{person_name}的对话 ---")
    print("正在整理对话记忆...")
    memory_nodes = agent.end_conversation()
    
    print(f"\n✓ 生成的记忆点数量: {len(memory_nodes)}")
    print("记忆点内容:")
    for i, node in enumerate(memory_nodes, 1):
        print(f"  {i}. {node.summary}")
        if node.keywords:
            print(f"     关键词: {', '.join(node.keywords)}")
    
    return memory_nodes

def simulate_chengyiling_conversation(agent):
    """
    模拟程一苓的对话 - 询问陆李昕相关问题，测试检索功能
    """
    person_name = "程一苓"
    print(f"\n{'='*60}")
    print(f"第二场对话：与{person_name}的检索测试")
    print(f"{'='*60}")
    
    agent.start_chat(person_name)
    
    # 程一苓询问关于陆李昕的问题
    test_conversations = [
        "你好，我是程一苓。我听说陆李昕是这个项目的创作者，你能告诉我一些关于他的信息吗？",
        "陆李昕最近去过什么地方旅游吗？我也很喜欢旅游。",
        "我想了解一下陆李昕的爱好，他平时喜欢做什么运动？",
        "听说陆李昕也喜欢摄影？他拍过什么比较好的照片吗？",
        "陆李昕有什么旅行计划吗？我也在计划下次的旅行目的地。"
    ]
    
    print("\n🔍 开始测试检索功能...")
    retrieval_results = []
    
    # 进行对话并记录检索结果
    for i, user_input in enumerate(test_conversations, 1):
        print(f"\n--- 第{i}轮检索测试 ---")
        print(f"[{person_name}]: {user_input}")
        
        # 手动测试检索功能
        print(f"\n🔎 检索关键词: {user_input}")
        retrieved_memories = agent.memory_tree.search(user_input, similarity_threshold=0.5, max_results=3)
        
        print(f"检索到 {len(retrieved_memories)} 条相关记忆:")
        for j, memory in enumerate(retrieved_memories, 1):
            print(f"  {j}. {memory['summary'][:80]}...")
            print(f"     相似度: {memory['similarity']:.3f} | 关键词: {memory['keywords']}")
        
        retrieval_results.append({
            'query': user_input,
            'results': retrieved_memories
        })
        
        # 获取机器人回复
        assistant_response = agent.chat(user_input)
        print(f"[机器人]: {assistant_response}")
        
        import time
        time.sleep(0.5)
    
    # 结束对话
    print(f"\n--- 结束与{person_name}的对话 ---")
    memory_nodes = agent.end_conversation()
    
    print(f"\n✓ 程一苓对话生成的记忆点数量: {len(memory_nodes)}")
    
    return retrieval_results

def analyze_retrieval_performance(retrieval_results):
    """
    分析检索性能
    """
    print(f"\n{'='*60}")
    print("检索性能分析报告")
    print(f"{'='*60}")
    
    total_queries = len(retrieval_results)
    successful_retrievals = 0
    
    for i, result in enumerate(retrieval_results, 1):
        query = result['query']
        memories = result['results']
        
        print(f"\n查询 {i}: {query}")
        if memories:
            successful_retrievals += 1
            print(f"  ✓ 成功检索到 {len(memories)} 条记忆")
            # 检查是否包含陆李昕相关信息
            lulikun_related = any('陆李昕' in memory['summary'] for memory in memories)
            if lulikun_related:
                print(f"  ✓ 包含陆李昕相关信息")
            else:
                print(f"  ⚠ 未包含陆李昕相关信息")
        else:
            print(f"  ✗ 未检索到相关记忆")
    
    success_rate = (successful_retrievals / total_queries) * 100
    print(f"\n📊 检索成功率: {success_rate:.1f}% ({successful_retrievals}/{total_queries})")
    
    if success_rate >= 80:
        print("🎉 检索性能优秀！")
    elif success_rate >= 60:
        print("👍 检索性能良好")
    else:
        print("⚠️ 检索性能需要改进")

def main():
    """
    主程序：执行双人对话测试
    """
    print("=" * 60)
    print("双人对话记忆检索测试程序")
    print("测试场景：陆李昕建立记忆 → 程一苓检索询问")
    print("=" * 60)
    
    # 配置
    DEEPSEEK_API_KEY = "sk-a4ce2451fc534091aff7704e5498a698"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    
    # 初始化记忆智能体，使用绝对路径
    print("初始化记忆智能体...")
    agent = MemoryAgent(
        deepseek_api_key=DEEPSEEK_API_KEY,
        deepseek_base_url=DEEPSEEK_BASE_URL,
        memory_file_path='/home/xuanwu/haven_ws/demos/data/memory_tree.json'
    )
    
    # 修复PersonProfile路径问题
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from memory_agent import PersonProfile
    
    # 重写PersonProfile的默认data_path为绝对路径
    original_init = PersonProfile.__init__
    def patched_init(self, person_name: str, data_path: str = '/home/xuanwu/haven_ws/data/profiles'):
        original_init(self, person_name, data_path)
    PersonProfile.__init__ = patched_init
    
    try:
        # 第一场对话：陆李昕建立基础记忆
        lulikun_memories = simulate_lulikun_conversation(agent)
        
        # 短暂等待，让embedding生成完成
        print("\n⏳ 等待记忆处理完成...")
        import time
        time.sleep(2)
        
        # 第二场对话：程一苓检索测试
        retrieval_results = simulate_chengyiling_conversation(agent)
        
        # 分析检索性能
        analyze_retrieval_performance(retrieval_results)
        
        # 显示文件位置
        print(f"\n{'='*60}")
        print("测试完成！文件位置:")
        print(f"📁 记忆文件: /home/xuanwu/haven_ws/demos/data/memory_tree.json")
        print(f"📁 陆李昕画像: /home/xuanwu/haven_ws/data/profiles/陆李昕_profile.json")
        print(f"📁 程一苓画像: /home/xuanwu/haven_ws/data/profiles/程一苓_profile.json")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()