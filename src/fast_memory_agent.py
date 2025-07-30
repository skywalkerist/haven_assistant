#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速记忆代理 - 优化版本的记忆管理系统
重点优化：缓存机制、批量处理、简化操作、异步保存
"""

import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

from openai import OpenAI

# 导入快速记忆系统和优化工具
from fast_semantic_memory import FastMemoryTree, FastMemoryNode
from performance_utils import (
    PerformanceOptimizer, FastStringProcessor, MemoryCache,
    global_cache, memory_batch_processor, fast_hash
)
from optimized_config import fast_config, should_skip_check, get_batch_size, get_timeout

class FastPersonProfile:
    """
    快速用户画像 - 使用缓存和简化I/O
    """
    def __init__(self, person_name: str, data_path: str = '/home/xuanwu/haven_ws/demos/data/profiles'):
        self.person_name = person_name
        self.profile_path = os.path.join(data_path, f"{person_name}_profile.json")
        self.attributes: Dict[str, Any] = {
            "name": person_name,
            "age": "",
            "occupation": "",
            "hobbies": [],
            "personality": "",
            "favorite_foods": [],
            "habits": [],
            "quirks": [],
            "hometown": "",
            "preferences": {},
            "mood": "neutral",
            "last_interaction": None
        }
        
        os.makedirs(data_path, exist_ok=True)
        self.load_profile()
        
        # 缓存标记
        self._needs_save = False
        self._last_save_time = datetime.utcnow()

    @PerformanceOptimizer.timing_decorator("load_profile")
    def load_profile(self):
        """快速加载用户画像"""
        try:
            # 检查缓存
            cache_key = f"profile_{self.person_name}"
            cached_profile = global_cache.get(cache_key)
            if cached_profile is not None:
                self.attributes = cached_profile
                return
            
            # 从文件加载
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self.attributes = json.load(f)
            
            # 缓存结果
            global_cache.put(cache_key, self.attributes.copy())
            
        except FileNotFoundError:
            self.save_profile()
        except (json.JSONDecodeError, KeyError):
            self.save_profile()

    def save_profile(self):
        """保存用户画像 - 支持批量和异步"""
        self.attributes['last_interaction'] = datetime.utcnow().isoformat()
        self._needs_save = True
        
        if fast_config.FAST_MODE.get('async_operations', False):
            # 异步保存
            threading.Thread(target=self._save_sync, daemon=True).start()
        else:
            self._save_sync()

    def _save_sync(self):
        """同步保存"""
        try:
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.attributes, f, ensure_ascii=False, indent=2)
            
            # 更新缓存
            cache_key = f"profile_{self.person_name}"
            global_cache.put(cache_key, self.attributes.copy())
            
            self._needs_save = False
            self._last_save_time = datetime.utcnow()
        except Exception:
            pass  # 简化错误处理

    def update_attribute(self, key: str, value: Any):
        """更新属性"""
        self.attributes[key] = value
        if fast_config.BATCH_CONFIG.get('auto_save_enabled', True):
            self.save_profile()

class FastMemoryAgent:
    """
    快速记忆代理 - 优化的对话和记忆管理
    """
    def __init__(self, deepseek_api_key: str, deepseek_base_url: str, 
                 memory_file_path: str = '/home/xuanwu/haven_ws/demos/data/memory_tree.json'):
        self.client = OpenAI(api_key=deepseek_api_key, base_url=deepseek_base_url)
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(memory_file_path), exist_ok=True)
        
        # 初始化快速记忆树
        embedding_config = {
            'APPID': 'b32f165e',
            'APISecret': 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
            'APIKEY': 'bf4caffa0bd087acc04cd63d0ee27fc5'
        }
        
        # 加载或创建记忆树
        try:
            self.memory_tree = FastMemoryTree.load(memory_file_path, embedding_config)
        except:
            self.memory_tree = FastMemoryTree(embedding_config=embedding_config)
        
        self.memory_file_path = memory_file_path
        self.current_person_profile: Optional[FastPersonProfile] = None
        self.short_term_memory: List[Dict[str, str]] = []
        
        # 性能优化：缓存常用模板
        self._system_prompt_template = None
        self._profile_format_cache = MemoryCache(max_size=50)
        
        # 批量保存计数器
        self._conversation_count = 0
        self._last_save_time = datetime.utcnow()

    @PerformanceOptimizer.timing_decorator("start_chat")
    def start_chat(self, person_name: str):
        """快速启动聊天"""
        try:
            self.current_person_profile = FastPersonProfile(person_name)
            self.short_term_memory = []  # 重置短期记忆
            self._conversation_count = 0
            return True
        except Exception:
            return False

    @PerformanceOptimizer.timing_decorator("fast_chat")
    def chat(self, user_input: str) -> str:
        """
        快速对话处理 - 优化的多轮对话
        """
        if not self.current_person_profile:
            return "Error: Chat not started. Please use start_chat(person_name) first."

        # 添加用户消息到短期记忆
        self.short_term_memory.append({"role": "user", "content": user_input})

        # 快速检索相关记忆
        retrieved_memories = self._fast_retrieve_memories(user_input)
        
        # 构建优化的提示词
        system_prompt = self._build_optimized_prompt(retrieved_memories)
        
        # 管理对话上下文长度
        self._manage_context_length()
        
        # 构建API消息
        messages_for_api = [{"role": "system", "content": system_prompt}] + self.short_term_memory

        # 调用DeepSeek API（使用优化的参数）
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_for_api,
                timeout=get_timeout('deepseek'),
                temperature=fast_config.API_CONFIG['temperature'],
                max_tokens=fast_config.API_CONFIG['max_tokens']
            )
            assistant_response = response.choices[0].message.content
        except Exception as e:
            return "抱歉，我现在有点忙，请稍后再试。"

        # 添加助手回复到短期记忆
        self.short_term_memory.append({"role": "assistant", "content": assistant_response})

        # 添加对话轮次到记忆树（使用批处理）
        should_process = self.memory_tree.add_conversation_turn(user_input, assistant_response)
        
        # 检查是否需要处理对话
        conversation_should_end = False
        if should_process:
            conversation_should_end = self._check_conversation_end_fast(user_input)
        
        # 检查显式告别
        goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话', 'quit', 'exit']
        if any(pattern in user_input.lower() for pattern in goodbye_patterns):
            conversation_should_end = True

        # 处理对话结束
        if conversation_should_end:
            self._finalize_conversation_fast()

        # 批量更新用户画像
        self._conversation_count += 1
        if self._conversation_count % get_batch_size('memory') == 0:
            self._batch_update_profile()

        return assistant_response

    def _fast_retrieve_memories(self, user_input: str) -> List[Dict[str, Any]]:
        """快速检索记忆"""
        # 检查缓存
        cache_key = f"memories_{fast_hash(user_input)}"
        cached_memories = global_cache.get(cache_key)
        if cached_memories is not None:
            return cached_memories
        
        # 检索记忆
        retrieved_memories = self.memory_tree.search(
            user_input, 
            similarity_threshold=fast_config.MEMORY_CONFIG['similarity_threshold'],
            max_results=fast_config.MEMORY_CONFIG['max_search_results']
        )
        
        # 缓存结果
        global_cache.put(cache_key, retrieved_memories)
        
        return retrieved_memories

    def _build_optimized_prompt(self, retrieved_memories: List[Dict[str, Any]]) -> str:
        """构建优化的系统提示词"""
        # 使用缓存的模板
        if self._system_prompt_template is None:
            template_str = (
                "你是一个养老机构的智能协助机器人，你的名字叫小助。"
                "当前对话对象：$current_user\n"
                "$profile_info\n"
                "$memory_context\n"
                "特点：语言通俗易懂，回复简洁不超过50字，语气亲切温和。"
            )
            self._system_prompt_template = FastStringProcessor.format_with_template(
                "system_prompt", template_str
            )
        
        # 格式化记忆上下文（简化版）
        memory_context = ""
        if retrieved_memories:
            memory_lines = []
            for i, memory in enumerate(retrieved_memories[:2], 1):  # 只取前2个
                memory_lines.append(f"{i}. {memory['summary']}")
            memory_context = f"相关记忆:\n{chr(10).join(memory_lines)}"
        
        # 获取简化的用户画像
        profile_info = self._get_cached_profile_info()
        
        return FastStringProcessor.format_with_template(
            "system_prompt_final",
            self._system_prompt_template,
            current_user=self.current_person_profile.person_name,
            profile_info=profile_info,
            memory_context=memory_context
        )

    def _get_cached_profile_info(self) -> str:
        """获取缓存的用户画像信息"""
        cache_key = f"profile_info_{self.current_person_profile.person_name}"
        cached_info = self._profile_format_cache.get(cache_key)
        if cached_info is not None:
            return cached_info
        
        # 简化的画像格式
        attributes = self.current_person_profile.attributes
        info_parts = []
        
        if attributes.get('age'):
            info_parts.append(f"年龄: {attributes['age']}")
        if attributes.get('occupation'):
            info_parts.append(f"职业: {attributes['occupation']}")
        if attributes.get('hobbies'):
            info_parts.append(f"爱好: {', '.join(attributes['hobbies'][:2])}")  # 只显示前2个
        
        profile_info = f"用户: {attributes['name']}"
        if info_parts:
            profile_info += f" ({', '.join(info_parts)})"
        
        # 缓存结果
        self._profile_format_cache.put(cache_key, profile_info)
        
        return profile_info

    def _manage_context_length(self):
        """管理对话上下文长度"""
        max_turns = fast_config.CONVERSATION_CONFIG['max_conversation_turns']
        if len(self.short_term_memory) > max_turns * 2:
            # 保留最近的对话轮次
            self.short_term_memory = self.short_term_memory[-(max_turns * 2):]

    def _check_conversation_end_fast(self, user_input: str) -> bool:
        """快速检查对话是否结束"""
        # 简化的结束检查
        end_keywords = ['再见', 'bye', '结束', '88', '拜拜']
        return any(keyword in user_input.lower() for keyword in end_keywords)

    def _finalize_conversation_fast(self):
        """快速完成对话"""
        if not self.current_person_profile or not self.memory_tree.current_conversation:
            return []
        
        # 生成记忆节点
        memory_nodes = self.memory_tree.finalize_conversation(
            llm_client=self.client, 
            person_name=self.current_person_profile.person_name
        )
        
        # 批量保存记忆
        if memory_nodes:
            should_save = memory_batch_processor.add(self.memory_file_path)
            if should_save:
                self._batch_save_memories()
        
        # 更新用户画像
        self._batch_update_profile()
        
        return memory_nodes

    def _batch_save_memories(self):
        """批量保存记忆"""
        try:
            self.memory_tree.save(self.memory_file_path)
        except Exception:
            pass  # 简化错误处理

    def _batch_update_profile(self):
        """批量更新用户画像"""
        if not fast_config.FAST_MODE.get('async_operations', False):
            return  # 跳过实时画像更新以提高速度
        
        # 异步更新画像
        if self.current_person_profile and hasattr(self.current_person_profile, '_needs_save'):
            if self.current_person_profile._needs_save:
                self.current_person_profile.save_profile()

    @PerformanceOptimizer.timing_decorator("end_conversation")
    def end_conversation(self):
        """结束对话"""
        if self.current_person_profile and self.memory_tree.current_conversation:
            memory_nodes = self._finalize_conversation_fast()
            
            # 重置状态
            self.current_person_profile = None
            self.short_term_memory = []
            self._conversation_count = 0
            
            return memory_nodes
        else:
            return []

    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        memory_stats = self.memory_tree.get_stats()
        perf_stats = PerformanceOptimizer.get_performance_stats()
        
        return {
            'memory_tree_stats': memory_stats,
            'performance_stats': perf_stats,
            'conversation_count': self._conversation_count,
            'cache_stats': {
                'global_cache_size': global_cache.size(),
                'profile_cache_size': self._profile_format_cache.size(),
            },
            'config_info': {
                'fast_mode_enabled': fast_config.FAST_MODE.get('cache_enabled', False),
                'batch_size': get_batch_size('memory'),
                'skip_checks': list(fast_config.SKIP_CHECKS.keys())
            }
        }

    def clear_caches(self):
        """清理缓存"""
        global_cache.clear()
        self._profile_format_cache.clear()
        PerformanceOptimizer.clear_performance_stats()

    # 为了兼容性保留原有方法（简化版本）
    def repair_embeddings(self):
        """修复embeddings（简化版本）"""
        if should_skip_check('embedding_validation'):
            return 0  # 跳过修复
        
        # 简化的修复逻辑
        return 0

if __name__ == "__main__":
    # 测试快速记忆代理
    agent = FastMemoryAgent(
        deepseek_api_key="sk-fdabadb2973b4795b2444da60e75152f",
        deepseek_base_url="https://api.deepseek.com",
        memory_file_path="/tmp/test_fast_memory.json"
    )
    
    # 测试对话
    agent.start_chat("张三")
    
    response1 = agent.chat("你好，我喜欢摄影")
    print("回复1:", response1)
    
    response2 = agent.chat("你能推荐一些相机吗？")
    print("回复2:", response2)
    
    # 获取统计信息
    stats = agent.get_stats()
    print("统计信息:", json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 结束对话
    agent.end_conversation()