#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部识别服务 - 模拟版本，用于测试系统集成
不需要实际硬件，使用模拟数据
"""

import time
import threading
import random
from typing import Optional, Tuple, Dict
from flask import Flask, jsonify, request

class MockFaceRecognitionService:
    """
    模拟面部识别服务类 - 用于测试
    """
    
    def __init__(self, port: int = 5001):
        self.app = Flask(__name__)
        self.port = port
        self.is_initialized = False
        self.is_running = False
        self.current_recognition = {"name": None, "position": None, "timestamp": 0}
        self.recognition_thread = None
        self.current_angle = 0.0
        
        # 模拟用户数据库
        self.mock_users = ["陆李昕", "张三", "李四", "王五"]
        
        # 设置API路由
        self._setup_routes()
        
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取服务状态"""
            return jsonify({
                "status": "running" if self.is_running else "stopped",
                "face_system_initialized": self.is_initialized,
                "current_recognition": self.current_recognition,
                "current_angle": self.current_angle
            })
        
        @self.app.route('/api/initialize', methods=['POST'])
        def initialize_system():
            """初始化面部识别系统"""
            try:
                print("🔧 开始初始化模拟面部识别系统...")
                config_data = request.get_json() or {}
                
                print("📋 配置解析完成")
                print(f"   识别阈值: {config_data.get('recognition_threshold', 0.4)}")
                print(f"   跟随角度: {config_data.get('follow_delta_angle', 15)}")
                
                # 模拟初始化延迟
                print("🤖 模拟硬件初始化...")
                time.sleep(2)  # 模拟硬件初始化时间
                
                self.is_initialized = True
                print("✅ 模拟面部识别系统初始化成功")
                
                return jsonify({
                    "success": True,
                    "message": "模拟系统初始化成功"
                })
                
            except Exception as e:
                error_msg = f"初始化错误: {str(e)}"
                print(f"❌ {error_msg}")
                return jsonify({
                    "success": False,
                    "message": error_msg
                }), 500
        
        @self.app.route('/api/start_recognition', methods=['POST'])
        def start_recognition():
            """启动面部识别"""
            try:
                if not self.is_initialized:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                if self.is_running:
                    return jsonify({
                        "success": True,
                        "message": "面部识别已在运行"
                    })
                
                self.is_running = True
                self.recognition_thread = threading.Thread(
                    target=self._mock_recognition_loop, 
                    daemon=True
                )
                self.recognition_thread.start()
                
                print("🔍 模拟面部识别已启动")
                
                return jsonify({
                    "success": True,
                    "message": "面部识别已启动"
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"启动错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/stop_recognition', methods=['POST'])
        def stop_recognition():
            """停止面部识别"""
            self.is_running = False
            print("⏹️ 模拟面部识别已停止")
            return jsonify({
                "success": True,
                "message": "面部识别已停止"
            })
        
        @self.app.route('/api/get_recognition', methods=['GET'])
        def get_current_recognition():
            """获取当前识别结果"""
            return jsonify(self.current_recognition)
        
        @self.app.route('/api/turn_head', methods=['POST'])
        def turn_head():
            """控制机械臂转头 - 模拟"""
            try:
                data = request.get_json()
                angle = data.get('angle', 0)
                
                if not self.is_initialized:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                # 模拟转头
                self.current_angle = angle
                print(f"🔄 模拟转头到角度: {angle}°")
                
                return jsonify({
                    "success": True,
                    "message": f"转头到角度 {angle}"
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"转头错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/return_home', methods=['POST'])
        def return_home():
            """机械臂返回原点 - 模拟"""
            try:
                if not self.is_initialized:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                self.current_angle = 0.0
                print("🏠 模拟机械臂返回原点")
                
                return jsonify({
                    "success": True,
                    "message": "返回原点成功"
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"返回原点错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/shutdown', methods=['POST'])
        def shutdown():
            """关闭服务"""
            self.is_running = False
            print("🛑 模拟服务即将关闭")
            
            return jsonify({
                "success": True,
                "message": "服务即将关闭"
            })
    
    def _mock_recognition_loop(self):
        """模拟面部识别循环"""
        print("🔄 模拟面部识别循环开始")
        
        try:
            cycle = 0
            while self.is_running:
                cycle += 1
                
                # 模拟识别结果
                if cycle % 10 == 0:  # 每10次循环识别一次用户
                    # 随机选择一个用户或返回Unknown
                    if random.random() > 0.3:  # 70%概率识别到用户
                        recognized_name = random.choice(self.mock_users)
                        position = random.uniform(200, 500)  # 随机位置
                    else:
                        recognized_name = "Unknown"
                        position = None
                else:
                    recognized_name = None
                    position = None
                
                # 更新识别结果
                self.current_recognition = {
                    "name": recognized_name,
                    "position": position,
                    "timestamp": time.time()
                }
                
                if recognized_name and recognized_name != "Unknown":
                    print(f"👤 模拟识别到用户: {recognized_name} (位置: {position:.1f})")
                
                time.sleep(0.5)  # 控制识别频率
                
        except Exception as e:
            print(f"❌ 模拟面部识别循环错误: {e}")
        finally:
            print("🔄 模拟面部识别循环结束")
    
    def run(self, debug: bool = False):
        """启动服务"""
        print(f"🚀 模拟面部识别服务启动，端口: {self.port}")
        print("ℹ️ 这是模拟版本，不需要实际硬件")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug, threaded=True)

def main():
    """主函数"""
    print("🤖 启动模拟面部识别服务")
    print("=" * 50)
    print("📋 模拟功能说明:")
    print("• 不需要实际相机和机械臂硬件")
    print("• 随机生成识别结果进行测试")
    print("• 支持完整的API接口")
    print("• 适用于系统集成测试")
    print("=" * 50)
    
    service = MockFaceRecognitionService(port=5001)
    
    try:
        service.run(debug=False)
    except KeyboardInterrupt:
        print("\n🛑 服务被用户中断")
    except Exception as e:
        print(f"❌ 服务错误: {e}")
    finally:
        print("👋 模拟面部识别服务已关闭")

if __name__ == "__main__":
    main()