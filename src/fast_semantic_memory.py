#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速语义记忆系统 - 优化版本的记忆树实现
重点优化：哈希索引、批量处理、缓存机制、简化算法
"""

import uuid
import json
import time
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from collections import defaultdict
import threading

# 导入优化工具
from performance_utils import (
    PerformanceOptimizer, FastStringProcessor, MemoryCache, 
    BatchProcessor, global_cache, embedding_cache, fast_hash
)
from optimized_config import fast_config, should_skip_check, get_batch_size
from Embedding import get_embp_embedding, parser_Message

class FastMemoryNode:
    """
    优化的记忆节点 - 使用哈希索引和缓存
    """
    def __init__(self, summary: str, embedding: Optional[List[float]] = None, 
                 children: Optional[List['FastMemoryNode']] = None, 
                 keywords: Optional[List[str]] = None, 
                 keywords_embedding: Optional[List[float]] = None):
        self.node_id: str = str(uuid.uuid4())
        self.timestamp: datetime = datetime.utcnow()
        self.summary: str = summary
        
        # 优化：只存储关键词embedding，不存储摘要embedding
        self.embedding: Optional[List[float]] = []  # 保留兼容性
        self.keywords: List[str] = keywords if keywords is not None else []
        self.keywords_embedding: Optional[List[float]] = keywords_embedding if keywords_embedding is not None else []
        self.children: List['FastMemoryNode'] = children if children is not None else []
        
        # 新增：快速访问的哈希值
        self.content_hash: str = fast_hash(summary)
        self.keywords_hash: str = fast_hash(' '.join(self.keywords)) if self.keywords else ""

    def __repr__(self) -> str:
        return f"FastMemoryNode(id={self.node_id[:8]}, summary='{self.summary[:30]}...', children={len(self.children)})"

    def add_child(self, child_node: 'FastMemoryNode'):
        """添加子节点"""
        self.children.append(child_node)

    def remove_child(self, node_id: str) -> bool:
        """移除子节点"""
        initial_len = len(self.children)
        self.children = [child for child in self.children if child.node_id != node_id]
        return len(self.children) < initial_len

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "embedding": [],  # 不保存摘要embedding
            "keywords": self.keywords,
            "keywords_embedding": self.keywords_embedding,
            "children": [child.to_dict() for child in self.children],
            "content_hash": self.content_hash,
            "keywords_hash": self.keywords_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FastMemoryNode':
        """从字典创建节点"""
        ts_str = data['timestamp'].replace('Z', '+00:00')
        node = cls(
            summary=data['summary'], 
            embedding=[],  # 不加载摘要embedding
            keywords=data.get('keywords', []),
            keywords_embedding=data.get('keywords_embedding', [])
        )
        node.node_id = data['node_id']
        node.timestamp = datetime.fromisoformat(ts_str)
        node.children = [cls.from_dict(child_data) for child_data in data['children']]
        
        # 重新计算哈希值（向后兼容）
        node.content_hash = data.get('content_hash', fast_hash(node.summary))
        node.keywords_hash = data.get('keywords_hash', fast_hash(' '.join(node.keywords)) if node.keywords else "")
        
        return node

class FastMemoryTree:
    """
    优化的记忆树 - 使用哈希索引和批量处理
    """
    def __init__(self, root: FastMemoryNode = None, embedding_config: Dict[str, str] = None):
        if root:
            self.root = root
        else:
            self.root = FastMemoryNode(summary="Robot's Core Memory")
        
        # embedding配置
        self.embedding_config = embedding_config or {
            'APPID': 'b32f165e',
            'APISecret': 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
            'APIKEY': 'bf4caffa0bd087acc04cd63d0ee27fc5'
        }
        
        # 优化：哈希索引表
        self.node_index: Dict[str, FastMemoryNode] = {}  # node_id -> node
        self.content_index: Dict[str, List[FastMemoryNode]] = defaultdict(list)  # content_hash -> nodes
        self.keyword_index: Dict[str, List[FastMemoryNode]] = defaultdict(list)  # keyword -> nodes
        
        # 构建索引
        self._build_indexes()
        
        # 对话会话管理
        self.current_conversation = []
        self.conversation_threshold = get_batch_size('memory')
        
        # 批处理器
        self.save_batch_processor = BatchProcessor(
            batch_size=get_batch_size('memory'), 
            flush_interval=fast_config.BATCH_CONFIG['max_batch_wait_time']
        )
        
        # 线程锁
        self._lock = threading.Lock()

    def _build_indexes(self):
        """构建哈希索引"""
        def _index_node(node: FastMemoryNode):
            # 节点ID索引
            self.node_index[node.node_id] = node
            
            # 内容哈希索引
            if node.content_hash:
                self.content_index[node.content_hash].append(node)
            
            # 关键词索引
            for keyword in node.keywords:
                self.keyword_index[keyword].append(node)
            
            # 递归索引子节点
            for child in node.children:
                _index_node(child)
        
        # 清空现有索引
        self.node_index.clear()
        self.content_index.clear()
        self.keyword_index.clear()
        
        # 重建索引
        _index_node(self.root)

    @PerformanceOptimizer.timing_decorator("fast_extract_keywords")
    def _fast_extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        快速关键词提取 - 使用缓存和简化算法
        """
        if not text:
            return []
        
        # 检查缓存
        cache_key = f"keywords_{fast_hash(text)}_{max_keywords}"
        cached_result = global_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 使用快速字符串处理器
        keywords = FastStringProcessor.fast_extract_keywords(text, max_keywords)
        
        # 缓存结果
        global_cache.put(cache_key, keywords)
        
        return keywords

    @PerformanceOptimizer.timing_decorator("fast_generate_embedding")
    def _fast_generate_embedding(self, text: str, max_retries: int = 2) -> List[float]:
        """
        快速生成embedding - 使用缓存和减少重试
        """
        if not text:
            return []
        
        # 检查是否跳过embedding验证
        if should_skip_check('embedding_validation'):
            max_retries = 1
        
        # 检查缓存
        cache_key = f"emb_{fast_hash(text)}"
        cached_embedding = embedding_cache.get(cache_key)
        if cached_embedding is not None:
            return cached_embedding
        
        # 生成embedding
        for attempt in range(max_retries):
            try:
                desc = {"messages": [{"content": text, "role": "user"}]}
                response = get_embp_embedding(
                    desc,
                    appid=self.embedding_config['APPID'],
                    apikey=self.embedding_config['APIKEY'],
                    apisecret=self.embedding_config['APISecret']
                )
                embedding_vector = parser_Message(response)
                result = embedding_vector.tolist() if hasattr(embedding_vector, 'tolist') else list(embedding_vector)
                
                if result and len(result) > 0:
                    # 缓存结果
                    embedding_cache.put(cache_key, result)
                    return result
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    # 最后一次尝试失败，返回空embedding
                    pass
                else:
                    time.sleep(1)  # 短暂等待
        
        return []

    def _update_indexes_for_node(self, node: FastMemoryNode):
        """更新单个节点的索引"""
        with self._lock:
            # 更新各种索引
            self.node_index[node.node_id] = node
            
            if node.content_hash:
                if node not in self.content_index[node.content_hash]:
                    self.content_index[node.content_hash].append(node)
            
            for keyword in node.keywords:
                if node not in self.keyword_index[keyword]:
                    self.keyword_index[keyword].append(node)

    @PerformanceOptimizer.timing_decorator("add_conversation_turn")
    def add_conversation_turn(self, user_input: str, assistant_response: str):
        """
        添加对话轮次 - 使用批处理
        """
        self.current_conversation.append({
            'user': user_input,
            'assistant': assistant_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # 检查是否需要批处理
        if len(self.current_conversation) >= self.conversation_threshold:
            return True  # 需要处理
        return False

    @PerformanceOptimizer.timing_decorator("fast_finalize_conversation")
    def finalize_conversation(self, llm_client=None, person_name: str = ""):
        """
        快速完成对话处理 - 使用批量embedding和简化处理
        """
        if not self.current_conversation:
            return []
        
        # 格式化对话
        conversation_text = ""
        for turn in self.current_conversation:
            conversation_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        
        # 提取记忆点
        if llm_client:
            memory_points = self._extract_memory_points_fast(conversation_text, llm_client, person_name)
        else:
            memory_points = [f"Conversation with {person_name}: {conversation_text[:100]}..."]
        
        # 批量生成关键词和embedding
        memory_nodes = []
        keywords_list = []
        
        # 第一步：批量提取关键词
        for memory_point in memory_points:
            keywords = self._fast_extract_keywords(memory_point, max_keywords=5)
            if person_name and person_name not in keywords:
                keywords.insert(0, person_name)
            keywords_list.append(keywords)
        
        # 第二步：批量生成embedding
        embedding_texts = [" ".join(keywords) for keywords in keywords_list if keywords]
        embeddings = self._batch_generate_embeddings(embedding_texts)
        
        # 第三步：创建记忆节点
        for i, memory_point in enumerate(memory_points):
            keywords = keywords_list[i]
            keywords_embedding = embeddings[i] if i < len(embeddings) else []
            
            memory_node = FastMemoryNode(
                summary=memory_point,
                embedding=[],  # 不生成摘要embedding
                keywords=keywords,
                keywords_embedding=keywords_embedding
            )
            
            # 添加到树并更新索引
            self.root.add_child(memory_node)
            self._update_indexes_for_node(memory_node)
            memory_nodes.append(memory_node)
        
        # 清空当前对话
        self.current_conversation = []
        
        return memory_nodes

    def _batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成embedding - 优化网络调用
        """
        embeddings = []
        for text in texts:
            if text.strip():
                embedding = self._fast_generate_embedding(text)
                embeddings.append(embedding)
            else:
                embeddings.append([])
        return embeddings

    def _extract_memory_points_fast(self, conversation_text: str, llm_client, person_name: str) -> List[str]:
        """
        快速提取记忆点 - 简化prompt和处理
        """
        # 简化的prompt
        prompt = (
            f"提取与{person_name}对话的关键记忆点，每行一个，简洁明了：\n"
            f"{conversation_text}\n\n"
            "记忆点："
        )
        
        try:
            response = llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 低随机性
                max_tokens=fast_config.API_CONFIG['max_tokens']
            )
            
            memory_points_text = response.choices[0].message.content.strip()
            memory_points = []
            
            for line in memory_points_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 简化清理
                    cleaned_line = line.lstrip('0123456789.-• ').strip()
                    if cleaned_line:
                        memory_points.append(cleaned_line)
            
            return memory_points or [f"与{person_name}进行了对话交流"]
            
        except Exception as e:
            # 简化错误处理
            return [f"与{person_name}进行了对话交流"]

    @PerformanceOptimizer.timing_decorator("fast_search")
    def search(self, query_text: str, similarity_threshold: float = 0.6, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        快速搜索 - 使用哈希索引和缓存
        """
        # 检查缓存
        cache_key = f"search_{fast_hash(query_text)}_{similarity_threshold}_{max_results}"
        cached_result = global_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 提取查询关键词
        query_keywords = self._fast_extract_keywords(query_text, max_keywords=6)
        if not query_keywords:
            return []
        
        # 使用关键词索引快速查找候选节点
        candidate_nodes = set()
        for keyword in query_keywords:
            if keyword in self.keyword_index:
                candidate_nodes.update(self.keyword_index[keyword])
        
        if not candidate_nodes:
            return []
        
        # 生成查询embedding
        query_keywords_text = " ".join(query_keywords)
        query_embedding = self._fast_generate_embedding(query_keywords_text)
        
        if not query_embedding:
            return []
        
        # 计算相似度
        results = []
        for node in candidate_nodes:
            if node.summary == "Robot's Core Memory":
                continue
            
            if node.keywords_embedding:
                similarity = self._cosine_similarity(query_embedding, node.keywords_embedding)
                if similarity >= similarity_threshold:
                    decay_factor = self._fast_memory_decay(node)
                    final_score = similarity * decay_factor
                    
                    results.append({
                        'node_id': node.node_id,
                        'summary': node.summary,
                        'keywords': node.keywords,
                        'similarity': similarity,
                        'decay_factor': decay_factor,
                        'final_score': final_score,
                        'timestamp': node.timestamp.isoformat()
                    })
        
        # 排序并限制结果
        results.sort(key=lambda x: x['final_score'], reverse=True)
        results = results[:max_results]
        
        # 缓存结果
        global_cache.put(cache_key, results)
        
        return results

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """快速余弦相似度计算"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = sum(a * a for a in vec1) ** 0.5
        norm_b = sum(b * b for b in vec2) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)

    def _fast_memory_decay(self, node: FastMemoryNode) -> float:
        """快速记忆衰减计算"""
        now = datetime.utcnow()
        age_days = (now - node.timestamp).days
        return max(0.1, 0.95 ** age_days)

    def find_node(self, node_id: str) -> Optional[FastMemoryNode]:
        """使用索引快速查找节点"""
        return self.node_index.get(node_id)

    def add_memory(self, text: str, parent_node_id: Optional[str] = None):
        """
        添加记忆 - 使用批处理和索引
        """
        summary = text
        keywords = self._fast_extract_keywords(summary)
        
        # 生成关键词embedding
        keywords_text = " ".join(keywords) if keywords else ""
        keywords_embedding = self._fast_generate_embedding(keywords_text) if keywords_text else []

        new_node = FastMemoryNode(
            summary=summary,
            embedding=[],  # 不生成摘要embedding
            keywords=keywords,
            keywords_embedding=keywords_embedding
        )

        # 查找父节点
        parent = self.find_node(parent_node_id) if parent_node_id else self.root
        if parent:
            parent.add_child(new_node)
        else:
            self.root.add_child(new_node)
        
        # 更新索引
        self._update_indexes_for_node(new_node)
        
        return new_node

    @PerformanceOptimizer.timing_decorator("fast_save")
    def save(self, file_path: str):
        """快速保存 - 支持异步"""
        if fast_config.FAST_MODE.get('async_operations', False):
            # 异步保存
            threading.Thread(target=self._save_sync, args=(file_path,), daemon=True).start()
        else:
            self._save_sync(file_path)

    def _save_sync(self, file_path: str):
        """同步保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.root.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 简化错误处理
            pass

    @staticmethod
    def load(file_path: str, embedding_config: Dict[str, str] = None) -> 'FastMemoryTree':
        """快速加载"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                root_node = FastMemoryNode.from_dict(data)
                tree = FastMemoryTree(root=root_node, embedding_config=embedding_config)
                return tree
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return FastMemoryTree(embedding_config=embedding_config)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_nodes': len(self.node_index),
            'content_index_size': len(self.content_index),
            'keyword_index_size': len(self.keyword_index),
            'current_conversation_turns': len(self.current_conversation),
            'cache_stats': {
                'global_cache_size': global_cache.size(),
                'embedding_cache_size': embedding_cache.size(),
            }
        }

if __name__ == "__main__":
    # 测试快速记忆树
    config = {
        'APPID': 'b32f165e',
        'APISecret': 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
        'APIKEY': 'bf4caffa0bd087acc04cd63d0ee27fc5'
    }
    
    tree = FastMemoryTree(embedding_config=config)
    
    # 测试添加记忆
    tree.add_memory("用户张三喜欢摄影")
    tree.add_memory("张三今天询问了相机推荐")
    
    # 测试搜索
    results = tree.search("张三 摄影")
    print("搜索结果:", results)
    
    # 打印统计信息
    stats = tree.get_stats()
    print("统计信息:", stats)
    
    # 打印性能统计
    perf_stats = PerformanceOptimizer.get_performance_stats()
    print("性能统计:", perf_stats)