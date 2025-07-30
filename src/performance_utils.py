#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化工具类 - 提供缓存、预编译和性能监控功能
"""

import re
import time
import functools
import gc
from typing import Dict, Any, Callable, Optional
from string import Template
import threading
import weakref

class PerformanceOptimizer:
    """
    性能优化工具类，提供各种性能优化功能
    """
    
    # 预编译的正则表达式
    COMPILED_PATTERNS = {
        'stop_words': re.compile(r'\b(?:的|了|在|是|有|和|就|不|都|一|一个|上|也|很|到|说|要|去|会|着|没有|看|好|这|那|还|把|做|让|给|我|你|他|她|我们|你们|他们|自己|啊|呢|吧|哦|嗯|么|吗|啦|非常|特别|太|比较|其实|突然|什么|怎么|为什么|谁|哪里|多少|怎样|如何|今天|明天|周末|现在|早上|晚上|这里|那里|附近|用户|对话|交流|聊天|询问|回答|提到|表示|认为|觉得|请问|听说|记得|要求|这个|那个|一些|几次|一天|一起|得|点|但|真的|已经|可以|想|还是|只是|应该|大概|也许|可能|如果|然后|不过|因为|所以|但是|而且|或者|还有|时候|之后|之前|刚才|正在|总是|经常|每次|一直|马上|快点|慢慢|几乎|完全|挺|稍微|有点|更加|越来越|最好|必须|一定|不用|不能|不要|再来|一下|一会儿|先|后|再|又|这样|那样|这么|那么|怎么样|什么样|这种|那种|其他|另外|全部|整个|每个|各位|大家|所有人|一切|所有|任何|某|某些|某个|某位|某事|某物|别人|人家|本人|对方|双方|彼此|之间|其中|当中|中间|之内|之外|以上|以下|以内|以外|前面|后面|左边|右边|旁边|对面|周围|附近|之中|刚|刚从|回来|真|真是|美|美了)\b'),
        'punctuation': re.compile(r'[！。，、；：？""''（）【】《》]'),
        'chinese_chars': re.compile(r'[\u4e00-\u9fff]{2,6}'),
        'whitespace': re.compile(r'\s+'),
    }
    
    # 缓存的字符串模板
    TEMPLATE_CACHE = {}
    
    # 性能监控数据
    _performance_stats = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_template(cls, name: str, template_str: str) -> Template:
        """
        获取缓存的字符串模板
        """
        if name not in cls.TEMPLATE_CACHE:
            cls.TEMPLATE_CACHE[name] = Template(template_str)
        return cls.TEMPLATE_CACHE[name]
    
    @classmethod
    def timing_decorator(cls, func_name: Optional[str] = None):
        """
        性能监控装饰器
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed = time.time() - start_time
                    cls._record_timing(name, elapsed)
            
            return wrapper
        return decorator
    
    @classmethod
    def _record_timing(cls, func_name: str, elapsed_time: float):
        """
        记录函数执行时间
        """
        with cls._lock:
            if func_name not in cls._performance_stats:
                cls._performance_stats[func_name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'avg_time': 0.0,
                    'max_time': 0.0
                }
            
            stats = cls._performance_stats[func_name]
            stats['count'] += 1
            stats['total_time'] += elapsed_time
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['max_time'] = max(stats['max_time'], elapsed_time)
    
    @classmethod
    def get_performance_stats(cls) -> Dict[str, Any]:
        """
        获取性能统计数据
        """
        with cls._lock:
            return cls._performance_stats.copy()
    
    @classmethod
    def clear_performance_stats(cls):
        """
        清空性能统计数据
        """
        with cls._lock:
            cls._performance_stats.clear()
    
    @staticmethod
    def optimize_memory():
        """
        内存优化工具
        """
        # 强制垃圾回收
        gc.collect()
        
        # 清理弱引用
        for obj in list(weakref.WeakSet()):
            try:
                del obj
            except:
                pass

class FastStringProcessor:
    """
    快速字符串处理工具
    """
    
    @staticmethod
    def fast_extract_keywords(text: str, max_keywords: int = 6) -> list:
        """
        快速关键词提取（简化版本）
        """
        if not text:
            return []
        
        # 使用预编译的正则表达式
        patterns = PerformanceOptimizer.COMPILED_PATTERNS
        
        # 移除标点符号
        text_cleaned = patterns['punctuation'].sub(' ', text)
        
        # 移除停用词（简化版）
        text_cleaned = patterns['stop_words'].sub(' ', text_cleaned)
        
        # 规范化空白字符
        text_cleaned = patterns['whitespace'].sub(' ', text_cleaned).strip()
        
        # 提取中文关键词
        keywords = patterns['chinese_chars'].findall(text_cleaned)
        
        # 去重并限制数量
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen and len(unique_keywords) < max_keywords:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    @staticmethod
    def format_with_template(template_name: str, template_str: str, **kwargs) -> str:
        """
        使用缓存的模板格式化字符串
        """
        template = PerformanceOptimizer.get_template(template_name, template_str)
        return template.safe_substitute(kwargs)

class MemoryCache:
    """
    内存缓存管理器
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Any:
        """
        获取缓存项
        """
        with self._lock:
            if key in self.cache:
                # 更新访问顺序
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any):
        """
        添加缓存项
        """
        with self._lock:
            if key in self.cache:
                # 更新已存在的项
                self.cache[key] = value
                self.access_order.remove(key)
                self.access_order.append(key)
            else:
                # 添加新项
                if len(self.cache) >= self.max_size:
                    # 移除最少使用的项
                    oldest_key = self.access_order.pop(0)
                    del self.cache[oldest_key]
                
                self.cache[key] = value
                self.access_order.append(key)
    
    def clear(self):
        """
        清空缓存
        """
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
    
    def size(self) -> int:
        """
        获取缓存大小
        """
        return len(self.cache)

class BatchProcessor:
    """
    批量处理器
    """
    
    def __init__(self, batch_size: int = 10, flush_interval: float = 60.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
        self._lock = threading.Lock()
    
    def add(self, item: Any) -> bool:
        """
        添加项到批处理队列
        返回是否需要立即处理
        """
        with self._lock:
            self.batch.append(item)
            current_time = time.time()
            
            # 检查是否需要刷新
            should_flush = (
                len(self.batch) >= self.batch_size or
                (current_time - self.last_flush) >= self.flush_interval
            )
            
            return should_flush
    
    def get_batch(self) -> list:
        """
        获取当前批次并清空队列
        """
        with self._lock:
            batch = self.batch.copy()
            self.batch.clear()
            self.last_flush = time.time()
            return batch
    
    def force_flush(self) -> list:
        """
        强制刷新并返回批次
        """
        return self.get_batch()

# 全局缓存实例
global_cache = MemoryCache(max_size=500)
embedding_cache = MemoryCache(max_size=100)
template_cache = MemoryCache(max_size=50)

# 批处理实例
memory_batch_processor = BatchProcessor(batch_size=3, flush_interval=180.0)  # 3个记忆或3分钟
file_cleanup_batch = BatchProcessor(batch_size=10, flush_interval=300.0)      # 10个文件或5分钟

def fast_hash(text: str) -> str:
    """
    快速字符串哈希（用于缓存键）
    """
    return str(hash(text) % 1000000)

def skip_check(check_name: str) -> bool:
    """
    检查是否跳过某个验证步骤
    """
    from optimized_config import FastConfig
    return FastConfig.SKIP_CHECKS.get(check_name, False)

if __name__ == "__main__":
    # 测试性能工具
    @PerformanceOptimizer.timing_decorator("test_function")
    def test_function():
        time.sleep(0.1)
        return "test"
    
    # 运行测试
    for _ in range(5):
        test_function()
    
    # 打印性能统计
    stats = PerformanceOptimizer.get_performance_stats()
    print("性能统计:", stats)
    
    # 测试关键词提取
    keywords = FastStringProcessor.fast_extract_keywords("今天天气很好，我想去公园散步")
    print("关键词:", keywords)