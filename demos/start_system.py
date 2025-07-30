#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级智能体启动脚本 - 完整的系统启动和关闭解决方案
"""

import os
import sys
import time
import subprocess
import requests
import signal
import psutil
from pathlib import Path

# 全局变量存储进程
face_service_process = None
shutdown_requested = False

def check_face_service():
    """检查face环境的识别服务是否运行"""
    try:
        response = requests.get("http://localhost:5001/api/status", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_face_service():
    """启动face环境的识别服务"""
    global face_service_process
    
    print("🚀 启动面部识别服务 (face环境)...")
    
    # 构建启动命令
    face_env_python = "/home/xuanwu/miniconda3/envs/face/bin/python"
    service_script = "/home/xuanwu/haven_ws/src/face_recognition_service.py"
    
    if not os.path.exists(face_env_python):
        print("❌ face环境的Python解释器未找到")
        print(f"请检查路径: {face_env_python}")
        return False
    
    if not os.path.exists(service_script):
        print("❌ 面部识别服务脚本未找到")
        print(f"请检查路径: {service_script}")
        return False
    
    # 启动service进程
    try:
        print(f"执行命令: {face_env_python} {service_script}")
        face_service_process = subprocess.Popen(
            [face_env_python, service_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/home/xuanwu/haven_ws/src"
        )
        
        # 等待服务启动
        print("⏳ 等待面部识别服务启动...")
        for i in range(20):  # 增加等待时间到20秒
            time.sleep(1)
            if check_face_service():
                print("✅ 面部识别服务启动成功")
                # 再等待一段时间让服务完全准备好
                print("⏳ 等待服务完全初始化...")
                time.sleep(3)
                return True
            print(f"等待中... ({i+1}/20)")
        
        print("❌ 面部识别服务启动超时")
        if face_service_process:
            face_service_process.terminate()
            face_service_process = None
        return False
        
    except Exception as e:
        print(f"❌ 启动面部识别服务失败: {e}")
        face_service_process = None
        return False

def signal_handler(sig, frame):
    """信号处理函数 - 处理Ctrl+C等中断信号"""
    global shutdown_requested
    print(f"\n🛑 接收到信号 {sig}，开始优雅关闭...")
    shutdown_requested = True
    cleanup_and_exit()

def cleanup_and_exit():
    """清理资源并退出"""
    global face_service_process
    
    print("🧹 正在清理资源...")
    
    # 1. 尝试通过API关闭面部识别服务
    try:
        print("🛑 通过API关闭面部识别服务...")
        response = requests.post("http://localhost:5001/api/shutdown", timeout=3)
        if response.status_code == 200:
            print("✅ 面部识别服务API关闭成功")
        time.sleep(2)  # 等待服务优雅关闭
    except Exception as e:
        print(f"⚠️ API关闭失败: {e}")
    
    # 2. 如果进程仍在运行，强制终止
    if face_service_process and face_service_process.poll() is None:
        try:
            print("🛑 强制终止面部识别服务进程...")
            face_service_process.terminate()
            face_service_process.wait(timeout=5)
            print("✅ 面部识别服务进程已终止")
        except subprocess.TimeoutExpired:
            print("⚠️ 进程未在5秒内终止，强制杀死...")
            face_service_process.kill()
        except Exception as e:
            print(f"⚠️ 终止进程失败: {e}")
    
    # 3. 清理任何残留的相关进程
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'face_recognition_service.py' in ' '.join(cmdline):
                    print(f"🛑 清理残留的面部识别服务进程 (PID: {proc.info['pid']})")
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"⚠️ 清理残留进程失败: {e}")
    
    print("✅ 资源清理完成")
    print("👋 系统已安全退出")
    sys.exit(0)

def shutdown_system():
    """一键关闭系统"""
    print("🛑 执行一键关闭...")
    cleanup_and_exit()

def get_face_tracking_config():
    """获取人脸跟踪配置"""
    # print("\n🎯 人脸跟踪配置")
    # print("=" * 40)
    # print("说明：")
    # print("• 唤醒后的人脸识别：必须开启（核心功能）")
    # print("• 对话时的人脸跟踪：可选择开启/关闭")
    # print("")
    # print("对话时人脸跟踪的作用：")
    # print("✅ 开启：机械臂会持续跟随您的脸部，保持\"注视\"")
    # print("❌ 关闭：机械臂保持静止，但仍能正常对话")
    # print("")
    return False
    while True:
        choice = input("是否启用对话时的人脸跟踪？(y/n，默认y): ").strip().lower()
        
        if choice == '' or choice == 'y' or choice == 'yes':
            print("✅ 已启用对话时人脸跟踪")
            return True
        elif choice == 'n' or choice == 'no':
            print("⚠️ 已禁用对话时人脸跟踪")
            return False
        else:
            print("❌ 请输入 y/n")

def start_super_agent(enable_conversation_tracking=True):
    """启动超级智能体 - 语音唤醒模式 (base环境)"""
    print("🤖 启动超级智能体 - 语音唤醒模式 (base环境)...")
    
    # 确保在base环境中运行
    base_env_python = "/home/xuanwu/miniconda3/bin/python"
    agent_script = "/home/xuanwu/haven_ws/src/super_intelligent_agent.py"
    
    try:
        # 导入智能体配置类
        sys.path.append('/home/xuanwu/haven_ws/src')
        from super_intelligent_agent import create_default_config
        
        # 创建配置并设置跟踪选项
        config = create_default_config()
        config.enable_conversation_tracking = enable_conversation_tracking
        
        # 将配置传递给超级智能体（需要修改调用方式）
        print(f"执行命令: {base_env_python} {agent_script}")
        print("ℹ️ 系统将进入语音唤醒监听模式")
        print("💬 请说 '小助小助' 来唤醒智能体")
        if enable_conversation_tracking:
            print("👁️ 对话时人脸跟踪：已启用")
        else:
            print("⚠️ 对话时人脸跟踪：已禁用")
        print("🛑 按 Ctrl+C 可以安全关闭整个系统")
        
        # 设置环境变量传递配置
        env = os.environ.copy()
        env['CONVERSATION_TRACKING'] = str(enable_conversation_tracking)
        
        os.chdir("/home/xuanwu/haven_ws/src")
        # 使用环境变量方式传递配置
        result = subprocess.run([base_env_python, agent_script], env=env)
        
    except Exception as e:
        print(f"❌ 启动超级智能体失败: {e}")
    finally:
        # 超级智能体退出时，清理资源
        cleanup_and_exit()

def main():
    """主启动流程"""
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🚀 超级智能体完整系统启动")
    print("=" * 60)
    
    print("\n📋 系统架构说明:")
    print("• 面部识别服务: 运行在face环境，提供HTTP API")
    print("• 超级智能体: 运行在base环境，语音唤醒 + 面部识别 + 对话")
    print("• 记忆系统: 运行在base环境，处理对话和记忆")
    print("• 语音唤醒: 监听'小助小助'关键词，触发完整交互流程")
    
    print("\n🔄 交互流程:")
    print("1. 语音唤醒监听")
    print("2. 检测到'小助小助' → 播放招呼语音")
    print("3. 面部识别 → 直接扫描/搜索模式")
    print("4. 个性化问候: '您好[用户名]，有什么可以帮到您？'")
    print("5. 智能对话 → 记忆存储")
    print("6. 返回语音监听")
    
    print("\n🔧 启动步骤:")
    
    # 步骤1: 检查或启动face服务
    print("1. 检查面部识别服务状态...")
    if check_face_service():
        print("✅ 面部识别服务已在运行")
    else:
        print("⚠️ 面部识别服务未运行，正在启动...")
        if not start_face_service():
            print("❌ 无法启动面部识别服务，程序退出")
            return
    
    # 步骤2: 启动超级智能体
    print("\n2. 配置人脸跟踪...")
    enable_conversation_tracking = get_face_tracking_config()
    
    print("\n3. 启动超级智能体...")
    print("💡 提示: 按 Ctrl+C 可以安全关闭整个系统")
    start_super_agent(enable_conversation_tracking)

def test_system():
    """测试系统连接"""
    print("🧪 测试系统连接...")
    
    # 测试面部识别服务
    if check_face_service():
        print("✅ 面部识别服务连接正常")
    else:
        print("❌ 面部识别服务连接失败")
        return False
    
    # 测试客户端连接
    try:
        sys.path.append('/home/xuanwu/haven_ws/src')
        from face_recognition_client import FaceRecognitionClient, FaceRecognitionConfig
        
        config = FaceRecognitionConfig()
        client = FaceRecognitionClient(config)
        
        if client.check_service_status():
            print("✅ 客户端连接正常")
            return True
        else:
            print("❌ 客户端连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 客户端测试失败: {e}")
        return False

def print_usage():
    """打印使用说明"""
    print("📖 使用说明:")
    print("-" * 40)
    print("1. 确保已安装所有依赖:")
    print("   • face环境: insightface, pyorbbecsdk, opencv-python")
    print("   • base环境: requests, flask, openai")
    print("")
    print("2. 确保硬件连接:")
    print("   • Orbbec相机已连接")
    print("   • 机械臂已连接并可控制")
    print("")
    print("3. 确保配置文件:")
    print("   • 面部数据库: /home/xuanwu/taskAgent/config/face_db.json")
    print("   • DeepSeek API密钥已配置")
    print("")
    print("4. 启动命令:")
    print("   python start_system.py")
    print("")
    print("5. 测试命令:")
    print("   python start_system.py test")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "test":
            test_system()
        elif command == "help":
            print_usage()
        elif command == "shutdown" or command == "stop":
            shutdown_system()
        else:
            print("❌ 未知命令")
            print("📖 可用命令:")
            print("  python start_system.py          # 启动系统")
            print("  python start_system.py test     # 测试连接")
            print("  python start_system.py help     # 显示帮助")
            print("  python start_system.py shutdown # 关闭系统")
    else:
        main()