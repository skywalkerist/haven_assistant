#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部识别服务 - 运行在face环境中，提供REST API接口
"""

import sys
import os
import json
import time
import threading
from typing import Optional, Tuple, Dict
from flask import Flask, jsonify, request
from dataclasses import asdict

# 确保在face环境中运行
sys.path.append('/home/xuanwu/haven_ws/src/myTools')
from recognize_oop import FaceRecognitionSystem, RecognitionConfig

class FaceRecognitionService:
    """
    面部识别服务类 - 提供HTTP API接口
    """
    
    def __init__(self, port: int = 5001):
        self.app = Flask(__name__)
        self.port = port
        self.face_system = None
        self.is_running = False
        self.current_recognition = {"name": None, "position": None, "timestamp": 0}
        self.recognition_thread = None
        
        # 设置API路由
        self._setup_routes()
        
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取服务状态"""
            return jsonify({
                "status": "running" if self.is_running else "stopped",
                "face_system_initialized": self.face_system is not None,
                "current_recognition": self.current_recognition
            })
        
        @self.app.route('/api/initialize', methods=['POST'])
        def initialize_system():
            """初始化面部识别系统"""
            try:
                print("🔧 开始初始化面部识别系统...")
                config_data = request.get_json() or {}
                
                # 创建配置
                config = RecognitionConfig(
                    recognition_threshold=config_data.get('recognition_threshold', 0.6),
                    left_threshold=config_data.get('left_threshold', 300),
                    right_threshold=config_data.get('right_threshold', 340),
                    follow_delta_angle=config_data.get('follow_delta_angle', 15)
                )
                
                print("📋 配置创建完成")
                print(f"   识别阈值: {config.recognition_threshold}")
                print(f"   跟随角度: {config.follow_delta_angle}")
                
                # 初始化系统
                print("🤖 创建面部识别系统实例...")
                self.face_system = FaceRecognitionSystem(config)
                
                print("🔧 执行系统初始化...")
                success = self.face_system.initialize()
                
                if success:
                    print("✅ 面部识别系统初始化成功")
                    return jsonify({
                        "success": True,
                        "message": "系统初始化成功"
                    })
                else:
                    print("❌ 面部识别系统初始化失败")
                    return jsonify({
                        "success": False,
                        "message": "系统初始化失败"
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
                if not self.face_system:
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
                    target=self._recognition_loop, 
                    daemon=True
                )
                self.recognition_thread.start()
                
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
            """控制机械臂转头"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "success": False,
                        "message": "请求数据为空"
                    }), 400
                
                angle = data.get('angle', 0)
                
                if not self.face_system:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                print(f"[INFO] 收到转头请求: {angle}°")
                
                # 调用系统的转头方法
                success = self.face_system.turn_head(angle)
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": f"转头到角度 {angle}° 成功"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": f"转头到角度 {angle}° 失败"
                    })
                
            except Exception as e:
                print(f"[ERROR] 转头接口错误: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    "success": False,
                    "message": f"转头错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/return_home', methods=['POST'])
        def return_home():
            """机械臂返回原点"""
            try:
                if not self.face_system:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                success = self.face_system.return_home()
                return jsonify({
                    "success": success,
                    "message": "返回原点成功" if success else "返回原点失败"
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"返回原点错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/capture_photo', methods=['POST'])
        def capture_photo():
            """截取当前画面照片"""
            try:
                data = request.get_json()
                photo_path = data.get('photo_path')
                
                if not photo_path:
                    return jsonify({
                        "success": False,
                        "message": "缺少photo_path参数"
                    }), 400
                
                if not self.face_system:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                # 获取当前帧
                frames = self.face_system.pipeline.wait_for_frames(100)
                if frames is None:
                    return jsonify({
                        "success": False,
                        "message": "无法获取相机画面"
                    })
                
                color_frame = frames.get_color_frame()
                if color_frame is None:
                    return jsonify({
                        "success": False,
                        "message": "无法获取彩色画面"
                    })
                
                # 导入frame转换函数
                sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
                from utils import frame_to_bgr_image
                import cv2
                
                frame = frame_to_bgr_image(color_frame)
                if frame is None:
                    return jsonify({
                        "success": False,
                        "message": "画面转换失败"
                    })
                
                # 确保目录存在
                import os
                os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                
                # 保存图片
                success = cv2.imwrite(photo_path, frame)
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": f"照片已保存到 {photo_path}"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "保存照片失败"
                    })
                    
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"截图错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/recognize_photo', methods=['POST'])
        def recognize_photo():
            """识别指定照片中的人脸"""
            try:
                data = request.get_json()
                photo_path = data.get('photo_path')
                
                if not photo_path:
                    return jsonify({
                        "success": False,
                        "message": "缺少photo_path参数"
                    }), 400
                
                if not self.face_system:
                    return jsonify({
                        "success": False,
                        "message": "面部识别系统未初始化"
                    }), 400
                
                # 检查文件是否存在
                import os
                if not os.path.exists(photo_path):
                    return jsonify({
                        "success": False,
                        "message": f"照片文件不存在: {photo_path}"
                    })
                
                # 读取图片
                import cv2
                frame = cv2.imread(photo_path)
                if frame is None:
                    return jsonify({
                        "success": False,
                        "message": "无法读取照片文件"
                    })
                
                # 识别人脸
                recognized_name, middle_pixel = self.face_system.recognize_person(frame)
                
                if recognized_name and recognized_name != "Unknown":
                    # 获取真实的识别置信度
                    try:
                        # 重新进行识别以获取置信度
                        faces = self.face_system.face_analyzer.get(frame)
                        if faces:
                            largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))
                            emb = largest_face.normed_embedding.astype('float32')
                            
                            # 计算与数据库中最匹配用户的距离
                            if len(self.face_system.db_users) > 0:
                                distances = self.face_system._batch_cosine_distance(emb, self.face_system.db_vectors_normalized)
                                min_dist = float(distances.min())
                                confidence = max(0.0, 1.0 - min_dist)  # 距离越小置信度越高
                            else:
                                confidence = 0.0
                        else:
                            confidence = 0.0
                    except Exception as e:
                        print(f"[WARNING] 获取置信度失败: {e}")
                        confidence = 0.8  # 降级使用默认值
                    
                    return jsonify({
                        "success": True,
                        "name": recognized_name,
                        "confidence": confidence,
                        "message": f"识别到: {recognized_name} (置信度: {confidence:.2f})"
                    })
                else:
                    return jsonify({
                        "success": True,
                        "name": "Unknown",
                        "confidence": 0.0,
                        "message": "未识别到已知用户"
                    })
                    
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"识别错误: {str(e)}"
                }), 500
        
        @self.app.route('/api/shutdown', methods=['POST'])
        def shutdown():
            """关闭服务"""
            self.is_running = False
            if self.face_system:
                self.face_system.cleanup()
            
            # 在单独线程中关闭Flask服务器
            def shutdown_server():
                time.sleep(1)  # 给响应一点时间
                print("🛑 正在关闭面部识别服务...")
                os._exit(0)  # 强制退出进程
            
            import threading
            threading.Thread(target=shutdown_server, daemon=True).start()
            
            return jsonify({
                "success": True,
                "message": "服务即将关闭"
            })
    
    def _recognition_loop(self):
        """面部识别循环"""
        print("🔄 面部识别循环开始")
        
        try:
            while self.is_running and self.face_system:
                frames = self.face_system.pipeline.wait_for_frames(100)
                if frames is None:
                    time.sleep(0.1)
                    continue
                
                color_frame = frames.get_color_frame()
                if color_frame is None:
                    time.sleep(0.1)
                    continue
                
                # 导入frame转换函数
                sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
                from utils import frame_to_bgr_image
                
                frame = frame_to_bgr_image(color_frame)
                if frame is None:
                    continue
                
                # 执行人脸识别
                recognized_name, middle_pixel = self.face_system.recognize_person(frame)
                
                # 更新识别结果
                self.current_recognition = {
                    "name": recognized_name,
                    "position": middle_pixel,
                    "timestamp": time.time()
                }
                
                time.sleep(0.1)  # 控制识别频率
                
        except Exception as e:
            print(f"❌ 面部识别循环错误: {e}")
        finally:
            print("🔄 面部识别循环结束")
    
    def run(self, debug: bool = False):
        """启动服务"""
        print(f"🚀 面部识别服务启动，端口: {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug, threaded=True)

def main():
    """主函数"""
    print("🤖 启动面部识别服务 (face环境)")
    
    service = FaceRecognitionService(port=5001)
    
    try:
        service.run(debug=False)
    except KeyboardInterrupt:
        print("\n🛑 服务被用户中断")
    except Exception as e:
        print(f"❌ 服务错误: {e}")
    finally:
        print("👋 面部识别服务已关闭")

if __name__ == "__main__":
    main()