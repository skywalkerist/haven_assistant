#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自思考事件触发器 - 按概率随机触发四种自思考事件

事件概率配置：
- 记忆清理 (_summarize_similar_memories): 30%
- 画像更新 (_reflect_on_profile): 35% 
- 关系分析 (_discover_relationships): 25%
- 全局认知 (_synthesize_global_experience): 10%

总概率：100%
"""

import random
import sys
import os
from typing import Dict, Callable

# 添加必要的路径
sys.path.append('/home/xuanwu/haven_ws/src')

from memory_agent import MemoryAgent

class SelfReflectionTrigger:
    """
    自思考事件触发器
    """
    
    def __init__(self, memory_agent: MemoryAgent):
        self.memory_agent = memory_agent
        
        # 定义四个事件及其概率（概率总和应为1.0）
        self.events = {
            'summarize_similar': {
                'probability': 0.30,
                'name': '记忆清理',
                'description': '随机挑选10条同一人的记忆，检测相似或无意义记忆，精简删除并保留最新记忆',
                'function': self._trigger_summarize_similar
            },
            'update_profile': {
                'probability': 0.35,
                'name': '画像更新', 
                'description': '随机分析一个人物的记忆，更新优化其个人画像',
                'function': self._trigger_reflect_on_profile
            },
            'discover_relationships': {
                'probability': 0.25,
                'name': '关系分析',
                'description': '随机分析两个人的记忆，推断关系并更新用户画像（好友、恋人、不太和睦的人等）',
                'function': self._trigger_discover_relationships
            },
            'global_synthesis': {
                'probability': 0.10,
                'name': '全局认知',
                'description': '提取时间相近记忆，理解总体主题，维护机器人脑海文件',
                'function': self._trigger_synthesize_global_experience
            }
        }
        
        # 验证概率总和
        total_prob = sum(event['probability'] for event in self.events.values())
        if abs(total_prob - 1.0) > 0.001:
            raise ValueError(f"事件概率总和不等于1.0，当前总和：{total_prob}")
    
    def display_event_probabilities(self):
        """
        显示所有事件的概率配置
        """
        print("=" * 60)
        print("🧠 自思考事件触发器 - 概率配置")
        print("=" * 60)
        
        for event_key, event_info in self.events.items():
            probability_percent = event_info['probability'] * 100
            print(f"📊 {event_info['name']}: {probability_percent:.1f}%")
            print(f"   {event_info['description']}")
            print()
        
        print(f"✅ 概率总和: {sum(event['probability'] for event in self.events.values()) * 100:.1f}%")
        print("=" * 60)
    
    def select_random_event(self) -> str:
        """
        基于概率随机选择一个事件
        
        Returns:
            选中的事件键名
        """
        # 生成0-1之间的随机数
        rand_num = random.random()
        
        # 累积概率选择
        cumulative_prob = 0.0
        for event_key, event_info in self.events.items():
            cumulative_prob += event_info['probability']
            if rand_num <= cumulative_prob:
                return event_key
        
        # 如果由于浮点数精度问题没有选中，返回最后一个事件
        return list(self.events.keys())[-1]
    
    def trigger_random_reflection(self):
        """
        触发一次随机的自思考事件
        """
        # 选择随机事件
        selected_event_key = self.select_random_event()
        selected_event = self.events[selected_event_key]
        
        print("\n🎲 随机事件选择结果:")
        print(f"🎯 触发事件: {selected_event['name']}")
        print(f"📝 事件描述: {selected_event['description']}")
        print(f"🎲 选中概率: {selected_event['probability'] * 100:.1f}%")
        print("\n" + "="*50)
        
        # 执行对应的函数
        try:
            print(f"🚀 开始执行 {selected_event['name']} ...")
            selected_event['function']()
            print(f"✅ {selected_event['name']} 执行完成")
        except Exception as e:
            print(f"❌ {selected_event['name']} 执行失败: {e}")
        
        print("="*50)
    
    def _trigger_summarize_similar(self):
        """触发记忆清理事件"""
        self.memory_agent.self_reflect('summarize_similar')
    
    def _trigger_reflect_on_profile(self):
        """触发画像更新事件"""
        self.memory_agent.self_reflect('update_profile')
    
    def _trigger_discover_relationships(self):
        """触发关系分析事件"""
        self.memory_agent.self_reflect('discover_relationships')
    
    def _trigger_synthesize_global_experience(self):
        """触发全局认知事件"""
        self.memory_agent.self_reflect('global_synthesis')
    
    def run_simulation(self, num_runs: int = 10):
        """
        运行多次模拟，统计各事件的触发次数
        
        Args:
            num_runs: 模拟运行次数
        """
        print(f"\n🔬 运行{num_runs}次模拟，统计事件触发频率...")
        
        event_counts = {key: 0 for key in self.events.keys()}
        
        for i in range(num_runs):
            selected_event = self.select_random_event()
            event_counts[selected_event] += 1
        
        print("\n📈 模拟结果统计:")
        print("-" * 50)
        for event_key, count in event_counts.items():
            event_name = self.events[event_key]['name']
            expected_prob = self.events[event_key]['probability'] * 100
            actual_prob = (count / num_runs) * 100
            print(f"{event_name}: {count}/{num_runs} ({actual_prob:.1f}%, 期望{expected_prob:.1f}%)")
        print("-" * 50)


def create_memory_agent():
    """
    创建记忆智能体实例
    """
    # DeepSeek API配置
    deepseek_api_key = "sk-fdabadb2973b4795b2444da60e75152f"
    deepseek_base_url = "https://api.deepseek.com"
    memory_file_path = "/home/xuanwu/haven_ws/demos/data/memory_tree.json"
    
    # 创建记忆智能体
    memory_agent = MemoryAgent(
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=deepseek_base_url,
        memory_file_path=memory_file_path
    )
    
    return memory_agent


def main():
    """
    主函数 - 运行自思考事件触发器
    """
    print("🚀 启动自思考事件触发器")
    
    try:
        # 创建记忆智能体
        print("🔧 正在初始化记忆智能体...")
        memory_agent = create_memory_agent()
        
        # 创建触发器
        trigger = SelfReflectionTrigger(memory_agent)
        
        # 显示事件概率配置
        trigger.display_event_probabilities()
        
        # 用户选择模式
        print("请选择运行模式:")
        print("1. 触发一次随机自思考事件")
        print("2. 运行模拟统计（不执行实际函数）")
        print("3. 连续触发多次事件")
        
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == '1':
            # 触发一次随机事件
            trigger.trigger_random_reflection()
            
        elif choice == '2':
            # 运行模拟
            try:
                num_runs = int(input("请输入模拟次数 (默认100): ") or "100")
                trigger.run_simulation(num_runs)
            except ValueError:
                print("❌ 输入无效，使用默认值100次")
                trigger.run_simulation(100)
                
        elif choice == '3':
            # 连续触发多次
            try:
                num_triggers = int(input("请输入触发次数 (默认3): ") or "3")
                print(f"\n🔄 将连续触发{num_triggers}次自思考事件...")
                
                for i in range(num_triggers):
                    print(f"\n{'='*20} 第 {i+1}/{num_triggers} 次 {'='*20}")
                    trigger.trigger_random_reflection()
                    
                    if i < num_triggers - 1:
                        input("\n按回车键继续下一次触发...")
                        
            except ValueError:
                print("❌ 输入无效，使用默认值3次")
                for i in range(3):
                    print(f"\n{'='*20} 第 {i+1}/3 次 {'='*20}")
                    trigger.trigger_random_reflection()
                    if i < 2:
                        input("\n按回车键继续下一次触发...")
        else:
            print("❌ 无效选择，默认触发一次随机事件")
            trigger.trigger_random_reflection()
            
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 自思考事件触发器已结束")


if __name__ == "__main__":
    main()