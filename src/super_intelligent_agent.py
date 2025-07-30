#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级智能体 - 集成面部识别、语音唤醒和对话功能的完整系统
"""

import os
import sys
import time
import threading
import signal
import json
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# 添加必要的路径
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
sys.path.append('/home/xuanwu/haven_ws/src')
sys.path.append('/home/xuanwu/snowboy/snowboy-master/examples/Python3')
sys.path.append('/home/xuanwu/jakaPythonSdk')

# 导入语音唤醒模块
import snowboydecoder

# 导入现有的组件
from memory_agent import MemoryAgent
from face_recognition_client import FaceRecognitionClient, FaceRecognitionConfig
from audio_recorder import AudioRecorder
from spark_asr import SparkASR
from voice_cloner import VoiceCloner
from move_controller import MoveController
from marker_manager import MarkerManager
from openai import OpenAI

# 导入握手相关模块
try:
    # 需要先添加jkrc库的路径并设置动态库路径
    import os
    jkrc_path = '/home/xuanwu/jakaPythonSdk'
    if jkrc_path not in sys.path:
        sys.path.append(jkrc_path)
    
    # 设置动态库路径
    current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
    if jkrc_path not in current_ld_path:
        os.environ['LD_LIBRARY_PATH'] = f"{jkrc_path}:{current_ld_path}"
    
    # 切换到jkrc目录进行导入（因为jkrc.so可能需要在特定目录下才能正常工作）
    original_cwd = os.getcwd()
    os.chdir(jkrc_path)
    
    import jkrc
    from pickandplace import hand_control
    
    # 恢复原始工作目录
    os.chdir(original_cwd)
    
    HANDSHAKE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 握手功能不可用，缺少依赖: {e}")
    HANDSHAKE_AVAILABLE = False
except Exception as e:
    print(f"⚠️ 握手功能初始化失败: {e}")
    HANDSHAKE_AVAILABLE = False

class AgentState(Enum):
    """智能体状态枚举"""
    LISTENING = "listening"            # 语音唤醒监听状态
    WAKE_DETECTED = "wake_detected"    # 检测到唤醒词
    SCANNING = "scanning"              # 后台扫描
    SEARCHING = "searching"            # 主动搜索用户
    CHATTING = "chatting"              # 对话状态

@dataclass
class SuperAgentConfig:
    """超级智能体配置"""
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
    
    # 搜索配置
    search_angle_range: Tuple[int, int] = (-60, 60)  # 搜索角度范围
    search_step: int = 15  # 搜索步长
    search_delay: float = 2.0  # 每步搜索延迟
    
    # 识别配置
    recognition_confidence_threshold: float = 0.6  # 识别置信度阈值
    continuous_scan_interval: float = 0.5  # 连续扫描间隔
    unknown_user_timeout: float = 5.0  # 未知用户超时时间
    
    # 握手配置
    handshake_robot_host: str = "192.168.10.90"  # 握手机械臂IP
    handshake_positions_file: str = "/home/xuanwu/jakaPythonSdk/json/woshou1.json"  # 握手位置文件
    handshake_reverse_positions_file: str = "/home/xuanwu/jakaPythonSdk/json/woshou1_reverse.json"  # 握手返回位置文件
    handshake_hold_time: float = 2.0  # 握手持续时间（秒）
    
    # 人脸跟踪配置
    enable_conversation_tracking: bool = True  # 对话期间是否启用人脸跟踪

class SuperIntelligentAgent:
    """
    超级智能体 - 融合面部识别和对话功能
    """
    
    def __init__(self, config: SuperAgentConfig):
        self.config = config
        self.state = AgentState.LISTENING  # 初始状态改为监听
        self.memory_history = ""
        # 初始化子系统
        self.face_system = FaceRecognitionClient(config.face_config)
        self.memory_agent = MemoryAgent(
            deepseek_api_key=config.deepseek_api_key,
            deepseek_base_url=config.deepseek_base_url,
            memory_file_path=config.memory_file_path
        )
        
        # 初始化DeepSeek客户端用于智能对话
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
        
        # 初始化移动控制器和点位管理器
        self.move_controller = MoveController(
            host=config.robot_host,
            port=config.robot_port
        )
        self.marker_manager = MarkerManager(
            host=config.robot_host,
            port=config.robot_port
        )
        self.move_connected = False
        
        # 点位确认状态
        self.pending_location_confirmation = None  # 待确认的点位信息
        
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
        self.search_direction: int = 1  # 1为右转，-1为左转
        self.search_interrupted: bool = False  # 搜索中断标志
        
        # 定义工具函数
        self.tools = self._define_tools()
        
        # 递归任务处理状态管理
        self.recursive_depth = 0  # 当前递归深度
        self.max_recursive_depth = 4  # 最大递归深度
        self.current_remaining_instruction = ""  # 当前剩余指令
        
        # 握手系统初始化
        self.handshake_robot = None
        self.handshake_action = None
        self.handshake_connected = False
        
        # print("🤖 超级智能体初始化完成")
    
    def _define_tools(self):
        """定义DeepSeek可调用的工具函数"""
        return [
            # 人脸识别工具
            {
                "type": "function",
                "function": {
                    "name": "recognize_face",
                    "description": "识别当前用户的人脸",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成人脸识别后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["remaining_instruction"]
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
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成人脸注册后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["user_name", "remaining_instruction"]
                    },
                }
            },
            # 前进移动
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
                            },
                            "voice_message": {
                                "type": "string",
                                "description": "执行动作前的语音播报内容",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成前进移动后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["distance", "voice_message", "remaining_instruction"]
                    },
                }
            },
            # 后退移动
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
                            },
                            "voice_message": {
                                "type": "string",
                                "description": "执行动作前的语音播报内容",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成后退移动后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["distance", "voice_message", "remaining_instruction"]
                    },
                }
            },
            # 左转
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
                            },
                            "voice_message": {
                                "type": "string",
                                "description": "执行动作前的语音播报内容",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成左转后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["angle", "voice_message", "remaining_instruction"]
                    },
                }
            },
            # 右转
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
                            },
                            "voice_message": {
                                "type": "string",
                                "description": "执行动作前的语音播报内容",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成右转后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["angle", "voice_message", "remaining_instruction"]
                    },
                }
            },
            # 智能导航到点位
            {
                "type": "function",
                "function": {
                    "name": "navigate_to_location",
                    "description": "直接导航到指定点位，会自动匹配最相似的可用点位并直接移动",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location_name": {
                                "type": "string",
                                "description": "从可用点位中选择的准确点位名称，如'厨房'、'客厅'、'书房'等",
                            },
                            "voice_message": {
                                "type": "string", 
                                "description": "执行导航前的语音播报内容，如'我将去往书房'",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成导航后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["location_name", "voice_message", "remaining_instruction"]
                    },
                }
            },
            # 点位匹配确认
            {
                "type": "function",
                "function": {
                    "name": "find_similar_locations",
                    "description": "查找与用户输入相似的点位名称",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_input": {
                                "type": "string",
                                "description": "用户说的目标位置",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成点位查找后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["user_input", "remaining_instruction"]
                    },
                }
            },
            # 确认点位移动
            {
                "type": "function",
                "function": {
                    "name": "confirm_and_move_to_location",
                    "description": "在用户确认后执行移动到指定点位",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "confirmed_location": {
                                "type": "string",
                                "description": "用户确认的准确点位名称",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成移动后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["confirmed_location", "remaining_instruction"]
                    },
                }
            },
            # 取消移动
            {
                "type": "function",
                "function": {
                    "name": "cancel_move",
                    "description": "取消当前正在执行的移动任务",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "remaining_instruction": {
                                "type": "string",
                                "description": "取消移动后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["remaining_instruction"]
                    },
                }
            },
            # 握手问候
            {
                "type": "function",
                "function": {
                    "name": "handshake_greeting",
                    "description": "当用户提到让你打个招呼或者和他握手时，执行握手动作",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "voice_message": {
                                "type": "string",
                                "description": "执行握手前的语音播报内容",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成握手后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["voice_message", "remaining_instruction"]
                    },
                }
            },
            # 抓取物品
            {
                "type": "function",
                "function": {
                    "name": "grab_object",
                    "description": "当用户要求拿起、抓取、取某个物品时，执行抓取动作",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "object_name": {
                                "type": "string",
                                "description": "要抓取的物品名称，如'水瓶'、'杯子'等",
                            },
                            "voice_message": {
                                "type": "string",
                                "description": "执行抓取前的语音播报内容",
                            },
                            "remaining_instruction": {
                                "type": "string",
                                "description": "完成抓取后剩余的指令内容，如果这是完整指令的一部分则填写剩余部分，如果是独立任务则为空字符串",
                            }
                        },
                        "required": ["object_name", "voice_message", "remaining_instruction"]
                    },
                }
            }
        ]
    
    def initialize(self) -> bool:
        """
        初始化整个系统
        """
        # print("🔧 正在初始化超级智能体系统...")
        
        # 初始化面部识别系统
        if not self.face_system.initialize():
            print("❌ 面部识别系统初始化失败")
            return False
        
        # 启动面部识别
        if not self.face_system.start_recognition():
            print("❌ 启动面部识别失败")
            return False
        
        # 尝试连接机器人移动系统（可选）
        if self.move_controller.connect():
            self.move_connected = True
            # 同时连接点位管理器（使用相同连接）
            if self.marker_manager.connect():
                # print("✅ 点位管理系统连接成功")
                pass
            else:
                print("⚠️ 点位管理系统连接失败")
            # print("✅ 机器人移动系统连接成功")
        else:
            print("⚠️ 机器人移动系统连接失败，移动功能将不可用")
        
        # print("✅ 超级智能体系统初始化成功")
        return True
    
    def interrupt_callback(self):
        """中断回调函数"""
        return self.interrupted
    
    def signal_handler(self, sig, frame):
        """信号处理函数"""
        self.interrupted = True
    
    def start_voice_wake_listening(self):
        """
        启动语音唤醒监听
        """
        if not os.path.exists(self.config.wake_word_model):
            print(f"❌ 唤醒词模型文件不存在: {self.config.wake_word_model}")
            return False
        
        # print('🎧 正在监听语音唤醒词... (按 Ctrl+C 停止)')
        # print('💬 请说 "小助小助" 来唤醒我')
        
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
        """
        唤醒词检测回调函数
        """
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
        """播放招呼语音（如果文件存在）"""
        if os.path.exists(self.config.greeting_audio):
            # print("🔊 播放招呼语音...")
            os.system(f'aplay -f S16_LE -r 16000 -c 1 {self.config.greeting_audio}')
        else:
            print("⚠️ 招呼语音文件不存在，跳过播放")
    
    def _handle_wake_detected(self):
        """
        处理唤醒检测后的流程
        """
        try:
            # 启动面部识别
            if not self.face_system.start_recognition():
                print("❌ 启动面部识别失败")
                return
            
            # 开始识别用户
            user_name = self._identify_user_with_search()
            
            if user_name and user_name != "Unknown":
                # 个性化确认提示
                self._give_personalized_greeting(user_name)
                
                # 开始对话
                self._start_conversation_with_user(user_name)
            else:
                print("😔 未能识别到注册用户，对话结束")
                # 可以播放一个"未识别"的提示音
                
        except Exception as e:
            print(f"❌ 唤醒处理过程出错: {e}")
        finally:
            # 停止面部识别
            self.face_system.stop_recognition()
    
    def _give_personalized_greeting(self, user_name: str):
        """
        给出个性化的问候（使用TTS语音播报）
        """
        greeting_text = f"{user_name}您好，有什么可以帮到您？"
        print(f"🤖 {greeting_text}")
        
        # 使用TTS语音播放问候
        try:
            # 将问候文本写入TTS文件
            with open(self.config.tts_text_file, 'w', encoding='utf-8') as f:
                f.write(greeting_text)
            
            # 生成并播放语音
            print("🔊 正在播放个性化问候...")
            self.voice_cloner.speak()
            self.voice_cloner.play_audio()
            print("✅ 个性化问候播放完成")
            
        except Exception as e:
            print(f"❌ 个性化问候TTS失败: {e}")
            # 如果TTS失败，仍然显示文本问候
            print(f"💬 文本问候: {greeting_text}")
    
    def _identify_user_with_search(self) -> Optional[str]:
        """
        识别用户，包含搜索功能
        """
        # print("👁️ 开始识别用户...")
        
        # 直接扫描
        max_direct_scan_time = 2.0
        start_time = time.time()
        
        while (time.time() - start_time) < max_direct_scan_time:
            recognized_name, _ = self.face_system.recognize_person()
            if recognized_name and recognized_name != "Unknown":
                # print(f"✅ 直接识别到用户: {recognized_name}")
                return recognized_name
            time.sleep(0.2)
        
        # 如果直接扫描没有结果，开始搜索模式
        # print("🔍 直接扫描未发现用户，开始搜索模式...")
        return self._search_for_user()
    
    def _search_for_user(self) -> Optional[str]:
        """
        搜索用户（恢复稳定的摇头寻找逻辑，优化为45°/-45°搜索）
        """
        # print("🔍 开始搜索模式...")
        
        # 搜索角度序列：45° → -45° → 0°
        search_angles = [45, -45, 0]
        
        try:
            for angle in search_angles:
                # print(f"🔄 转头到角度: {angle}°")
                
                # 转头到指定角度
                self.face_system.turn_head(angle)
                
                # 🔑 关键修改：等待机械臂到位并稳定
                stabilization_time = 1.2  # 等待1.2秒让机械臂到位
                time.sleep(stabilization_time)
                # print(f"⏳ 机械臂已到位，开始在{angle}°角度识别...")
                
                # 重新设置识别开始时间
                start_time = time.time()
                max_recognition_time = 2.0  # 每个角度识别2秒
                
                while (time.time() - start_time) < max_recognition_time:
                    recognized_name, _ = self.face_system.recognize_person()
                    if recognized_name and recognized_name != "Unknown":
                        print(f"🎯 在角度{angle}°发现用户: {recognized_name}")
                        return recognized_name
                    time.sleep(0.3)  # 稍微降低识别频率，避免过于频繁
                    
            # print("🔍 搜索完成，未发现注册用户")
            return None
            
        except Exception as e:
            print(f"❌ 搜索过程出错: {e}")
            return None
        finally:            
            # 搜索完成，回到正面
            self.face_system.return_home()
    
    def _start_conversation_with_user(self, user_name: str):
        """
        与用户开始语音对话
        """
        print(f"💬 开始与 {user_name} 的语音对话")
        
        try:
            # 启动记忆智能体对话
            if not self.memory_agent.start_chat(user_name):
                print("❌ 无法启动对话系统")
                return
            
            self.state = AgentState.CHATTING
            
            # 启动人脸跟踪线程（对话期间保持跟踪）
            if self.config.enable_conversation_tracking:
                print("👁️ 启用对话期间人脸跟踪")
                self._start_face_tracking_thread()
            else:
                print("⚠️ 对话期间人脸跟踪已禁用")
            
            # 创建音频录音器
            recorder = AudioRecorder()
            
            # print("🎤 语音对话已启动")
            # print("💡 说话结束后会自动检测并处理您的语音")
            # print("💬 说'再见'或'结束对话'来结束对话")
            
            conversation_count = 0
            max_turns = 20  # 限制对话轮数防止无限循环
            
            while self.state == AgentState.CHATTING and conversation_count < max_turns:
                try:
                    conversation_count += 1
                    # print(f"\n🔄 对话轮次 {conversation_count}")
                    
                    # 语音录音
                    audio_file = f"/tmp/user_input_{conversation_count}.wav"
                    print("🎤 请开始说话...")
                    
                    recorder.start_dynamic_recording(
                        output_file=audio_file,
                        enable_vad=True,  # 启用语音活动检测
                        debug_output=False  # 关闭调试输出
                    )
                    
                    print("✅ 录音完成，正在处理...")
                    
                    # 并行处理：ASR识别和TTS引擎预热
                    import threading
                    
                    # 用于存储ASR结果的容器
                    asr_result = {"text": ""}
                    
                    def asr_worker():
                        """ASR工作线程"""
                        asr_result["text"] = self._speech_to_text(audio_file)
                    
                    def tts_warmup_worker():
                        """TTS预热工作线程"""
                        self._warm_up_tts_engine()
                    
                    # 启动两个并行线程
                    asr_thread = threading.Thread(target=asr_worker, daemon=True)
                    tts_thread = threading.Thread(target=tts_warmup_worker, daemon=True)
                    
                    asr_thread.start()
                    tts_thread.start()
                    
                    # 等待ASR完成（TTS预热可以在后台继续）
                    asr_thread.join()
                    user_input = asr_result["text"]
                    
                    # TTS预热不阻塞主流程，让它在后台完成
                    
                    if not user_input or user_input.strip() == "":
                        # print("⚠️ 未识别到有效语音，请重试")
                        continue
                    
                    print(f"👤 [识别结果]: {user_input}")
                    
                    # 检查是否为结束指令
                    goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话', 'quit', 'exit']
                    if any(pattern in user_input.lower() for pattern in goodbye_patterns):
                        # print("👋 检测到告别语，准备结束对话")
                        break
                    
                    # 获取智能体回复（集成工具调用功能）
                    response, should_end, tool_calls = self._get_intelligent_response(user_input)
                    print(f"🤖 [智能体]: {response}")
                    
                    # TTS语音播放回复
                    self._text_to_speech(response)
                    
                    # 执行工具调用（如果有）
                    if tool_calls:
                        self._execute_tool_calls(tool_calls)
                    
                    # 检查是否需要结束对话
                    if should_end:
                        # print("🔄 检测到对话结束信号")
                        break
                    
                    # 清理临时音频文件
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                    
                except KeyboardInterrupt:
                    print("\n⚠️ 用户中断对话")
                    break
                except Exception as e:
                    print(f"❌ 对话轮次出错: {e}")
                    continue
            
            # 结束对话
            self.memory_agent.end_conversation()
            print("👋 语音对话结束")
            
            if conversation_count >= max_turns:
                print(f"ℹ️ 已达到最大对话轮数({max_turns})，自动结束")
            
        except Exception as e:
            print(f"❌ 语音对话过程出错: {e}")
        finally:
            # 停止人脸跟踪线程
            if self.config.enable_conversation_tracking:
                self._stop_face_tracking_thread()
            self.state = AgentState.LISTENING
    
    def _speech_to_text(self, audio_file: str) -> str:
        """
        语音转文字（使用科大讯飞ASR）
        """
        try:
            if not os.path.exists(audio_file):
                print("❌ 音频文件不存在")
                return ""
            
            # 检查音频文件大小
            file_size = os.path.getsize(audio_file)
            if file_size < 1000:  # 小于1KB认为是空录音
                # print("⚠️ 音频文件太小，可能没有录到有效语音")
                return ""
            
            # print("🔄 正在进行语音识别...")
            # print(f"📁 音频文件: {audio_file} ({file_size} 字节)")
            
            # 使用科大讯飞ASR进行语音识别
            asr_result_file = f"/tmp/asr_result_{int(time.time())}.txt"
            
            asr = SparkASR(
                app_id=self.config.asr_app_id,
                api_key=self.config.asr_api_key,
                api_secret=self.config.asr_api_secret,
                audio_file=audio_file,
                output_file=asr_result_file
            )
            
            # print("🌐 连接科大讯飞ASR服务...")
            
            # 执行语音识别（这是阻塞调用，会等待识别完成）
            asr.recognize()
            
            # print("✅ ASR识别完成，读取结果...")
            
            # 读取识别结果
            if os.path.exists(asr_result_file):
                try:
                    with open(asr_result_file, 'r', encoding='utf-8') as f:
                        result = f.read().strip()
                    
                    # 清理临时文件
                    if os.path.exists(asr_result_file):
                        os.remove(asr_result_file)
                    
                    if result:
                        # print(f"✅ 语音识别成功: {result}")
                        return result
                    else:
                        # print("⚠️ 识别结果为空")
                        return ""
                        
                except Exception as e:
                    print(f"❌ 读取ASR结果失败: {e}")
                    return ""
            else:
                print("❌ ASR结果文件未生成")
                return ""
            
        except Exception as e:
            print(f"❌ 语音识别失败: {e}")
            return ""
    
    def _text_to_speech(self, text: str):
        """
        文字转语音并播放
        """
        try:
            # print(f"🔊 正在生成语音: {text}")
            
            # 将文本写入文件
            with open(self.config.tts_text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # 生成语音
            self.voice_cloner.speak()
            
            # 播放语音
            # print("📢 正在播放语音...")
            self.voice_cloner.play_audio()
            
            # print("✅ 语音播放完成")
            
        except Exception as e:
            print(f"❌ 语音合成失败: {e}")
    
    def _get_intelligent_response(self, user_input: str) -> tuple[str, bool, list]:
        """
        获取智能体回复（集成记忆系统和工具调用）
        """
        try:
            # print("🤖 正在生成智能回复...")
            
            # 获取相关记忆
            retrieved_memories = self.memory_agent.memory_tree.search(
                user_input, similarity_threshold=0.6, max_results=3
            )
            
            # 格式化记忆上下文
            memory_context=""
            if retrieved_memories:
                memory_context = "\n\n相关记忆:\n"
                for i, memory in enumerate(retrieved_memories, 1):
                    memory_context += f"{i}. {memory['summary']} (相似度: {memory['similarity']:.2f})\n"
            
            # 获取个人画像信息
            profile_info = ""
            if self.memory_agent.current_person_profile:
                import json
                profile_data = self.memory_agent.current_person_profile.attributes
                profile_info = f"\n\n用户画像: {json.dumps(profile_data, ensure_ascii=False)}"
            
            # 获取可用点位信息
            available_locations = ""
            try:
                if self.move_connected:
                    response = self.marker_manager.get_marker_brief()
                    if response and response.get("status") == "OK":
                        markers = response.get("results", {})
                        if markers:
                            location_list = list(markers.keys())
                            available_locations = f"\n\n🎯 可用导航点位: {', '.join(location_list)}"
            except Exception:
                pass  # 获取点位失败不影响主流程
            
            # 构建系统提示词
            system_prompt = f"""你是一个养老机构的智能协助机器人，你的名字叫小助。你的任务是协助老年人的日常生活，包括：
1. 回答问题和日常聊天
2. 协助人脸识别和注册
3. 帮助老人在机构内移动和导航
4. 提供生活上的关怀和帮助

当前对话对象：{self.current_user}
他/她的个人形象：{profile_info}

你的特点：
- 语言通俗易懂，简单明了，适合老年人理解
- 语气亲切温和，像家人一样关怀
- 回复简洁，不超过50字
- 当你觉得这次对话可能要结束时，可以主动问"您还有什么需要我帮忙的吗？"
- 你不必总是叫出对方的名字，但可以在合适的情况下使用敬语

🔥 重要：递归式任务处理规则
如果用户的指令包含多个步骤的任务（如"先注册人脸，然后前进2米，再左转45度"），你需要：
1. 只处理第一个任务（如"注册人脸"）
2. 在相应的工具函数的remaining_instruction参数中填写剩余的指令内容（如"前进2米，再左转45度"）
3. 如果指令只有一个任务，remaining_instruction填写空字符串""
4. 系统会自动处理remaining_instruction中的剩余任务

示例：
- 用户："请注册人脸，然后前进2米" → 调用register_face，remaining_instruction="前进2米"
- 用户："前进2米，再左转45度" → 调用move_forward，remaining_instruction="左转45度"  
- 用户："左转45度" → 调用turn_left，remaining_instruction=""

关于点位导航的处理：
- 当用户要求去某个地方时，使用navigate_to_location工具并直接移动
- 请从可用点位中选择最匹配的点位名称
- 直接播报"我将去往xxx"然后执行移动，无需确认
- 点位确认等待期间：{f"当前等待确认的点位：{self.pending_location_confirmation}" if self.pending_location_confirmation else "无待确认点位"}
{available_locations}

- 如果用户明确表示不需要更多帮助或要结束对话，请在回复末尾添加 [CONVERSATION_END]
{memory_context}
这是你们的聊天记录，简单可以参考：{self.memory_history}"""
            print(f"🤖 系统提示词: {system_prompt}")
            # 调用DeepSeek API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools
            )
            
            assistant_response = response.choices[0].message.content or ""
            tool_calls = response.choices[0].message.tool_calls or []
            self.memory_history+=f"用户：{user_input}， 智能体：{assistant_response}\n"
            # 检查是否包含对话结束标记
            conversation_should_end = False
            if "[CONVERSATION_END]" in assistant_response:
                conversation_should_end = True
                assistant_response = assistant_response.replace("[CONVERSATION_END]", "").strip()
            
            # 检查显式告别关键词
            goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话', 'quit', 'exit']
            if any(pattern in user_input.lower() for pattern in goodbye_patterns):
                conversation_should_end = True
            
            # 添加对话轮次到记忆
            if not conversation_should_end:
                self.memory_agent.memory_tree.add_conversation_turn(user_input, assistant_response)
            
            return assistant_response, conversation_should_end, tool_calls
            
        except Exception as e:
            print(f"❌ 获取回复失败: {e}")
            return "抱歉，我现在有点不舒服，您稍后再试试吧。", False, []
    
    def _execute_tool_calls(self, tool_calls: list):
        """
        执行工具调用，支持递归式任务处理
        """
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            
            try:
                import json
                arguments = json.loads(tool_call.function.arguments)
            except:
                arguments = {}
            
            # 提取剩余指令
            remaining_instruction = arguments.get("remaining_instruction", "")
            
            # 提取语音播报内容并播放
            voice_message = arguments.get("voice_message", "")
            if voice_message:
                print(f"🔊 [语音播报]: {voice_message}")
                self._text_to_speech(voice_message)
            
            print(f"🔧 执行工具: {tool_name} (递归深度: {self.recursive_depth})")
            
            try:
                if tool_name == "recognize_face":
                    self._execute_face_recognition()
                elif tool_name == "register_face":
                    user_name = arguments.get("user_name", "")
                    self._execute_face_registration(user_name)
                elif tool_name == "move_forward":
                    distance = arguments.get("distance", 0)
                    self._execute_move_forward(distance)
                elif tool_name == "move_backward":
                    distance = arguments.get("distance", 0)
                    self._execute_move_backward(distance)
                elif tool_name == "turn_left":
                    angle = arguments.get("angle", 0)
                    self._execute_turn_left(angle)
                elif tool_name == "turn_right":
                    angle = arguments.get("angle", 0)
                    self._execute_turn_right(angle)
                elif tool_name == "move_to_location":
                    location_name = arguments.get("location_name", "")
                    self._execute_move_to_location(location_name)
                elif tool_name == "navigate_to_location":
                    location_name = arguments.get("location_name", "")
                    self._execute_navigate_to_location(location_name)
                elif tool_name == "find_similar_locations":
                    user_input = arguments.get("user_input", "")
                    self._execute_find_similar_locations(user_input)
                elif tool_name == "confirm_and_move_to_location":
                    confirmed_location = arguments.get("confirmed_location", "")
                    self._execute_confirm_and_move_to_location(confirmed_location)
                elif tool_name == "cancel_move":
                    self._execute_cancel_move()
                elif tool_name == "handshake_greeting":
                    self._execute_handshake_greeting()
                elif tool_name == "grab_object":
                    object_name = arguments.get("object_name", "")
                    self._execute_grab_object(object_name)
                else:
                    print(f"❌ 未知的工具函数: {tool_name}")
                    
            except Exception as e:
                print(f"❌ 工具执行失败: {e}")
                return  # 工具执行失败时不继续递归
            
            # 🔥 递归式任务处理：如果有剩余指令且未达到最大深度，则递归调用
            if remaining_instruction and remaining_instruction.strip():
                if self.recursive_depth < self.max_recursive_depth:
                    print(f"📋 检测到剩余指令: '{remaining_instruction}' (递归深度: {self.recursive_depth + 1})")
                    self._process_remaining_instruction(remaining_instruction)
                else:
                    print(f"⚠️ 已达到最大递归深度({self.max_recursive_depth})，剩余指令将被忽略: '{remaining_instruction}'")
            else:
                print(f"✅ 任务完成，无剩余指令 (递归深度: {self.recursive_depth})")
    
    def _process_remaining_instruction(self, remaining_instruction: str):
        """
        处理剩余指令的递归调用
        """
        try:
            # 增加递归深度
            self.recursive_depth += 1
            self.current_remaining_instruction = remaining_instruction
            
            print(f"🔄 开始处理剩余指令 (递归深度: {self.recursive_depth}): '{remaining_instruction}'")
            
            # 获取剩余指令的智能回复
            response, should_end, tool_calls = self._get_intelligent_response(remaining_instruction)
            print(f"🤖 [递归回复]: {response}")
            
            # TTS语音播放回复
            if response and response.strip():
                self._text_to_speech(response)
            
            # 执行工具调用（递归）
            if tool_calls:
                self._execute_tool_calls(tool_calls)
            
        except Exception as e:
            print(f"❌ 递归处理剩余指令失败: {e}")
        finally:
            # 减少递归深度
            self.recursive_depth -= 1
            if self.recursive_depth == 0:
                print("🎯 所有递归任务处理完成")
                self.current_remaining_instruction = ""
    
    def _execute_face_recognition(self):
        """执行人脸识别"""
        try:
            os.system("/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/recognize.py")
            # print("✅ 人脸识别任务已启动")
        except Exception as e:
            print(f"❌ 人脸识别失败: {e}")
    
    def _execute_face_registration(self, user_name: str):
        """执行人脸注册"""
        try:
            command = f"/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/register.py {user_name}"
            os.system(command)
            # print(f"✅ 人脸注册任务已启动: {user_name}")
        except Exception as e:
            print(f"❌ 人脸注册失败: {e}")
    
    def _execute_move_forward(self, distance: float):
        """执行前进移动"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return
        
        try:
            self.move_controller.move_linear_for_distance(distance)
            # print(f"✅ 前进 {distance} 米")
        except Exception as e:
            print(f"❌ 前进移动失败: {e}")
    
    def _execute_move_backward(self, distance: float):
        """执行后退移动"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return
        
        try:
            self.move_controller.move_linear_for_distance(-distance)
            # print(f"✅ 后退 {distance} 米")
        except Exception as e:
            print(f"❌ 后退移动失败: {e}")
    
    def _execute_turn_left(self, angle: float):
        """执行左转"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法转动")
            return
        
        try:
            self.move_controller.move_angular_for_angle(angle)
            print(f"✅ 左转 {angle} 度")
        except Exception as e:
            print(f"❌ 左转失败: {e}")
    
    def _execute_turn_right(self, angle: float):
        """执行右转"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法转动")
            return
        
        try:
            self.move_controller.move_angular_for_angle(-angle)
            print(f"✅ 右转 {angle} 度")
        except Exception as e:
            print(f"❌ 右转失败: {e}")
    
    def _execute_move_to_location(self, location_name: str):
        """执行移动到指定位置"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return
        
        try:
            response = self.move_controller.move_to_marker(location_name)
            if response and response.get("status") == "OK":
                print(f"✅ 正在前往 {location_name}")
            else:
                print(f"❌ 移动到 {location_name} 失败")
        except Exception as e:
            print(f"❌ 移动到位置失败: {e}")
    
    def _execute_cancel_move(self):
        """执行取消移动"""
        if not self.move_connected:
            print("❌ 机器人未连接")
            return
        
        try:
            response = self.move_controller.cancel_move()
            if response and response.get("status") == "OK":
                print("✅ 已取消当前移动任务")
            else:
                print("❌ 取消移动失败")
        except Exception as e:
            print(f"❌ 取消移动失败: {e}")
    
    def _execute_navigate_to_location(self, location_name: str):
        """执行直接导航到指定点位"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            error_message = "抱歉，机器人未连接，无法前往指定位置"
            self._text_to_speech(error_message)
            return
        
        try:
            print(f"🎯 直接导航到: {location_name}")
            
            # 验证点位是否存在
            response = self.marker_manager.get_marker_brief()
            if not response or response.get("status") != "OK":
                print("❌ 获取点位列表失败")
                error_message = "抱歉，无法获取点位信息"
                self._text_to_speech(error_message)
                return
            
            markers = response.get("results", {})
            if location_name not in markers:
                print(f"❌ 点位'{location_name}'不存在")
                error_message = f"抱歉，找不到{location_name}这个位置"
                self._text_to_speech(error_message)
                return
            
            # 直接执行移动并等待完成
            print(f"🤖 开始移动到{location_name}")
            
            # 修改：明确指定wait=True并检查返回值
            success = self.move_controller.move_to_marker(location_name, wait=True)
            
            if success:
                print(f"✅ 成功到达 {location_name}")
                success_message = f"我已经到达{location_name}了"
                self._text_to_speech(success_message)
            else:
                print(f"❌ 移动到 {location_name} 失败")
                error_message = f"抱歉，无法前往{location_name}"
                self._text_to_speech(error_message)
                
        except Exception as e:
            print(f"❌ 导航执行失败: {e}")
            error_message = "抱歉，导航过程中出现了问题"
            self._text_to_speech(error_message)
    
    def _execute_find_similar_locations(self, user_input: str):
        """查找相似点位并请求确认"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法查询点位")
            return
        
        try:
            # 获取所有点位列表
            response = self.marker_manager.get_marker_brief()
            if not response or response.get("status") != "OK":
                print("❌ 获取点位列表失败")
                error_message = "抱歉，我无法查询到点位信息"
                self._text_to_speech(error_message)
                return
            
            markers = response.get("results", {})
            if not markers:
                print("❌ 没有可用的点位")
                no_markers_message = "抱歉，系统中没有设置任何点位"
                self._text_to_speech(no_markers_message)
                return
            
            # 使用LLM进行智能匹配
            matched_location = self._find_best_match_with_llm(user_input, list(markers.keys()))
            
            if matched_location:
                # 保存待确认的点位
                self.pending_location_confirmation = matched_location
                
                # 语音确认
                confirm_message = f"您让我去的是否是{matched_location}点位？"
                print(f"🔊 [确认询问]: {confirm_message}")
                self._text_to_speech(confirm_message)
            else:
                # 没有找到匹配的点位
                not_found_message = f"抱歉，我没有找到与'{user_input}'相似的点位"
                print(f"🔊 [未找到]: {not_found_message}")
                self._text_to_speech(not_found_message)
                
        except Exception as e:
            print(f"❌ 查找点位失败: {e}")
            error_message = "抱歉，查找点位时出现了问题"
            self._text_to_speech(error_message)
    
    def _find_best_match_with_llm(self, user_input: str, available_locations: list) -> str:
        """使用LLM找到最佳匹配的点位"""
        try:
            locations_text = "、".join(available_locations)
            
            prompt = f"""
            用户说要去"{user_input}"，现在有以下可用点位：{locations_text}
            
            请从这些点位中选择一个最匹配用户意图的点位名称。考虑：
            1. 发音相似性（如"厨房"可能被识别为"出房"）
            2. 语义相似性（如"餐厅"和"饭厅"）
            3. 常见简称（如"卧室"可能说成"卧"）
            
            如果找到匹配的点位，只返回准确的点位名称。
            如果没有找到合适的匹配，返回"未找到"。
            """
            
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个智能点位匹配助手，专门帮助匹配用户语音输入和实际点位名称。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # 降低随机性，提高匹配准确性
            )
            
            result = response.choices[0].message.content.strip()
            
            # 检查结果是否在可用点位列表中
            if result in available_locations:
                print(f"✅ LLM匹配结果: '{user_input}' -> '{result}'")
                return result
            elif result == "未找到":
                print(f"❌ LLM未找到匹配: '{user_input}'")
                return None
            else:
                print(f"⚠️ LLM返回了无效点位: '{result}'")
                return None
                
        except Exception as e:
            print(f"❌ LLM点位匹配失败: {e}")
            return None
    
    def _execute_confirm_and_move_to_location(self, confirmed_location: str):
        """执行确认后的移动"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return
        
        try:
            # 播放开始移动的语音
            start_message = f"好的，我现在去{confirmed_location}"
            print(f"🔊 [开始移动]: {start_message}")
            self._text_to_speech(start_message)
            
            # 执行移动
            response = self.move_controller.move_to_marker(confirmed_location)
            if response and response.get("status") == "OK":
                print(f"✅ 正在前往 {confirmed_location}")
                # 清除待确认状态
                self.pending_location_confirmation = None
            else:
                print(f"❌ 移动到 {confirmed_location} 失败")
                error_message = f"抱歉，无法前往{confirmed_location}"
                self._text_to_speech(error_message)
        except Exception as e:
            print(f"❌ 移动到位置失败: {e}")
            error_message = "抱歉，移动过程中出现了问题"
            self._text_to_speech(error_message)
    
    def _execute_handshake_greeting(self):
        """执行握手问候功能"""
        print(f"DEBUG: HANDSHAKE_AVAILABLE = {HANDSHAKE_AVAILABLE}")
        
        if not HANDSHAKE_AVAILABLE:
            print("❌ 握手功能不可用，缺少必要的依赖")
            error_message = "抱歉，握手功能暂时不可用"
            self._text_to_speech(error_message)
            return
        
        try:
            print("🤝 开始握手问候流程...")
            
            # 播放开始语音
            start_message = "好的，我来和您握个手，请稍等我准备一下"
            print(f"🔊 [握手开始]: {start_message}")
            self._text_to_speech(start_message)
            
            # 初始化握手系统
            print("🔧 准备初始化握手系统...")
            if not self._initialize_handshake_system():
                print("❌ 握手系统初始化失败，退出")
                return
            
            print("✅ 握手系统初始化成功，开始加载位置数据...")
            
            # 读取握手位置数据
            positions = self._load_handshake_positions()
            positions_reverse = self._load_handshake_reverse_positions()
            
            if not positions or not positions_reverse:
                print("❌ 位置数据加载失败")
                error_message = "抱歉，握手位置数据加载失败"
                self._text_to_speech(error_message)
                return
            
            print("✅ 位置数据加载成功，开始执行握手流程...")
            
            # 执行握手流程
            self._perform_handshake_sequence(positions, positions_reverse)
            
        except Exception as e:
            print(f"❌ 握手执行失败: {e}")
            import traceback
            traceback.print_exc()
            error_message = "抱歉，握手过程中出现了问题"
            self._text_to_speech(error_message)
        finally:
            # 清理握手系统
            print("🧹 清理握手系统...")
            self._cleanup_handshake_system()
    
    def _initialize_handshake_system(self) -> bool:
        """初始化握手系统"""
        try:
            print("🔧 初始化握手系统...")
            print(f"DEBUG: 握手机械臂IP: {self.config.handshake_robot_host}")
            
            # 初始化机械臂连接
            print("🔌 连接机械臂...")
            self.handshake_robot = jkrc.RC(self.config.handshake_robot_host)
            
            print("🔑 登录机械臂...")
            login_result = self.handshake_robot.login()
            print(f"DEBUG: 登录结果: {login_result}")
            print("✅ 机械臂连接成功")
            
            print("⚡ 机械臂上电...")
            power_result = self.handshake_robot.power_on()
            print(f"DEBUG: 上电结果: {power_result}")
            print("✅ 机械臂上电成功")
            
            print("🚀 机械臂使能...")
            enable_result = self.handshake_robot.enable_robot()
            print(f"DEBUG: 使能结果: {enable_result}")
            print("✅ 机械臂使能成功")
            
            # 初始化灵巧手控制
            print("🤲 初始化灵巧手...")
            self.handshake_action = hand_control()
            print("✅ 灵巧手连接成功")
            
            self.handshake_connected = True
            print("✅ 握手系统完全初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ 握手系统初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_handshake_positions(self) -> list:
        """加载握手位置数据"""
        try:
            with open(self.config.handshake_positions_file, 'r') as f:
                positions = json.load(f)
            print(f"✅ 加载握手位置数据: {len(positions)} 个位置")
            return positions
        except Exception as e:
            print(f"❌ 加载握手位置失败: {e}")
            return None
    
    def _load_handshake_reverse_positions(self) -> list:
        """加载握手返回位置数据"""
        try:
            with open(self.config.handshake_reverse_positions_file, 'r') as f:
                positions = json.load(f)
            print(f"✅ 加载返回位置数据: {len(positions)} 个位置")
            return positions
        except Exception as e:
            print(f"❌ 加载返回位置失败: {e}")
            return None
    
    def _perform_handshake_sequence(self, positions: list, positions_reverse: list):
        """执行完整的握手序列"""
        try:
            print(f"🎬 开始握手序列，位置数据: {len(positions)} 个前进位置, {len(positions_reverse)} 个返回位置")
            
            # 1. 移动到握手位置
            print("🤖 移动到握手位置...")
            move_message = "我正在移动到握手位置，请伸出您的手"
            self._text_to_speech(move_message)
            
            print("🔄 开始复现握手位置...")
            self._replay_positions(positions)
            print("✅ 握手位置移动完成")
            
            # 2. 等待用户伸手并执行握手
            print("🤝 等待用户伸手...")
            wait_message = "请伸出您的手，我会轻轻握住"
            self._text_to_speech(wait_message)
            
            print("🔍 开始执行握手检测...")
            self._execute_safe_handshake()
            print("✅ 握手动作完成")
            
            # 3. 返回初始位置
            print("🔄 返回初始位置...")
            return_message = "很高兴和您握手！"
            self._text_to_speech(return_message)
            
            print("🔄 开始复现返回位置...")
            self._replay_positions(positions_reverse)
            print("✅ 返回位置移动完成")
            
            print("✅ 握手流程完成")
            
        except Exception as e:
            print(f"❌ 握手序列执行失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _replay_positions(self, positions: list):
        """复现机械臂运动位置"""
        for i, position in enumerate(positions):
            print(f"🤖 移动到位置 {i+1}/{len(positions)}")
            
            # 使用关节运动，阻塞模式
            ret = self.handshake_robot.joint_move(position, 0, True, 0.3)
            
            if ret[0] != 0:
                raise Exception(f"机械臂移动失败，错误码: {ret[0]}")
    
    def _execute_safe_handshake(self):
        """执行安全握手动作（来自woshou.py的逻辑）"""
        try:
            # 灵巧手参数设置
            open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            close_angle = [60, 20, 90, 0, 53, 0, 90, 90, 90]
            speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]
            currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
            
            # 传感器阈值配置
            group_thresholds = [30, 25, 25, 20, 15]
            safety_limit = 1200
            min_groups = 2  # 需要至少2个传感器组触发
            
            # 初始化：张开手
            self.handshake_action.RS485_AngleSend(open_angle, speedval, currentval)
            time.sleep(2)
            
            print("👋 等待用户伸手触发传感器...")
            
            # 等待传感器触发
            max_wait_time = 10.0  # 最大等待10秒
            start_time = time.time()
            
            while (time.time() - start_time) < max_wait_time:
                try:
                    sensor_data = self.handshake_action.RS485_SenSor()
                    
                    # 检查触发的传感器组
                    triggered_groups = []
                    for group_idx in range(5):
                        max_val = max(sensor_data[group_idx])
                        if max_val > group_thresholds[group_idx]:
                            triggered_groups.append(group_idx)
                    
                    # 判断是否满足触发条件
                    if len(triggered_groups) >= min_groups:
                        print(f"🎯 检测到用户伸手！触发传感器组: {triggered_groups}")
                        
                        # 执行安全握手
                        print("🤝 开始握手...")
                        success = self._safe_close_hand(close_angle, speedval, currentval, safety_limit)
                        
                        if success:
                            print("✅ 握手成功")
                            # 握手持续指定时间
                            time.sleep(self.config.handshake_hold_time)
                        else:
                            print("⚠️ 握手过程中触发安全保护")
                        
                        # 松开手
                        print("👋 松开手...")
                        self.handshake_action.RS485_AngleSend(open_angle, speedval, currentval)
                        time.sleep(2)
                        return
                        
                except Exception as e:
                    print(f"⚠️ 传感器读取错误: {e}")
                    time.sleep(0.5)
                
                time.sleep(0.1)
            
            print("⏰ 等待超时，未检测到用户伸手")
            timeout_message = "没有检测到您的手，握手取消了"
            self._text_to_speech(timeout_message)
            
        except Exception as e:
            print(f"❌ 握手动作执行失败: {e}")
            raise
    
    def _safe_close_hand(self, close_angle: list, speedval: list, currentval: list, safety_limit: int) -> bool:
        """安全闭手函数：在闭手过程中监控力度，超过安全限制立即停止"""
        print("🤝 开始安全握手...")
        
        # 启动闭手动作
        self.handshake_action.RS485_AngleSend(close_angle, speedval, currentval)
        
        # 监控闭手过程中的力度
        start_time = time.time()
        max_monitor_time = 5  # 最大监控5秒
        
        try:
            while time.time() - start_time < max_monitor_time:
                # 读取传感器数据
                sensor_data = self.handshake_action.RS485_SenSor()
                
                # 计算全局最大值
                all_sensor_values = []
                for finger_idx in range(5):
                    finger_sensors = sensor_data[finger_idx]
                    all_sensor_values.extend(finger_sensors)
                
                current_max_force = max(all_sensor_values)
                
                print(f"\r握手中... 当前最大力度: {current_max_force:3d}", end="", flush=True)
                
                # 检查是否超过安全限制
                if current_max_force > safety_limit:
                    print(f"\n!!! 安全保护触发 !!! 力度 {current_max_force} 超过安全限制 {safety_limit}")
                    
                    # 立即停止所有运动
                    stop_flags = [1, 1, 1, 1, 1, 1, 1, 1, 1]
                    self.handshake_action.RS485_Stop(stop_flags)
                    print("已执行急停，保护安全")
                    
                    # 等待一下再解除急停
                    time.sleep(1)
                    self.handshake_action.RS485_LiftStop(stop_flags)
                    print("急停已解除")
                    
                    return False  # 返回False表示因安全保护而停止
                
                time.sleep(0.2)  # 200ms检查一次
            
            print("\n握手动作完成")
            return True  # 返回True表示正常完成
            
        except Exception as e:
            print(f"\n安全监控过程中发生错误: {e}")
            return False
    
    def _cleanup_handshake_system(self):
        """清理握手系统资源"""
        try:
            if self.handshake_robot:
                self.handshake_robot.logout()
                self.handshake_robot = None
                print("✅ 机械臂连接已关闭")
            
            if self.handshake_action:
                # 灵巧手没有特殊的关闭方法，直接设为None
                self.handshake_action = None
                print("✅ 灵巧手连接已关闭")
            
            self.handshake_connected = False
            
        except Exception as e:
            print(f"⚠️ 握手系统清理时出错: {e}")
    
    def _execute_grab_object(self, object_name: str):
        """执行抓取物品功能"""
        if not HANDSHAKE_AVAILABLE:
            print("❌ 抓取功能不可用，缺少必要的依赖")
            error_message = "抱歉，抓取功能暂时不可用"
            self._text_to_speech(error_message)
            return
        
        try:
            print(f"🤏 开始抓取{object_name}流程...")
            
            # 播放开始语音
            start_message = f"正在搜索{object_name}"
            print(f"🔊 [搜索物品]: {start_message}")
            self._text_to_speech(start_message)
            
            # 初始化抓取系统
            if not self._initialize_grab_system():
                return
            
            # 读取抓取位置数据
            positions_zhuaqu = self._load_grab_positions()
            positions_fangxia = self._load_place_positions() 
            positions_gohome = self._load_home_positions()
            
            if not positions_zhuaqu or not positions_fangxia or not positions_gohome:
                error_message = f"抱歉，{object_name}抓取位置数据加载失败"
                self._text_to_speech(error_message)
                return
            
            # 执行抓取流程
            self._perform_grab_sequence(object_name, positions_zhuaqu, positions_fangxia, positions_gohome)
            
        except Exception as e:
            print(f"❌ 抓取执行失败: {e}")
            error_message = f"抱歉，抓取{object_name}过程中出现了问题"
            self._text_to_speech(error_message)
        finally:
            # 清理抓取系统
            self._cleanup_grab_system()
    
    def _initialize_grab_system(self) -> bool:
        """初始化抓取系统"""
        try:
            print("🔧 初始化抓取系统...")
            
            # 初始化机械臂连接（复用握手系统的连接逻辑）
            self.handshake_robot = jkrc.RC(self.config.handshake_robot_host)
            self.handshake_robot.login()
            print("✅ 机械臂连接成功")
            
            self.handshake_robot.power_on()
            print("✅ 机械臂上电")
            
            self.handshake_robot.enable_robot()
            print("✅ 机械臂使能")
            
            # 初始化灵巧手控制
            self.handshake_action = hand_control()
            print("✅ 灵巧手连接成功")
            
            # 初始化：张开手
            open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]
            currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
            self.handshake_action.RS485_AngleSend(open_angle, speedval, currentval)
            
            self.handshake_connected = True
            return True
            
        except Exception as e:
            print(f"❌ 抓取系统初始化失败: {e}")
            return False
    
    def _load_grab_positions(self) -> list:
        """加载抓取位置数据"""
        try:
            with open('/home/xuanwu/jakaPythonSdk/json/zhuaqu.json', 'r') as f:
                positions = json.load(f)
            print(f"✅ 加载抓取位置数据: {len(positions)} 个位置")
            return positions
        except Exception as e:
            print(f"❌ 加载抓取位置失败: {e}")
            return None
    
    def _load_place_positions(self) -> list:
        """加载放置位置数据"""
        try:
            with open('/home/xuanwu/jakaPythonSdk/json/fangxia.json', 'r') as f:
                positions = json.load(f)
            print(f"✅ 加载放置位置数据: {len(positions)} 个位置")
            return positions
        except Exception as e:
            print(f"❌ 加载放置位置失败: {e}")
            return None
    
    def _load_home_positions(self) -> list:
        """加载回家位置数据"""
        try:
            with open('/home/xuanwu/jakaPythonSdk/json/go_home.json', 'r') as f:
                positions = json.load(f)
            print(f"✅ 加载回家位置数据: {len(positions)} 个位置")
            return positions
        except Exception as e:
            print(f"❌ 加载回家位置失败: {e}")
            return None
    
    def _perform_grab_sequence(self, object_name: str, positions_zhuaqu: list, positions_fangxia: list, positions_gohome: list):
        """执行完整的抓取序列"""
        try:
            # 1. 移动到抓取位置
            print(f"🤖 移动到{object_name}抓取位置...")
            move_message = f"发现{object_name}，正在抓取"
            self._text_to_speech(move_message)
            
            self._replay_positions(positions_zhuaqu)
            
            # 2. 执行抓取动作
            print(f"🤏 执行抓取{object_name}...")
            grab_message = f"正在抓取{object_name}"
            
            self._execute_adaptive_force_grasp()
            
            # 3. 移动到放置位置
            print("🤖 移动到放置位置...")
            place_message = f"已抓取{object_name}，正在放置"
            self._text_to_speech(place_message)
            
            self._replay_positions(positions_fangxia)
            
            # 4. 放下物品
            print(f"📦 放下{object_name}...")
            release_message = f"正在放下{object_name}"
            
            time.sleep(2)
            # 张开手放下物品
            open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]
            currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
            self.handshake_action.RS485_AngleSend(open_angle, speedval, currentval)
            time.sleep(1)
            
            # 5. 返回初始位置
            print("🔄 返回初始位置...")
            complete_message = f"{object_name}抓取任务完成"
            self._text_to_speech(complete_message)
            
            self._replay_positions(positions_gohome)
            
            print(f"✅ {object_name}抓取流程完成")
            
        except Exception as e:
            print(f"❌ 抓取序列执行失败: {e}")
            raise
    
    def _execute_adaptive_force_grasp(self):
        """执行自适应力度抓取（来自zhuaqu.py的逻辑）"""
        try:
            # 灵巧手参数设置
            close_angle = [60, 20, 90, 0, 53, 0, 90, 90, 90]
            speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]
            currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
            safety_limit = 1200
            
            print("🤏 开始自适应力度抓取...")
            
            # 使用安全闭手函数
            success = self._safe_close_hand(close_angle, speedval, currentval, safety_limit)
            
            if success:
                print("✅ 智能安全抓取完成!")
            else:
                print("⚠️ 抓取过程中触发安全保护")
                
        except Exception as e:
            print(f"❌ 自适应抓取失败: {e}")
            raise
    
    def _cleanup_grab_system(self):
        """清理抓取系统资源（复用握手系统的清理逻辑）"""
        try:
            if self.handshake_robot:
                self.handshake_robot.logout()
                self.handshake_robot = None
                print("✅ 机械臂连接已关闭")
            
            if self.handshake_action:
                # 灵巧手没有特殊的关闭方法，直接设为None
                self.handshake_action = None
                print("✅ 灵巧手连接已关闭")
            
            self.handshake_connected = False
            
        except Exception as e:
            print(f"⚠️ 抓取系统清理时出错: {e}")
    
    def _warm_up_tts_engine(self):
        """TTS引擎预热 - 预加载常用回复，减少首次调用延迟"""
        try:
            # 常用的简短回复，用于预热TTS引擎
            warm_up_phrases = ["好的", "我明白了", "请稍等"]
            
            for phrase in warm_up_phrases:
                # 预热TTS引擎：写入文本但不播放
                with open(self.config.tts_text_file, 'w', encoding='utf-8') as f:
                    f.write(phrase)
                
                # 调用TTS生成但不播放音频，只是预热引擎
                try:
                    self.voice_cloner.speak()  # 这会生成音频文件但不播放
                except Exception:
                    pass  # 忽略预热过程中的错误
                    
        except Exception as e:
            # 预热失败不影响主流程，只记录错误
            pass
    
    
    def start_background_recognition(self):
        """
        启动后台面部识别循环
        """
        if self.recognition_thread and self.recognition_thread.is_alive():
            print("⚠️ 后台识别已在运行")
            return
        
        self.is_running = True
        self.recognition_thread = threading.Thread(target=self._background_recognition_loop, daemon=True)
        self.recognition_thread.start()
        print("🔍 后台面部识别循环已启动")
    
    def stop_background_recognition(self):
        """
        停止后台面部识别循环
        """
        self.is_running = False
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2.0)
        print("⏹️ 后台面部识别循环已停止")
    
    def _background_recognition_loop(self):
        """
        后台面部识别循环 - 在独立线程中运行
        """
        print("🔄 开始后台面部识别循环")
        
        try:
            while self.is_running:
                if self.state in [AgentState.SCANNING, AgentState.SEARCHING]:
                    # 执行人脸识别（通过API调用）
                    recognized_name, middle_pixel = self.face_system.recognize_person()
                    
                    if recognized_name and recognized_name != "Unknown":
                        # 发现已知用户
                        self._on_user_discovered(recognized_name, middle_pixel)
                    elif self.state == AgentState.SCANNING:
                        # 扫描模式下未发现用户，检查是否需要切换到搜索模式
                        current_time = time.time()
                        if (current_time - self.last_recognition_time) > self.config.unknown_user_timeout:
                            self._switch_to_search_mode()
                
                time.sleep(self.config.continuous_scan_interval)
                
        except Exception as e:
            print(f"❌ 后台识别循环出错: {e}")
        finally:
            print("🔄 后台面部识别循环结束")
    
    def _on_user_discovered(self, user_name: str, face_position: Optional[float]):
        """
        发现用户时的处理逻辑
        """
        self.current_user = user_name
        self.last_recognition_time = time.time()
        
        # 如果正在搜索，停止搜索并返回正面
        if self.state == AgentState.SEARCHING:
            print(f"🎯 搜索模式中发现用户: {user_name}")
            self.face_system.return_home()
            self.state = AgentState.SCANNING
        
        # 跟随用户
        if face_position is not None:
            self.face_system.follow_person(face_position, user_name)
        
        print(f"👤 发现用户: {user_name}")
    
    def _switch_to_search_mode(self):
        """
        切换到搜索模式
        """
        if self.state != AgentState.SEARCHING:
            print("🔍 未发现已知用户，切换到搜索模式")
            self.state = AgentState.SEARCHING
            self.search_current_angle = 0
            self.search_direction = 1
            self._start_search_sequence()
    
    def _start_search_sequence(self):
        """
        开始搜索序列 - 在后台线程中异步执行
        """
        def search_sequence():
            print(f"🔄 开始搜索序列: {self.config.search_angle_range[0]}° 到 {self.config.search_angle_range[1]}°")
            
            # 搜索范围
            min_angle, max_angle = self.config.search_angle_range
            current_angle = 0
            
            while self.state == AgentState.SEARCHING and self.is_running:
                # 转到下一个搜索位置
                next_angle = current_angle + (self.search_direction * self.config.search_step)
                
                # 检查边界并调转方向
                if next_angle > max_angle:
                    next_angle = max_angle
                    self.search_direction = -1
                elif next_angle < min_angle:
                    next_angle = min_angle
                    self.search_direction = 1
                
                # 转头
                print(f"🔍 搜索角度: {next_angle}°")
                self.face_system.turn_head(next_angle)
                current_angle = next_angle
                
                # 等待并检查是否发现用户
                time.sleep(self.config.search_delay)
                
                # 如果到达边界，反向搜索
                if current_angle == max_angle or current_angle == min_angle:
                    time.sleep(0.5)  # 在边界处多停留一会
        
        # 在独立线程中执行搜索
        search_thread = threading.Thread(target=search_sequence, daemon=True)
        search_thread.start()
    
    def wake_up(self) -> Optional[str]:
        """
        智能体被唤醒，返回当前识别到的用户名
        
        Returns:
            识别到的用户名，如果没有则为None
        """
        print("🌅 智能体被唤醒")
        
        # 如果当前正在对话，直接返回当前用户
        if self.state == AgentState.CHATTING and self.current_user:
            print(f"💬 继续与 {self.current_user} 的对话")
            return self.current_user
        
        # 切换到扫描模式
        self.state = AgentState.SCANNING
        self.last_recognition_time = time.time()
        
        # 启动后台识别（如果还没启动）
        if not self.recognition_thread or not self.recognition_thread.is_alive():
            self.start_background_recognition()
        
        # 等待一段时间尝试识别用户
        max_wait_time = 3.0  # 最多等待3秒
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            if self.current_user and self.current_user != "Unknown":
                print(f"✅ 识别到用户: {self.current_user}")
                return self.current_user
            time.sleep(0.1)
        
        # 如果没有立即识别到用户，触发搜索模式
        print("❓ 未立即识别到用户，将进入搜索模式")
        self._switch_to_search_mode()
        
        # 等待搜索结果
        search_timeout = 10.0  # 搜索超时时间
        search_start = time.time()
        
        while (time.time() - search_start) < search_timeout:
            if self.current_user and self.current_user != "Unknown":
                print(f"🎯 搜索发现用户: {self.current_user}")
                return self.current_user
            time.sleep(0.2)
        
        print("⚠️ 唤醒后未发现已注册用户")
        return None
    
    def start_conversation(self, user_name: str) -> bool:
        """
        开始与指定用户的对话
        
        Args:
            user_name: 用户名
            
        Returns:
            是否成功开始对话
        """
        try:
            self.memory_agent.start_chat(user_name)
            self.state = AgentState.CHATTING
            self.current_user = user_name
            print(f"💬 已开始与 {user_name} 的对话")
            return True
        except Exception as e:
            print(f"❌ 开始对话失败: {e}")
            return False
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入并返回回复
        
        Args:
            user_input: 用户输入
            
        Returns:
            智能体回复
        """
        if self.state != AgentState.CHATTING:
            return "请先唤醒我并开始对话。"
        
        try:
            response = self.memory_agent.chat(user_input)
            
            # 检查是否为告别语，如果是则结束对话
            goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话', 'quit', 'exit']
            if any(pattern in user_input.lower() for pattern in goodbye_patterns):
                self.end_conversation()
            
            return response
        except Exception as e:
            print(f"❌ 对话处理失败: {e}")
            return "抱歉，我遇到了一些问题。"
    
    def end_conversation(self):
        """
        结束当前对话
        """
        if self.state == AgentState.CHATTING:
            print(f"👋 结束与 {self.current_user} 的对话")
            
            # 让记忆系统保存对话记录
            try:
                self.memory_agent.end_conversation()
            except Exception as e:
                print(f"⚠️ 保存对话记录时出错: {e}")
            
            # 重置状态
            self.state = AgentState.SCANNING
            self.current_user = None
            
            # 机械臂回到正面
            self.face_system.return_home()
            
            print("🔄 返回扫描模式")
    
    def get_current_state(self) -> Dict:
        """
        获取当前状态信息
        """
        return {
            "state": self.state.value,
            "current_user": self.current_user,
            "current_confidence": self.current_confidence,
            "is_running": self.is_running,
            "last_recognition_time": self.last_recognition_time
        }
    
    def cleanup(self):
        """
        清理资源
        """
        print("🧹 清理超级智能体资源...")
        
        # 停止后台识别
        self.stop_background_recognition()
        
        # 结束当前对话
        if self.state == AgentState.CHATTING:
            self.end_conversation()
        
        # 清理面部识别系统并关闭服务
        self.face_system.cleanup()
        
        # 关闭面部识别服务
        try:
            print("🛑 正在关闭面部识别服务...")
            import requests
            response = requests.post(f"{self.face_system.base_url}/api/shutdown", timeout=5)
            if response.status_code == 200:
                print("✅ 面部识别服务已关闭")
            else:
                print("⚠️ 面部识别服务关闭请求已发送")
        except Exception as e:
            print(f"⚠️ 关闭面部识别服务失败: {e}")
        
        # 断开机器人连接
        if self.move_connected:
            self.move_controller.disconnect()
            self.marker_manager.disconnect()
            self.move_connected = False
        
        print("✅ 超级智能体资源清理完成")
    
    def _start_face_tracking_thread(self):
        """启动人脸跟踪线程"""
        if not self.config.enable_conversation_tracking:
            print("⚠️ 对话跟踪已禁用，跳过启动跟踪线程")
            return
            
        print("👁️ 启动对话期间的人脸跟踪")
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
            print("👁️ 停止对话期间的人脸跟踪")
    
    def _face_tracking_loop(self):
        """人脸跟踪循环（对话期间运行）"""
        try:
            while (hasattr(self, 'face_tracking_active') and 
                   self.face_tracking_active and 
                   self.state == AgentState.CHATTING):
                
                # 获取当前识别结果
                recognized_name, middle_pixel = self.face_system.recognize_person()
                
                # 如果识别到用户，进行跟踪
                if recognized_name and recognized_name != "Unknown":
                    self.face_system.follow_person(middle_pixel, recognized_name)
                
                time.sleep(0.5)  # 跟踪频率
                
        except Exception as e:
            print(f"❌ 人脸跟踪出错: {e}")
        finally:
            print("🔄 人脸跟踪循环结束")

# 使用示例和测试函数
def create_default_config() -> SuperAgentConfig:
    """
    创建默认配置
    """
    # 从环境变量读取配置（如果有）
    import os
    enable_conversation_tracking = os.environ.get('CONVERSATION_TRACKING', 'True').lower() == 'true'
    
    face_config = FaceRecognitionConfig(
        service_url="http://localhost:5001",
        recognition_threshold=0.6,
        left_threshold=300,
        right_threshold=340,
        follow_delta_angle=15
    )
    
    return SuperAgentConfig(
        face_config=face_config,
        deepseek_api_key="sk-fdabadb2973b4795b2444da60e75152f",  # 请替换为实际的API密钥
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
        
        # 人脸跟踪配置
        enable_conversation_tracking=enable_conversation_tracking,
        
        # 其他配置
        search_angle_range=(-60, 60),
        search_step=15,
        search_delay=2.0,
        recognition_confidence_threshold=0.6,
        continuous_scan_interval=0.5,
        unknown_user_timeout=5.0
    )

def main():
    """
    主函数 - 语音唤醒模式的超级智能体
    """
    print("🚀 启动超级智能体 - 语音唤醒模式")
    
    # 创建配置
    config = create_default_config()
    
    # 创建超级智能体
    agent = SuperIntelligentAgent(config)
    
    try:
        # 初始化系统
        if not agent.initialize():
            print("❌ 系统初始化失败")
            return
        
        print("\n" + "="*60)
        print("🤖 超级智能体已启动 - 语音唤醒模式")
        print("🎧 系统将持续监听语音唤醒词")
        print("💬 请说 '小助小助' 来唤醒智能体")
        print("🔄 完整流程: 语音唤醒 → 面部识别 → 个性化问候 → 智能对话")
        print("🤖 支持功能: 人脸识别/注册、机器人移动、TTS语音回复")
        print("="*60 + "\n")
        
        # 启动语音唤醒监听（这是一个阻塞调用）
        agent.start_voice_wake_listening()
        
    except KeyboardInterrupt:
        print("\n🛑 检测到中断信号")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")
    finally:
        # 清理资源
        agent.cleanup()
        print("👋 超级智能体已关闭")

if __name__ == "__main__":
    main()