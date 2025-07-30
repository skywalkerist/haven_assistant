#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速超级智能体 - 优化版本的主智能体系统
重点优化：减少状态检查、内存缓存、批量处理、异步操作
"""

import os
import sys
import time
import threading
import signal
import io
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 添加必要的路径
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
sys.path.append('/home/xuanwu/haven_ws/src')
sys.path.append('/home/xuanwu/snowboy/snowboy-master/examples/Python3')

# 导入语音唤醒模块
import snowboydecoder

# 导入优化的组件
from fast_memory_agent import FastMemoryAgent
from face_recognition_client import FaceRecognitionClient, FaceRecognitionConfig
from audio_recorder import AudioRecorder
from spark_asr import SparkASR
from voice_cloner import VoiceCloner
from move_controller import MoveController
from openai import OpenAI

# 导入性能优化工具
from performance_utils import (
    PerformanceOptimizer, FastStringProcessor, MemoryCache,
    global_cache, file_cleanup_batch, fast_hash
)
from optimized_config import fast_config, should_skip_check, get_timeout, get_batch_size

class AgentState(Enum):
    """智能体状态枚举"""
    LISTENING = "listening"
    WAKE_DETECTED = "wake_detected"
    SCANNING = "scanning"
    SEARCHING = "searching"
    CHATTING = "chatting"

@dataclass
class FastSuperAgentConfig:
    """快速超级智能体配置"""
    # 面部识别配置
    face_config: FaceRecognitionConfig = None
    
    # DeepSeek API配置
    deepseek_api_key: str = "sk-fdabadb2973b4795b2444da60e75152f"
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # 记忆系统配置
    memory_file_path: str = "/home/xuanwu/haven_ws/demos/data/memory_tree.json"
    
    # 语音唤醒配置
    wake_word_model: str = "/home/xuanwu/haven_ws/src/resources/haven.pmdl"
    wake_sensitivity: float = 0.5
    greeting_audio: str = "/home/xuanwu/haven_ws/config/greeting.wav"
    
    # 语音识别配置
    asr_app_id: str = "b32f165e"
    asr_api_key: str = "bf4caffa0bd087acc04cd63d0ee27fc5"
    asr_api_secret: str = "MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0"

    tts_voice_name: str = "default"
    tts_config_path: str = "/home/xuanwu/haven_ws/config/voices.json"
    tts_text_file: str = "/tmp/tts_text.txt"
    tts_audio_file: str = "/tmp/tts_output.wav"
    
    # 机器人移动配置
    robot_host: str = "192.168.10.10"
    robot_port: int = 31001
    
    # 搜索配置（优化）
    search_angle_range: Tuple[int, int] = (-45, 45)  # 减少搜索范围
    search_step: int = 45  # 增加步长
    search_delay: float = fast_config.FACE_RECOGNITION_CONFIG['search_stabilization_time']
    
    # 识别配置
    recognition_confidence_threshold: float = 0.6
    continuous_scan_interval: float = 0.3  # 减少扫描间隔
    unknown_user_timeout: float = 3.0  # 减少超时时间

class FastSuperIntelligentAgent:
    """
    快速超级智能体 - 优化版本
    """
    
    def __init__(self, config: FastSuperAgentConfig):
        self.config = config
        self.state = AgentState.LISTENING
        self.memory_history = ""
        
        # 初始化优化的子系统
        self.face_system = FaceRecognitionClient(config.face_config)
        self.memory_agent = FastMemoryAgent(
            deepseek_api_key=config.deepseek_api_key,
            deepseek_base_url=config.deepseek_base_url,
            memory_file_path=config.memory_file_path
        )
        
        # 初始化DeepSeek客户端
        self.deepseek_client = OpenAI(
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url
        )
        
        # 初始化TTS系统
        self.voice_cloner = VoiceCloner(
            app_id=config.asr_app_id,
            api_key=config.asr_api_key,
            api_secret=config.asr_api_secret,
            text_file=config.tts_text_file,
            output_file=config.tts_audio_file,
            voice_name=config.tts_voice_name,
            config_path=config.tts_config_path
        )
        
        # 初始化移动控制器
        self.move_controller = MoveController(
            host=config.robot_host,
            port=config.robot_port
        )
        self.move_connected = False
        
        # 状态变量
        self.current_user: Optional[str] = None
        self.current_confidence: float = 0.0
        self.last_recognition_time: float = 0.0
        self.is_running: bool = False
        self.recognition_thread: Optional[threading.Thread] = None
        
        # 语音唤醒相关
        self.wake_detector: Optional[snowboydecoder.HotwordDetector] = None
        self.interrupted: bool = False
        
        # 搜索状态
        self.search_current_angle: int = 0
        self.search_direction: int = 1
        self.search_interrupted: bool = False
        
        # 定义工具函数
        self.tools = self._define_tools()
        
        # 性能优化：缓存常用数据
        self._audio_cache = MemoryCache(max_size=20)
        self._response_cache = MemoryCache(max_size=30)
        self._temp_files = []  # 批量清理的临时文件列表
        
        print("🤖 快速智能体初始化完成")
    
    def _define_tools(self):
        """定义DeepSeek可调用的工具函数（完整保留）"""
        return [
            # 人脸识别工具
            {
                "type": "function",
                "function": {
                    "name": "recognize_face",
                    "description": "识别当前用户的人脸",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                }
            },
            # 人脸注册工具
            {
                "type": "function", 
                "function": {
                    "name": "register_face",
                    "description": "注册新用户的人脸，需要用户提供姓名",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_name": {
                                "type": "string",
                                "description": "要注册的用户姓名",
                            }
                        },
                        "required": ["user_name"]
                    },
                }
            },
            # 移动相关工具（简化版本）
            {
                "type": "function",
                "function": {
                    "name": "move_forward",
                    "description": "机器人向前移动指定距离",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "distance": {
                                "type": "number",
                                "description": "前进距离，单位为米",
                            }
                        },
                        "required": ["distance"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_backward", 
                    "description": "机器人向后移动指定距离",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "distance": {
                                "type": "number",
                                "description": "后退距离，单位为米",
                            }
                        },
                        "required": ["distance"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "turn_left",
                    "description": "机器人向左转指定角度",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "angle": {
                                "type": "number",
                                "description": "左转角度，单位为度",
                            }
                        },
                        "required": ["angle"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "turn_right",
                    "description": "机器人向右转指定角度",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "angle": {
                                "type": "number",
                                "description": "右转角度，单位为度",
                            }
                        },
                        "required": ["angle"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_to_location",
                    "description": "机器人移动到指定的标记点位置",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location_name": {
                                "type": "string",
                                "description": "目标位置的标记点名称",
                            }
                        },
                        "required": ["location_name"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_move",
                    "description": "取消当前正在执行的移动任务",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                }
            }
        ]
    
    @PerformanceOptimizer.timing_decorator("initialize")
    def initialize(self) -> bool:
        """快速初始化系统"""
        # 初始化面部识别系统
        if not self.face_system.initialize():
            print("❌ 面部识别系统初始化失败")
            return False
        
        # 启动面部识别
        if not self.face_system.start_recognition():
            print("❌ 启动面部识别失败")
            return False
        
        # 尝试连接机器人移动系统（跳过详细检查）
        if should_skip_check('service_health') or self.move_controller.connect():
            self.move_connected = True
        
        return True
    
    def interrupt_callback(self):
        """中断回调函数"""
        return self.interrupted
    
    def signal_handler(self, sig, frame):
        """信号处理函数"""
        self.interrupted = True
    
    def start_voice_wake_listening(self):
        """启动语音唤醒监听"""
        if not should_skip_check('audio_file_exists') and not os.path.exists(self.config.wake_word_model):
            print(f"❌ 唤醒词模型文件不存在: {self.config.wake_word_model}")
            return False
        
        print('🎧 正在监听语音唤醒词...')
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # 创建检测器
            self.wake_detector = snowboydecoder.HotwordDetector(
                self.config.wake_word_model,
                sensitivity=self.config.wake_sensitivity
            )
            
            # 开始监听
            self.wake_detector.start(
                detected_callback=self._wake_word_callback,
                interrupt_check=self.interrupt_callback,
                sleep_time=0.03
            )
            
        except Exception as e:
            print(f"❌ 语音唤醒监听启动失败: {e}")
            return False
        finally:
            if self.wake_detector:
                self.wake_detector.terminate()
        
        return True
    
    def _wake_word_callback(self):
        """唤醒词检测回调函数"""
        print("🌅 检测到唤醒词！")
        
        # 停止唤醒词检测
        if self.wake_detector:
            self.wake_detector.terminate()
        
        self.state = AgentState.WAKE_DETECTED
        
        # 播放招呼语音（如果存在）
        self._play_greeting_if_exists()
        
        # 开始面部识别和用户交互流程
        self._handle_wake_detected()
        
        # 完成交互后重新开始监听
        self.state = AgentState.LISTENING
        self.start_voice_wake_listening()
    
    def _play_greeting_if_exists(self):
        """播放招呼语音（跳过检查优化）"""
        if should_skip_check('audio_file_exists') or os.path.exists(self.config.greeting_audio):
            try:
                os.system(f'aplay -f S16_LE -r 16000 -c 1 {self.config.greeting_audio}')
            except:
                pass  # 简化错误处理
    
    def _handle_wake_detected(self):
        """处理唤醒检测后的流程"""
        try:
            # 跳过重复的面部识别启动检查
            if not should_skip_check('service_health'):
                if not self.face_system.start_recognition():
                    print("❌ 启动面部识别失败")
                    return
            
            # 开始识别用户
            user_name = self._identify_user_with_fast_search()
            
            if user_name and user_name != "Unknown":
                # 个性化确认提示
                self._give_personalized_greeting(user_name)
                
                # 开始对话
                self._start_fast_conversation_with_user(user_name)
            else:
                print("😔 未能识别到注册用户")
                
        except Exception as e:
            if not should_skip_check('detailed_validation'):
                print(f"❌ 唤醒处理过程出错: {e}")
        finally:
            # 停止面部识别
            self.face_system.stop_recognition()
    
    @PerformanceOptimizer.timing_decorator("give_personalized_greeting")
    def _give_personalized_greeting(self, user_name: str):
        """给出个性化的问候（优化版本）"""
        # 使用缓存的问候文本
        cache_key = f"greeting_{user_name}"
        greeting_text = self._response_cache.get(cache_key)
        
        if greeting_text is None:
            greeting_text = f"{user_name}您好，有什么可以帮到您？"
            self._response_cache.put(cache_key, greeting_text)
        
        print(f"🤖 {greeting_text}")
        
        # 使用TTS语音播放问候（优化I/O）
        try:
            if fast_config.FAST_MODE.get('memory_optimization', False):
                # 使用内存而非文件
                self._tts_to_memory_and_play(greeting_text)
            else:
                # 传统文件方式
                with open(self.config.tts_text_file, 'w', encoding='utf-8') as f:
                    f.write(greeting_text)
                
                self.voice_cloner.speak()
                self.voice_cloner.play_audio()
            
        except Exception as e:
            if not should_skip_check('detailed_validation'):
                print(f"❌ 个性化问候TTS失败: {e}")
    
    def _tts_to_memory_and_play(self, text: str):
        """TTS到内存并播放（避免文件I/O）"""
        # 这里可以实现内存版本的TTS，暂时使用文件版本
        with open(self.config.tts_text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        self.voice_cloner.speak()
        self.voice_cloner.play_audio()
    
    @PerformanceOptimizer.timing_decorator("identify_user_with_fast_search")
    def _identify_user_with_fast_search(self) -> Optional[str]:
        """快速识别用户"""
        # 直接扫描（减少时间）
        max_direct_scan_time = 1.5  # 从2.0减少到1.5
        start_time = time.time()
        
        while (time.time() - start_time) < max_direct_scan_time:
            recognized_name, _ = self.face_system.recognize_person()
            if recognized_name and recognized_name != "Unknown":
                return recognized_name
            time.sleep(0.2)
        
        # 快速搜索模式
        return self._fast_search_for_user()
    
    def _fast_search_for_user(self) -> Optional[str]:
        """快速搜索用户（优化角度和时间）"""
        # 只搜索3个关键角度：0°, 45°, -45°
        search_angles = [0, 45, -45]
        
        try:
            for angle in search_angles:
                # 转头到指定角度
                self.face_system.turn_head(angle)
                
                # 减少等待时间
                time.sleep(self.config.search_delay)
                
                # 快速识别
                start_time = time.time()
                max_recognition_time = 1.5  # 从2.0减少到1.5秒
                
                while (time.time() - start_time) < max_recognition_time:
                    recognized_name, _ = self.face_system.recognize_person()
                    if recognized_name and recognized_name != "Unknown":
                        print(f"🎯 在角度{angle}°发现用户: {recognized_name}")
                        return recognized_name
                    time.sleep(0.3)
                    
            return None
            
        except Exception as e:
            if not should_skip_check('detailed_validation'):
                print(f"❌ 搜索过程出错: {e}")
            return None
        finally:            
            # 搜索完成，回到正面
            self.face_system.return_home()
    
    @PerformanceOptimizer.timing_decorator("start_fast_conversation")
    def _start_fast_conversation_with_user(self, user_name: str):
        """快速对话系统"""
        print(f"💬 开始与 {user_name} 的语音对话")
        
        try:
            # 启动快速记忆智能体对话
            if not self.memory_agent.start_chat(user_name):
                print("❌ 无法启动对话系统")
                return
            
            self.state = AgentState.CHATTING
            
            # 启动人脸跟踪线程（对话期间保持跟踪）
            self._start_face_tracking_thread()
            
            # 创建音频录音器
            recorder = AudioRecorder()
            
            # print("🎤 请开始说话...")
            
            conversation_count = 0
            max_turns = fast_config.CONVERSATION_CONFIG['max_conversation_turns']
            
            while self.state == AgentState.CHATTING and conversation_count < max_turns:
                try:
                    conversation_count += 1
                    
                    # 语音录音（使用优化参数）
                    audio_file = f"/tmp/user_input_{conversation_count}.wav"
                    # print("🎤 请开始说话...")
                    print("优化。。。")
                    
                    recorder.start_dynamic_recording(
                        output_file=audio_file,
                        enable_vad=True,
                        debug_output=False  # 关闭调试输出
                    )
                    
                    print("✅ 录音完成，正在处理...")
                    
                    # 快速语音识别
                    user_input = self._fast_speech_to_text(audio_file)
                    
                    if not user_input or user_input.strip() == "":
                        print("⚠️ 未识别到有效语音，请重试")
                        continue
                    
                    print(f"👤 [识别结果]: {user_input}")
                    
                    # 检查是否为结束指令
                    goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话']
                    if any(pattern in user_input.lower() for pattern in goodbye_patterns):
                        print("👋 检测到告别语，准备结束对话")
                        break
                    
                    # 获取智能体回复（使用快速记忆系统）
                    response = self.memory_agent.chat(user_input)
                    print(f"🤖 [智能体]: {response}")
                    
                    # TTS语音播放回复
                    self._fast_text_to_speech(response)
                    
                    # 批量清理临时文件
                    self._add_temp_file_for_cleanup(audio_file)
                    
                except KeyboardInterrupt:
                    print("\n⚠️ 用户中断对话")
                    break
                except Exception as e:
                    if not should_skip_check('detailed_validation'):
                        print(f"❌ 对话轮次出错: {e}")
                    continue
            
            # 结束对话
            self.memory_agent.end_conversation()
            print("👋 语音对话结束")
            
        except Exception as e:
            if not should_skip_check('detailed_validation'):
                print(f"❌ 语音对话过程出错: {e}")
        finally:
            # 停止人脸跟踪线程
            self._stop_face_tracking_thread()
            self.state = AgentState.LISTENING
            # 批量清理临时文件
            self._batch_cleanup_temp_files()
    
    @PerformanceOptimizer.timing_decorator("fast_speech_to_text")
    def _fast_speech_to_text(self, audio_file: str) -> str:
        """快速语音转文字（减少检查和优化处理）"""
        try:
            # 跳过详细的文件检查
            if not should_skip_check('audio_file_size'):
                file_size = os.path.getsize(audio_file)
                if file_size < 1000:
                    return ""
            
            # 使用缓存检查
            if fast_config.FAST_MODE.get('cache_enabled', False):
                cache_key = f"asr_{fast_hash(audio_file)}_{os.path.getmtime(audio_file)}"
                cached_result = self._audio_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # 使用科大讯飞ASR进行语音识别
            asr_result_file = f"/tmp/asr_result_{int(time.time())}.txt"
            
            asr = SparkASR(
                app_id=self.config.asr_app_id,
                api_key=self.config.asr_api_key,
                api_secret=self.config.asr_api_secret,
                audio_file=audio_file,
                output_file=asr_result_file
            )
            
            # 执行语音识别（使用超时）
            asr.recognize()
            
            # 读取识别结果
            result = ""
            if os.path.exists(asr_result_file):
                try:
                    with open(asr_result_file, 'r', encoding='utf-8') as f:
                        result = f.read().strip()
                    
                    # 添加到清理列表
                    self._add_temp_file_for_cleanup(asr_result_file)
                    
                    # 缓存结果
                    if fast_config.FAST_MODE.get('cache_enabled', False) and result:
                        self._audio_cache.put(cache_key, result)
                        
                except Exception:
                    pass  # 简化错误处理
            
            return result
            
        except Exception:
            return ""  # 简化错误处理
    
    @PerformanceOptimizer.timing_decorator("fast_text_to_speech")
    def _fast_text_to_speech(self, text: str):
        """快速文字转语音并播放"""
        try:
            # 使用缓存检查
            if fast_config.FAST_MODE.get('cache_enabled', False):
                cache_key = f"tts_{fast_hash(text)}"
                cached_audio = self._audio_cache.get(cache_key)
                if cached_audio is not None:
                    # 播放缓存的音频
                    return
            
            # 将文本写入文件
            with open(self.config.tts_text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # 生成语音
            self.voice_cloner.speak()
            
            # 播放语音
            self.voice_cloner.play_audio()
            
        except Exception:
            pass  # 简化错误处理
    
    def _add_temp_file_for_cleanup(self, file_path: str):
        """添加临时文件到批量清理列表"""
        self._temp_files.append(file_path)
        
        # 检查是否需要批量清理
        if len(self._temp_files) >= get_batch_size('file_cleanup'):
            self._batch_cleanup_temp_files()
    
    def _batch_cleanup_temp_files(self):
        """批量清理临时文件"""
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass  # 忽略删除错误
        
        self._temp_files.clear()
    
    # 简化的工具执行方法
    def _execute_face_recognition(self):
        """执行人脸识别（简化版本）"""
        try:
            os.system("/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/recognize.py")
        except:
            pass
    
    def _execute_face_registration(self, user_name: str):
        """执行人脸注册（简化版本）"""
        try:
            command = f"/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/register.py {user_name}"
            os.system(command)
        except:
            pass
    
    def _execute_move_forward(self, distance: float):
        """执行前进移动"""
        if not self.move_connected:
            return
        try:
            self.move_controller.move_linear_for_distance(distance)
        except:
            pass
    
    def _execute_move_backward(self, distance: float):
        """执行后退移动"""
        if not self.move_connected:
            return
        try:
            self.move_controller.move_linear_for_distance(-distance)
        except:
            pass
    
    def _execute_turn_left(self, angle: float):
        """执行左转"""
        if not self.move_connected:
            return
        try:
            self.move_controller.move_angular_for_angle(angle)
        except:
            pass
    
    def _execute_turn_right(self, angle: float):
        """执行右转"""
        if not self.move_connected:
            return
        try:
            self.move_controller.move_angular_for_angle(-angle)
        except:
            pass
    
    def _execute_move_to_location(self, location_name: str):
        """执行移动到指定位置"""
        if not self.move_connected:
            return
        try:
            self.move_controller.move_to_marker(location_name)
        except:
            pass
    
    def _execute_cancel_move(self):
        """执行取消移动"""
        if not self.move_connected:
            return
        try:
            self.move_controller.cancel_move()
        except:
            pass
    
    def _start_face_tracking_thread(self):
        """启动人脸跟踪线程（简化版本）"""
        self.face_tracking_active = True
        self.face_tracking_thread = threading.Thread(
            target=self._face_tracking_loop, 
            daemon=True
        )
        self.face_tracking_thread.start()
    
    def _stop_face_tracking_thread(self):
        """停止人脸跟踪线程"""
        if hasattr(self, 'face_tracking_active'):
            self.face_tracking_active = False
    
    def _face_tracking_loop(self):
        """人脸跟踪循环（简化版本）"""
        try:
            while (hasattr(self, 'face_tracking_active') and 
                   self.face_tracking_active and 
                   self.state == AgentState.CHATTING):
                
                # 获取当前识别结果
                recognized_name, middle_pixel = self.face_system.recognize_person()
                
                # 如果识别到用户，进行跟踪
                if recognized_name and recognized_name != "Unknown":
                    self.face_system.follow_person(middle_pixel, recognized_name)
                
                time.sleep(0.8)  # 减少跟踪频率
                
        except Exception:
            pass  # 简化错误处理
    
    def get_current_state(self) -> Dict:
        """获取当前状态信息"""
        return {
            "state": self.state.value,
            "current_user": self.current_user,
            "current_confidence": self.current_confidence,
            "is_running": self.is_running,
            "last_recognition_time": self.last_recognition_time,
            "performance_stats": PerformanceOptimizer.get_performance_stats(),
            "cache_stats": {
                "audio_cache_size": self._audio_cache.size(),
                "response_cache_size": self._response_cache.size(),
                "temp_files_count": len(self._temp_files)
            }
        }
    
    def cleanup(self):
        """清理资源（快速版本）"""
        # 停止后台识别
        self.is_running = False
        
        # 结束当前对话
        if self.state == AgentState.CHATTING:
            self.memory_agent.end_conversation()
        
        # 清理面部识别系统
        self.face_system.cleanup()
        
        # 断开机器人连接
        if self.move_connected:
            self.move_controller.disconnect()
            self.move_connected = False
        
        # 批量清理临时文件
        self._batch_cleanup_temp_files()
        
        # 清理缓存
        self._audio_cache.clear()
        self._response_cache.clear()
        global_cache.clear()

# 使用示例和测试函数
def create_fast_config() -> FastSuperAgentConfig:
    """创建快速配置"""
    face_config = FaceRecognitionConfig(
        service_url="http://localhost:5001",
        recognition_threshold=0.6,
        left_threshold=300,
        right_threshold=340,
        follow_delta_angle=15
    )
    
    return FastSuperAgentConfig(
        face_config=face_config,
        deepseek_api_key="sk-fdabadb2973b4795b2444da60e75152f",
        deepseek_base_url="https://api.deepseek.com",
        memory_file_path="/home/xuanwu/haven_ws/demos/data/memory_tree.json",
        
        # TTS配置
        tts_voice_name="default",
        tts_config_path="/home/xuanwu/haven_ws/config/voices.json",
        tts_text_file="/tmp/tts_text.txt",
        tts_audio_file="/tmp/tts_output.wav",
        
        # 机器人移动配置
        robot_host="192.168.10.10",
        robot_port=31001,
        
        # 优化的配置
        search_angle_range=(-45, 45),  # 减少搜索范围
        search_step=45,                # 增加步长
        search_delay=fast_config.FACE_RECOGNITION_CONFIG['search_stabilization_time'],
        recognition_confidence_threshold=0.6,
        continuous_scan_interval=0.3,   # 减少扫描间隔
        unknown_user_timeout=3.0        # 减少超时时间
    )

def main():
    """主函数 - 快速语音唤醒模式"""
    print("🚀 启动快速超级智能体 - 语音唤醒模式")
    
    # 创建快速配置
    config = create_fast_config()
    
    # 创建快速超级智能体
    agent = FastSuperIntelligentAgent(config)
    
    try:
        # 初始化系统
        if not agent.initialize():
            print("❌ 系统初始化失败")
            return
        
        print("\n" + "="*60)
        print("🤖 快速超级智能体已启动")
        print("🎧 系统将持续监听语音唤醒词")
        print("💬 请说 '小助小助' 来唤醒智能体")
        print("⚡ 性能优化已启用 - 响应更快速")
        print("="*60 + "\n")
        
        # 启动语音唤醒监听
        agent.start_voice_wake_listening()
        
    except KeyboardInterrupt:
        print("\n🛑 检测到中断信号")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")
    finally:
        # 清理资源
        agent.cleanup()
        
        # 打印性能统计
        stats = agent.get_current_state()
        print("\n📊 性能统计:")
        print(f"  缓存命中: {stats['cache_stats']}")
        print(f"  性能数据: {len(stats['performance_stats'])} 项")
        
        print("👋 快速超级智能体已关闭")

if __name__ == "__main__":
    main()