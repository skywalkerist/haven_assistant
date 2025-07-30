#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音唤醒 + 智能对话整合演示系统
功能包括：
1. 语音唤醒监听（基于snowboy）
2. 唤醒后进入智能对话模式（完整的IntelligentAgent功能）
3. 对话结束后自动返回唤醒监听状态
4. 保持所有组件的初始化状态，避免重复加载
"""

import os
import sys
import signal
import threading
import time

# 添加路径以导入所需模块
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import snowboydecoder
from intelligent_agent_demo import IntelligentAgent


class VoiceWakeupConversationSystem:
    """
    语音唤醒 + 智能对话整合系统
    """
    
    def __init__(self, wake_model_path, sensitivity=0.5, sleep_time=0.03):
        """
        初始化系统
        
        Args:
            wake_model_path: snowboy模型文件路径
            sensitivity: 唤醒敏感度
            sleep_time: 检测间隔
        """
        # snowboy配置
        self.wake_model_path = wake_model_path
        self.sensitivity = sensitivity
        self.sleep_time = sleep_time
        self.detector = None
        self.interrupted = False
        
        # 音频文件路径
        self.greeting_audio = '/home/xuanwu/haven_ws/config/greeting.wav'
        
        # 智能对话代理（一次性初始化）
        print("正在初始化智能对话系统...")
        init_start = time.time()
        self.intelligent_agent = IntelligentAgent()
        
        # 连接机器人（可选）
        self.intelligent_agent.connect_robot()
        
        init_time = time.time() - init_start
        print(f"✅ 智能对话系统初始化完成，耗时: {init_time:.2f}秒")
        
        # 系统状态
        self.system_running = True
        
    def interrupt_callback(self):
        """中断检查回调"""
        return self.interrupted
        
    def signal_handler(self, signal, frame):
        """信号处理器"""
        print("\n接收到退出信号，正在安全关闭系统...")
        self.interrupted = True
        self.system_running = False
        
    def play_greeting(self):
        """播放问候语音"""
        if os.path.exists(self.greeting_audio):
            print("🔊 播放问候语音...")
            os.system(f'aplay -f S16_LE -r 16000 -c 1 {self.greeting_audio}')
        else:
            print("⚠️ 问候语音文件不存在，跳过播放")
            
    def wake_up_callback(self):
        """
        语音唤醒回调函数
        唤醒后进入智能对话模式
        """
        print("\n🎯 检测到唤醒词！")
        
        # 暂停snowboy检测
        if self.detector:
            self.detector.terminate()
            
        try:
            # 播放问候语音
            self.play_greeting()
            
            # 进入对话模式
            print("进入智能对话模式...")
            
            # 开始对话（使用默认用户名，也可以通过人脸识别获取）
            self.intelligent_agent.start_conversation("用户")
            
            # 运行对话循环，直到用户结束对话
            conversation_ended = self.intelligent_agent.run_conversation_loop()
            
            if conversation_ended:
                print("对话已结束，返回唤醒监听模式")
            else:
                print("对话异常结束，返回唤醒监听模式")
                
        except Exception as e:
            print(f"❌ 对话过程中发生错误: {e}")
            # 确保结束对话会话
            if self.intelligent_agent.conversation_active:
                self.intelligent_agent.end_conversation()
                
        finally:
            # 无论对话如何结束，都要返回监听模式
            if self.system_running:
                print("返回语音唤醒监听模式...")
                time.sleep(1)  # 短暂延迟避免立即触发
                self.start_wake_up_listening()
                
    def start_wake_up_listening(self):
        """开始语音唤醒监听"""
        if not self.system_running:
            return
            
        print('🎧 正在监听唤醒词... (按 Ctrl+C 停止运行)')
        
        try:
            # 创建新的detector实例
            self.detector = snowboydecoder.HotwordDetector(
                self.wake_model_path, 
                sensitivity=self.sensitivity
            )
            
            # 开始监听
            self.detector.start(
                detected_callback=self.wake_up_callback,
                interrupt_check=self.interrupt_callback,
                sleep_time=self.sleep_time
            )
            
        except Exception as e:
            print(f"❌ 唤醒监听出错: {e}")
        finally:
            if self.detector:
                self.detector.terminate()
                
    def run(self):
        """运行整个系统"""
        print("=" * 60)
        print("语音唤醒 + 智能对话整合演示系统")
        print("=" * 60)
        print("系统功能：")
        print("1. 持续监听唤醒词")
        print("2. 唤醒后自动进入智能对话模式")
        print("3. 对话结束后自动返回监听状态")
        print("4. 支持完整的AI功能（记忆、函数调用、移动控制等）")
        print("=" * 60)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # 开始唤醒监听
            self.start_wake_up_listening()
            
        except KeyboardInterrupt:
            print("\n系统被用户中断")
        except Exception as e:
            print(f"❌ 系统运行出错: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """清理资源"""
        print("正在清理系统资源...")
        
        self.system_running = False
        self.interrupted = True
        
        # 停止snowboy检测
        if self.detector:
            try:
                self.detector.terminate()
            except:
                pass
                
        # 清理智能对话代理
        if self.intelligent_agent:
            try:
                self.intelligent_agent.disconnect_robot()
                if self.intelligent_agent.conversation_active:
                    self.intelligent_agent.end_conversation()
            except:
                pass
                
        print("✅ 系统资源清理完成")


def main():
    """主函数"""
    try:
        # 创建语音唤醒对话系统
        system = VoiceWakeupConversationSystem(
            wake_model_path="/home/xuanwu/haven_ws/src/resources/haven.pmdl",
            sensitivity=0.5,
            sleep_time=0.03
        )
        
        # 运行系统
        system.run()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("程序已退出")


if __name__ == "__main__":
    main()