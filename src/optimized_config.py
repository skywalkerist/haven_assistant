#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化配置文件 - 定义所有性能优化相关的配置参数
"""

import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class FastConfig:
    """
    快速模式配置类
    """
    
    # =============================================================================
    # 性能优化开关
    # =============================================================================
    
    # 跳过的检查项
    SKIP_CHECKS = {
        'audio_file_size': True,        # 跳过音频文件大小检查
        'audio_file_exists': True,      # 跳过音频文件存在性检查
        'service_health': True,         # 跳过服务健康检查
        'detailed_validation': True,    # 跳过详细验证
        'api_response_validation': True, # 跳过API响应详细验证
        'embedding_validation': True,   # 跳过embedding有效性检查
        'memory_tree_integrity': True,  # 跳过记忆树完整性检查
    }
    
    # 批量处理配置
    BATCH_CONFIG = {
        'memory_save_interval': 3,      # 3次对话后保存记忆
        'file_cleanup_interval': 300,   # 5分钟清理一次临时文件
        'embedding_batch_size': 5,      # 批量生成embedding的大小
        'max_batch_wait_time': 180,     # 最大批处理等待时间（秒）
    }
    
    # 缓存配置
    CACHE_CONFIG = {
        'embedding_cache_size': 100,    # embedding缓存大小
        'template_cache_size': 50,      # 字符串模板缓存大小
        'keyword_cache_size': 200,      # 关键词缓存大小
        'response_cache_size': 30,      # 响应缓存大小
        'cache_ttl': 3600,             # 缓存生存时间（秒）
    }
    
    # 简化的处理模式
    FAST_MODE = {
        'minimal_logging': True,        # 最小化日志输出
        'simple_error_handling': True,  # 简化错误处理
        'cache_enabled': True,          # 启用缓存
        'async_operations': True,       # 启用异步操作
        'memory_optimization': True,    # 启用内存优化
    }
    
    # =============================================================================
    # 音频处理优化
    # =============================================================================
    
    AUDIO_CONFIG = {
        'sample_rate': 16000,           # 采样率（降低以提高速度）
        'chunk_size': 1024,             # 音频块大小
        'channels': 1,                  # 单声道
        'format': 'wav',                # 音频格式
        'silence_threshold': 800,       # 静音阈值
        'silence_duration': 1.0,        # 静音持续时间（秒）
        'max_recording_time': 10,       # 最大录音时间（秒）
        'use_memory_buffer': True,      # 使用内存缓冲而非文件
    }
    
    # =============================================================================
    # API调用优化
    # =============================================================================
    
    API_CONFIG = {
        # 通用API设置
        'request_timeout': 8,           # 请求超时时间（秒）
        'max_retries': 2,               # 最大重试次数
        'retry_delay': 1,               # 重试延迟（秒）
        'connection_pool_size': 5,      # 连接池大小
        
        # DeepSeek API优化
        'deepseek_timeout': 10,         # DeepSeek API超时
        'max_context_length': 3000,     # 最大上下文长度
        'temperature': 0.3,             # 降低随机性提高速度
        'max_tokens': 200,              # 限制响应长度
        
        # 科大讯飞ASR优化
        'asr_timeout': 8,               # ASR超时时间
        'asr_format': 'wav',            # 音频格式
        'asr_rate': 16000,              # 采样率
        
        # TTS优化
        'tts_timeout': 6,               # TTS超时时间
        'tts_speed': 1.2,               # 语音速度（加快）
        'tts_volume': 80,               # 音量
    }
    
    # =============================================================================
    # 记忆系统优化
    # =============================================================================
    
    MEMORY_CONFIG = {
        # 记忆检索优化
        'max_search_results': 3,        # 最大搜索结果数
        'similarity_threshold': 0.6,    # 相似度阈值
        'search_timeout': 2,            # 搜索超时（秒）
        'use_keyword_index': True,      # 使用关键词索引
        'max_keywords_per_memory': 5,   # 每个记忆最大关键词数
        
        # 记忆存储优化
        'auto_save_enabled': True,      # 启用自动保存
        'save_async': True,             # 异步保存
        'compress_embeddings': False,   # 压缩embedding（可能影响精度）
        'max_memory_nodes': 1000,       # 最大记忆节点数
        
        # embedding优化
        'embedding_cache_enabled': True, # 启用embedding缓存
        'embedding_batch_enabled': True, # 启用批量embedding
        'embedding_retry_limit': 2,     # embedding生成重试限制
    }
    
    # =============================================================================
    # 文件系统优化
    # =============================================================================
    
    FILE_CONFIG = {
        # 临时文件管理
        'use_memory_temp': True,        # 优先使用内存临时存储
        'temp_dir': '/tmp/fast_agent',  # 临时文件目录
        'auto_cleanup': True,           # 自动清理
        'cleanup_interval': 300,        # 清理间隔（秒）
        'max_temp_files': 20,           # 最大临时文件数
        
        # 文件操作优化
        'async_file_ops': True,         # 异步文件操作
        'file_buffer_size': 8192,       # 文件缓冲区大小
        'sync_writes': False,           # 禁用同步写入（提高速度）
    }
    
    # =============================================================================
    # 系统资源优化
    # =============================================================================
    
    SYSTEM_CONFIG = {
        # 内存管理
        'gc_interval': 60,              # 垃圾回收间隔（秒）
        'max_memory_usage': 512,        # 最大内存使用（MB）
        'memory_warning_threshold': 400, # 内存警告阈值（MB）
        
        # 线程池配置
        'max_workers': 3,               # 最大工作线程数
        'thread_timeout': 30,           # 线程超时时间
        
        # 性能监控
        'performance_monitoring': True,  # 启用性能监控
        'stats_collection_interval': 300, # 统计收集间隔（秒）
    }
    
    # =============================================================================
    # 对话流程优化
    # =============================================================================
    
    CONVERSATION_CONFIG = {
        # 对话轮次限制
        'max_conversation_turns': 15,   # 最大对话轮数（从20减少）
        'quick_response_mode': True,    # 快速响应模式
        'parallel_processing': True,    # 并行处理
        
        # 响应生成优化
        'response_cache_enabled': True, # 启用响应缓存
        'template_based_response': True, # 基于模板的响应
        'simple_profile_format': True,  # 简化用户画像格式
        
        # 工具调用优化
        'tool_timeout': 5,              # 工具调用超时
        'async_tool_execution': True,   # 异步工具执行
    }
    
    # =============================================================================
    # 人脸识别优化
    # =============================================================================
    
    FACE_RECOGNITION_CONFIG = {
        # 搜索优化
        'search_stabilization_time': 0.8, # 从1.2秒减少到0.8秒
        'max_search_angles': 3,          # 最大搜索角度数量
        'search_angle_step': 45,         # 搜索角度步长
        'recognition_timeout': 2,        # 每个角度的识别超时
        
        # 识别参数
        'confidence_threshold': 0.6,     # 识别置信度阈值
        'max_recognition_attempts': 3,   # 最大识别尝试次数
        'fast_scan_mode': True,          # 快速扫描模式
    }
    
    # =============================================================================
    # 环境变量覆盖
    # =============================================================================
    
    @classmethod
    def from_env(cls) -> 'FastConfig':
        """
        从环境变量创建配置（可以覆盖默认值）
        """
        config = cls()
        
        # 检查环境变量覆盖
        if os.getenv('FAST_MODE', '').lower() == 'true':
            config.FAST_MODE['minimal_logging'] = True
            config.FAST_MODE['simple_error_handling'] = True
        
        if os.getenv('SKIP_AUDIO_CHECK', '').lower() == 'true':
            config.SKIP_CHECKS['audio_file_size'] = True
            config.SKIP_CHECKS['audio_file_exists'] = True
        
        if os.getenv('BATCH_SIZE'):
            try:
                batch_size = int(os.getenv('BATCH_SIZE'))
                config.BATCH_CONFIG['memory_save_interval'] = batch_size
            except ValueError:
                pass
        
        return config
    
    # =============================================================================
    # 性能预设配置
    # =============================================================================
    
    @classmethod
    def get_performance_preset(cls, preset_name: str) -> Dict[str, Any]:
        """
        获取性能预设配置
        """
        presets = {
            'ultra_fast': {
                'skip_all_checks': True,
                'minimal_logging': True,
                'cache_everything': True,
                'batch_size': 1,  # 立即处理
                'timeout_reduction': 0.5,  # 所有超时减半
            },
            'balanced': {
                'skip_some_checks': True,
                'moderate_logging': True,
                'cache_enabled': True,
                'batch_size': 3,
                'timeout_reduction': 0.7,
            },
            'safe': {
                'skip_minimal_checks': True,
                'full_logging': False,
                'cache_enabled': True,
                'batch_size': 5,
                'timeout_reduction': 0.9,
            }
        }
        
        return presets.get(preset_name, presets['balanced'])
    
    # =============================================================================
    # 硬件特定优化
    # =============================================================================
    
    @classmethod
    def get_raspberry_pi_config(cls) -> Dict[str, Any]:
        """
        树莓派4B特定优化配置
        """
        return {
            # 针对ARM架构和有限内存的优化
            'max_memory_usage': 256,      # 限制内存使用
            'thread_pool_size': 2,        # 减少线程数
            'cache_size_multiplier': 0.5, # 减小缓存
            'io_optimization': True,      # 启用I/O优化
            'cpu_optimization': True,     # 启用CPU优化
            'network_optimization': True, # 启用网络优化
        }

# 全局配置实例
fast_config = FastConfig.from_env()

# 便捷函数
def is_fast_mode() -> bool:
    """检查是否启用快速模式"""
    return fast_config.FAST_MODE.get('cache_enabled', False)

def should_skip_check(check_name: str) -> bool:
    """检查是否应该跳过某项检查"""
    return fast_config.SKIP_CHECKS.get(check_name, False)

def get_batch_size(operation: str) -> int:
    """获取指定操作的批处理大小"""
    mapping = {
        'memory': fast_config.BATCH_CONFIG['memory_save_interval'],
        'file_cleanup': fast_config.BATCH_CONFIG['file_cleanup_interval'],
        'embedding': fast_config.BATCH_CONFIG['embedding_batch_size'],
    }
    return mapping.get(operation, 1)

def get_timeout(operation: str) -> int:
    """获取指定操作的超时时间"""
    mapping = {
        'api': fast_config.API_CONFIG['request_timeout'],
        'deepseek': fast_config.API_CONFIG['deepseek_timeout'],
        'asr': fast_config.API_CONFIG['asr_timeout'],
        'tts': fast_config.API_CONFIG['tts_timeout'],
    }
    return mapping.get(operation, 10)

if __name__ == "__main__":
    # 测试配置
    config = FastConfig.from_env()
    print("快速模式配置:")
    print(f"  跳过检查: {config.SKIP_CHECKS}")
    print(f"  批处理配置: {config.BATCH_CONFIG}")
    print(f"  缓存配置: {config.CACHE_CONFIG}")
    print(f"  快速模式: {config.FAST_MODE}")