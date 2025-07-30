#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能养老协助机器人演示系统
功能包括：
1. 语音交互（录音→ASR→DeepSeek→TTS→播放）
2. 函数调用能力（人脸识别/注册、移动控制）
3. 语音播放与移动工具并发执行
4. 记忆系统集成（对话结束后保存记忆点）
5. 自然的对话结束检测
"""

import os
import sys
import json
import threading
import time
from datetime import datetime

# 添加路径以导入所需模块
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from openai import OpenAI
from audio_recorder import AudioRecorder
from spark_asr import SparkASR
from voice_cloner import VoiceCloner
from memory_agent import MemoryAgent
from move_controller import MoveController


class IntelligentAgent:
    """
    智能养老协助机器人主类
    集成语音交互、函数调用、移动控制和记忆系统
    """
    
    def __init__(self):
        # API配置
        self.deepseek_api_key = "sk-a4ce2451fc534091aff7704e5498a698"
        self.deepseek_base_url = "https://api.deepseek.com"
        
        # 讯飞API配置
        self.xf_app_id = 'b32f165e'
        self.xf_api_key = 'bf4caffa0bd087acc04cd63d0ee27fc5'
        self.xf_api_secret = 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0'
        
        # 文件路径配置
        self.work_dir = "/home/xuanwu/haven_ws/demos/temp"
        self.audio_file = os.path.join(self.work_dir, "input.wav")
        self.asr_result_file = os.path.join(self.work_dir, "user_input.txt")
        self.tts_text_file = os.path.join(self.work_dir, "reply.txt")
        self.tts_audio_file = os.path.join(self.work_dir, "reply.wav")
        
        # 创建工作目录
        os.makedirs(self.work_dir, exist_ok=True)
        
        # 初始化DeepSeek客户端
        self.client = OpenAI(
            api_key=self.deepseek_api_key,
            base_url=self.deepseek_base_url
        )
        
        # 初始化记忆系统
        self.memory_agent = MemoryAgent(
            deepseek_api_key=self.deepseek_api_key,
            deepseek_base_url=self.deepseek_base_url,
            memory_file_path='/home/xuanwu/haven_ws/demos/data/memory_tree.json'
        )
        
        # 初始化语音组件
        self.audio_recorder = AudioRecorder()
        self.asr = None  # 将在使用时初始化
        self.voice_cloner = VoiceCloner(
            app_id=self.xf_app_id,
            api_key=self.xf_api_key,
            api_secret=self.xf_api_secret,
            text_file=self.tts_text_file,
            output_file=self.tts_audio_file
        )
        
        # 初始化移动控制器
        self.move_controller = MoveController()
        self.move_connected = False
        
        # 当前对话状态
        self.current_person_name = "用户"  # 默认用户名
        self.conversation_active = False
        
        # 定义工具函数
        self.tools = self._define_tools()
        
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
                            }
                        },
                        "required": ["distance"]
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
                            }
                        },
                        "required": ["distance"]
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
                            }
                        },
                        "required": ["angle"]
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
                            }
                        },
                        "required": ["angle"]
                    },
                }
            },
            # 移动到标记点
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
                                "description": "目标位置的标记点名称，如'客厅'、'厨房'、'卧室'等",
                            }
                        },
                        "required": ["location_name"]
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
                        "properties": {},
                    },
                }
            }
        ]
    
    def connect_robot(self):
        """连接到机器人移动控制系统"""
        if not self.move_connected:
            self.move_connected = self.move_controller.connect()
            if self.move_connected:
                print("✅ 机器人移动系统连接成功")
            else:
                print("❌ 机器人移动系统连接失败，移动功能将不可用")
        return self.move_connected
    
    def disconnect_robot(self):
        """断开机器人连接"""
        if self.move_connected:
            self.move_controller.disconnect()
            self.move_connected = False
            print("机器人移动系统已断开连接")
    
    def start_conversation(self, person_name=None):
        """开始新的对话会话"""
        if person_name:
            self.current_person_name = person_name
        
        # 启动记忆系统的对话会话
        self.memory_agent.start_chat(self.current_person_name)
        self.conversation_active = True
        
        print(f"开始与 {self.current_person_name} 的对话")
        print("机器人已准备就绪，请开始语音交互...")
    
    def _wait_for_thread_with_interrupt(self, thread, thread_name, timeout=0.1):
        """
        等待线程完成，但允许KeyboardInterrupt中断
        """
        try:
            while thread.is_alive():
                thread.join(timeout)
        except KeyboardInterrupt:
            print(f"\n⚠️  {thread_name}线程被中断")
            raise
    
    def record_audio(self, timeout=10):
        """录制音频 - 使用智能动态录音"""
        print("🎤 开始智能录音，请说话（前2秒为准备时间，说完后稍等片刻会自动结束）...")
        
        try:
            # 使用动态录音功能
            self.audio_recorder.start_dynamic_recording(
                output_file=self.audio_file,
                enable_vad=True,
                debug_output=False  # 设为True可查看详细VAD信息
            )
            
            # 简单判断：文件是否存在且不为空
            if os.path.exists(self.audio_file) and os.path.getsize(self.audio_file) > 0:
                print("✅ 录音完成")
                return True
            else:
                print("❌ 录音失败或文件为空")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️  录音被用户中断")
            raise
    
    def speech_to_text(self):
        """语音识别 - 简化版本，参考main_dialog.py"""
        print("🔄 正在识别语音...")
        asr_start = time.time()
        
        # 初始化ASR（每次使用时重新初始化以避免连接问题）
        init_start = time.time()
        self.asr = SparkASR(
            app_id=self.xf_app_id,
            api_key=self.xf_api_key,
            api_secret=self.xf_api_secret,
            audio_file=self.audio_file,
            output_file=self.asr_result_file
        )
        init_time = time.time() - init_start
        print(f"    ⏱️  ASR初始化耗时: {init_time:.2f}秒")
        
        # 执行语音识别
        recognize_start = time.time()
        self.asr.recognize()
        recognize_time = time.time() - recognize_start
        print(f"    ⏱️  语音识别处理耗时: {recognize_time:.2f}秒")
        
        # 简单判断：识别结果文件是否存在且不为空
        file_start = time.time()
        if os.path.exists(self.asr_result_file) and os.path.getsize(self.asr_result_file) > 0:
            with open(self.asr_result_file, 'r', encoding='utf-8') as f:
                user_input = f.read().strip()
            
            if user_input:
                file_time = time.time() - file_start
                total_asr_time = time.time() - asr_start
                print(f"    ⏱️  结果文件读取耗时: {file_time:.2f}秒")
                print(f"    ⏱️  ASR总耗时: {total_asr_time:.2f}秒 (初始化: {init_time:.1f}s + 识别: {recognize_time:.1f}s)")
                print(f"✅ 识别结果: {user_input}")
                
                # 语音识别成功后删除录音文件
                try:
                    if os.path.exists(self.audio_file):
                        os.remove(self.audio_file)
                        print("🗑️  录音文件已删除")
                except:
                    pass  # 删除失败不影响主流程
                
                return user_input
        
        print("❌ 语音识别失败或结果为空")
        return None
    
    def get_assistant_response(self, user_input):
        """获取智能助手回复"""
        print("🤖 正在生成回复...")
        method_start = time.time()
        
        try:
            # 直接获取相关记忆，不调用memory_agent.chat（避免触发记忆整理）
            # 获取相关记忆
            memory_start = time.time()
            retrieved_memories = self.memory_agent.memory_tree.search(user_input, similarity_threshold=0.6, max_results=3)
            memory_search_time = time.time() - memory_start
            print(f"    ⏱️  记忆检索耗时: {memory_search_time:.2f}秒")
            
            # 格式化记忆上下文
            memory_context = ""
            if retrieved_memories:
                memory_context = "\n\n相关记忆:\n"
                for i, memory in enumerate(retrieved_memories, 1):
                    memory_context += f"{i}. {memory['summary']} (相似度: {memory['similarity']:.2f})\n"
            
            # 获取个人画像信息
            profile_start = time.time()
            profile_info = ""
            if self.memory_agent.current_person_profile:
                profile_data = self.memory_agent.current_person_profile.attributes
                profile_info = f"\n\n用户画像: {json.dumps(profile_data, ensure_ascii=False)}"
            profile_time = time.time() - profile_start
            print(f"    ⏱️  画像格式化耗时: {profile_time:.2f}秒")
            
            # 构建完整的系统提示词
            system_prompt = f"""你是一个养老机构的智能协助机器人，你的名字叫小助。你的任务是协助老年人的日常生活，包括：
1. 回答问题和日常聊天
2. 协助人脸识别和注册
3. 帮助老人在机构内移动和导航
4. 提供生活上的关怀和帮助

你的特点：
- 语言通俗易懂，简单明了，适合老年人理解
- 语气亲切温和，像家人一样关怀
- 回复简洁，不超过50字
- 当你觉得这次对话可能要结束时，可以主动问"您还有什么需要我帮忙的吗？"
- 如果用户明确表示不需要更多帮助或要结束对话，请在回复末尾添加 [CONVERSATION_END]

当前对话对象：{self.current_person_name}{profile_info}{memory_context}"""
            
            # 使用DeepSeek API生成回复
            api_start = time.time()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools
            )
            api_time = time.time() - api_start
            print(f"    ⏱️  DeepSeek API调用耗时: {api_time:.2f}秒")
            
            assistant_response = response.choices[0].message.content
            
            # 检查是否包含对话结束标记
            conversation_should_end = False
            if "[CONVERSATION_END]" in assistant_response:
                conversation_should_end = True
                assistant_response = assistant_response.replace("[CONVERSATION_END]", "").strip()

            # 检查显式告别关键词
            goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话', 'quit', 'exit']
            if any(pattern in user_input.lower() for pattern in goodbye_patterns):
                conversation_should_end = True

            total_method_time = time.time() - method_start
            print(f"    ⏱️  回复生成子步骤总耗时: {total_method_time:.2f}秒")

            return assistant_response, conversation_should_end, response.choices[0].message, user_input
            
        except Exception as e:
            print(f"❌ 获取回复失败: {e}")
            return "抱歉，我现在有点不舒服，您稍后再试试吧。", False, None, user_input
    
    def text_to_speech_and_play(self, text):
        """文本转语音并播放"""
        print("🔊 正在生成语音...")
        tts_start = time.time()
        
        try:
            # 将文本写入文件
            file_start = time.time()
            with open(self.tts_text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            file_time = time.time() - file_start
            print(f"    ⏱️  文本写入耗时: {file_time:.2f}秒")
            
            # 生成语音
            synthesis_start = time.time()
            self.voice_cloner.speak()
            synthesis_time = time.time() - synthesis_start
            print(f"    ⏱️  语音合成耗时: {synthesis_time:.2f}秒")
            
            # 播放语音
            play_start = time.time()
            print("📢 正在播放语音...")
            self.voice_cloner.play_audio()
            play_time = time.time() - play_start
            print(f"    ⏱️  语音播放耗时: {play_time:.2f}秒")
            
            total_tts_time = time.time() - tts_start
            print(f"    ⏱️  TTS总耗时: {total_tts_time:.2f}秒 (合成: {synthesis_time:.1f}s + 播放: {play_time:.1f}s)")
            
            return True
            
        except Exception as e:
            print(f"❌ 语音合成或播放失败: {e}")
            return False
    
    def execute_tool_function(self, tool_call):
        """执行工具函数"""
        tool_name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            arguments = {}
        
        print(f"🔧 执行工具: {tool_name}")
        
        success = True
        error_message = ""
        
        try:
            if tool_name == "recognize_face":
                success = self._execute_face_recognition()
                
            elif tool_name == "register_face":
                user_name = arguments.get("user_name", "")
                success = self._execute_face_registration(user_name)
                
            elif tool_name == "move_forward":
                distance = arguments.get("distance", 0)
                success = self._execute_move_forward(distance)
                
            elif tool_name == "move_backward":
                distance = arguments.get("distance", 0)
                success = self._execute_move_backward(distance)
                
            elif tool_name == "turn_left":
                angle = arguments.get("angle", 0)
                success = self._execute_turn_left(angle)
                
            elif tool_name == "turn_right":
                angle = arguments.get("angle", 0)
                success = self._execute_turn_right(angle)
                
            elif tool_name == "move_to_location":
                location_name = arguments.get("location_name", "")
                success = self._execute_move_to_location(location_name)
                
            elif tool_name == "cancel_move":
                success = self._execute_cancel_move()
                
            else:
                success = False
                error_message = f"未知的工具函数: {tool_name}"
                
        except Exception as e:
            success = False
            error_message = str(e)
        
        if not success and error_message:
            print(f"❌ 工具执行失败: {error_message}")
        
        return success, error_message
    
    def _execute_face_recognition(self):
        """执行人脸识别"""
        try:
            os.system("/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/recognize.py")
            print("✅ 人脸识别任务已启动")
            return True
        except Exception as e:
            print(f"❌ 人脸识别失败: {e}")
            return False
    
    def _execute_face_registration(self, user_name):
        """执行人脸注册"""
        try:
            command = f"/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/register.py {user_name}"
            os.system(command)
            print(f"✅ 人脸注册任务已启动: {user_name}")
            return True
        except Exception as e:
            print(f"❌ 人脸注册失败: {e}")
            return False
    
    def _execute_move_forward(self, distance):
        """执行前进移动"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return False
        
        try:
            self.move_controller.move_linear_for_distance(distance)
            print(f"✅ 前进 {distance} 米")
            return True
        except Exception as e:
            print(f"❌ 前进移动失败: {e}")
            return False
    
    def _execute_move_backward(self, distance):
        """执行后退移动"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return False
        
        try:
            self.move_controller.move_linear_for_distance(-distance)
            print(f"✅ 后退 {distance} 米")
            return True
        except Exception as e:
            print(f"❌ 后退移动失败: {e}")
            return False
    
    def _execute_turn_left(self, angle):
        """执行左转"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法转动")
            return False
        
        try:
            self.move_controller.move_angular_for_angle(angle)
            print(f"✅ 左转 {angle} 度")
            return True
        except Exception as e:
            print(f"❌ 左转失败: {e}")
            return False
    
    def _execute_turn_right(self, angle):
        """执行右转"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法转动")
            return False
        
        try:
            self.move_controller.move_angular_for_angle(-angle)
            print(f"✅ 右转 {angle} 度")
            return True
        except Exception as e:
            print(f"❌ 右转失败: {e}")
            return False
    
    def _execute_move_to_location(self, location_name):
        """执行移动到指定位置"""
        if not self.move_connected:
            print("❌ 机器人未连接，无法移动")
            return False
        
        try:
            response = self.move_controller.move_to_marker(location_name)
            if response and response.get("status") == "OK":
                print(f"✅ 正在前往 {location_name}")
                return True
            else:
                print(f"❌ 移动到 {location_name} 失败")
                return False
        except Exception as e:
            print(f"❌ 移动到位置失败: {e}")
            return False
    
    def _execute_cancel_move(self):
        """执行取消移动"""
        if not self.move_connected:
            print("❌ 机器人未连接")
            return False
        
        try:
            response = self.move_controller.cancel_move()
            if response and response.get("status") == "OK":
                print("✅ 已取消当前移动任务")
                return True
            else:
                print("❌ 取消移动失败")
                return False
        except Exception as e:
            print(f"❌ 取消移动失败: {e}")
            return False
    
    def process_single_interaction(self):
        """处理单次交互流程"""
        interaction_start = time.time()
        print(f"\n⏱️  开始新的交互 ({datetime.now().strftime('%H:%M:%S')})")
        
        try:
            # 1. 录音
            step_start = time.time()
            if not self.record_audio():
                return False, False
            record_time = time.time() - step_start
            print(f"⏱️  录音耗时: {record_time:.2f}秒")
            
            # 2. 语音识别
            step_start = time.time()
            user_input = self.speech_to_text()
            if not user_input:
                return False, False
            asr_time = time.time() - step_start
            print(f"⏱️  语音识别耗时: {asr_time:.2f}秒")
            
            # 3. 获取助手回复（包含个人画像和记忆，但不进行记忆整理）
            step_start = time.time()
            assistant_response, conversation_should_end, message, original_user_input = self.get_assistant_response(user_input)
            llm_time = time.time() - step_start
            print(f"⏱️  LLM回复生成耗时: {llm_time:.2f}秒")
            
            # 4. 先播放语音告别，再处理对话结束
            # 创建线程用于并发执行语音播放和工具调用
            tts_thread = None
            tool_threads = []
            
            # 启动语音合成和播放线程
            tts_start = time.time()
            tts_thread = threading.Thread(
                target=self.text_to_speech_and_play, 
                args=(assistant_response,),
                daemon=True  # 设置为守护线程，主程序退出时自动结束
            )
            tts_thread.start()
            
            # 5. 检查是否需要执行工具函数
            tool_start = time.time()
            if message and hasattr(message, "tool_calls") and message.tool_calls:
                # 并发执行所有工具调用
                for tool_call in message.tool_calls:
                    tool_thread = threading.Thread(
                        target=self.execute_tool_function,
                        args=(tool_call,),
                        daemon=True  # 设置为守护线程
                    )
                    tool_thread.start()
                    tool_threads.append(tool_thread)
            
            # 6. 等待语音播放完成
            if tts_thread:
                self._wait_for_thread_with_interrupt(tts_thread, "语音播放")
            tts_time = time.time() - tts_start
            print(f"⏱️  TTS语音合成+播放耗时: {tts_time:.2f}秒")
            
            # 7. 等待工具执行完成
            for i, thread in enumerate(tool_threads):
                self._wait_for_thread_with_interrupt(thread, f"工具执行{i+1}")
            tool_time = time.time() - tool_start
            if tool_threads:
                print(f"⏱️  工具函数执行耗时: {tool_time:.2f}秒")
            
            # 8. 语音播放完成后，再进行记忆处理（后台进行，不影响用户体验）
            memory_start = time.time()
            if not conversation_should_end:
                # 只在对话未结束时添加对话轮次，对话结束时会在end_conversation中统一处理
                self.memory_agent.memory_tree.add_conversation_turn(original_user_input, assistant_response)
            memory_time = time.time() - memory_start
            print(f"⏱️  记忆处理耗时: {memory_time:.2f}秒")
            
            # 总耗时统计
            total_time = time.time() - interaction_start
            print(f"⏱️  📊 单次交互总耗时: {total_time:.2f}秒")
            print(f"    └─ 录音: {record_time:.1f}s | ASR: {asr_time:.1f}s | LLM: {llm_time:.1f}s | TTS: {tts_time:.1f}s")
            
            return True, conversation_should_end
            
        except KeyboardInterrupt:
            print("\n⚠️  交互被用户中断")
            raise  # 重新抛出KeyboardInterrupt以便上层处理
    
    def run_conversation_loop(self):
        """运行完整的对话循环"""
        if not self.conversation_active:
            print("❌ 请先启动对话会话")
            return False  # 返回False表示未成功开始对话
        
        print("开始语音交互循环... (按Ctrl+C可随时退出)")
        
        try:
            while self.conversation_active:
                try:
                    success, should_end = self.process_single_interaction()
                    
                    if not success:
                        print("交互失败，请重试...")
                        continue
                    
                    if should_end:
                        print("\n检测到对话结束")
                        print("正在整理对话记忆...")
                        self.end_conversation()
                        print("对话已结束，程序即将退出")
                        return True  # 返回True表示正常结束对话
                        
                except KeyboardInterrupt:
                    print("\n用户中断对话")
                    self.end_conversation()
                    return True  # 用户主动退出也返回True
                except Exception as e:
                    print(f"❌ 交互过程中发生错误: {e}")
                    # 询问用户是否继续
                    try:
                        continue_choice = input("是否继续对话？(y/n): ").strip().lower()
                        if continue_choice != 'y':
                            self.end_conversation()
                            return True
                    except KeyboardInterrupt:
                        print("\n用户选择退出")
                        self.end_conversation()
                        return True
                    
        except KeyboardInterrupt:
            print("\n对话循环被中断")
            self.end_conversation()
            return True
    
    def end_conversation(self):
        """结束当前对话"""
        if self.conversation_active:
            print(f"结束与 {self.current_person_name} 的对话")
            
            # 结束记忆系统的对话（会自动保存记忆点）
            memory_nodes = self.memory_agent.end_conversation()
            
            self.conversation_active = False
            print("对话已结束，记忆已保存")


def main():
    """主函数"""
    agent = None
    
    try:
        print("=" * 50)
        print("智能养老协助机器人演示系统")
        print("=" * 50)
        print("提示：程序运行过程中可随时按Ctrl+C退出")
        
        # 创建智能代理
        agent = IntelligentAgent()
        
        # 连接机器人（可选，如果连接失败仍可进行语音交互）
        agent.connect_robot()
        
        # 开始对话
        try:
            person_name = input("请输入用户姓名（直接回车使用'用户'）: ").strip()
            if not person_name:
                person_name = "用户"
        except KeyboardInterrupt:
            print("\n程序启动被用户中断")
            return
        
        print(f"✅ 已启用智能动态录音模式（自动检测语音结束）")
        
        agent.start_conversation(person_name)
        
        # 运行对话循环
        conversation_ended = agent.run_conversation_loop()
        
        if conversation_ended:
            print("对话正常结束，感谢使用！")
        else:
            print("对话启动失败")
            
        # 正常退出，不继续运行
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        if agent:
            try:
                agent.disconnect_robot()
                if agent.conversation_active:
                    agent.end_conversation()
            except:
                pass  # 忽略清理过程中的错误
        print("程序已安全退出")


if __name__ == "__main__":
    main()