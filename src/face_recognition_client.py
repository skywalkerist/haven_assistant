#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部识别客户端 - 运行在base环境中，通过HTTP API调用face环境的服务
"""

import requests
import time
from typing import Optional, Tuple, Dict
from dataclasses import dataclass

@dataclass
class FaceRecognitionConfig:
    """面部识别客户端配置"""
    service_url: str = "http://localhost:5001"
    recognition_threshold: float = 0.4
    left_threshold: int = 300
    right_threshold: int = 340
    follow_delta_angle: int = 15
    request_timeout: int = 15  # 增加超时时间到15秒

class FaceRecognitionClient:
    """
    面部识别客户端 - 通过HTTP API与face环境中的服务通信
    """
    
    def __init__(self, config: FaceRecognitionConfig):
        self.config = config
        self.base_url = config.service_url
        self.is_initialized = False
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送HTTP请求"""
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=self.config.request_timeout)
            elif method.upper() == 'POST':
                response = requests.post(
                    url, 
                    json=data or {}, 
                    timeout=self.config.request_timeout
                )
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求失败 ({endpoint}): {e}")
            return {"success": False, "message": str(e)}
    
    def check_service_status(self) -> bool:
        """检查服务状态"""
        result = self._make_request('GET', 'status')
        return result.get('status') == 'running'
    
    def initialize(self) -> bool:
        """初始化面部识别系统"""
        print("🔧 正在初始化面部识别系统...")
        
        # 发送初始化请求
        config_data = {
            'recognition_threshold': self.config.recognition_threshold,
            'left_threshold': self.config.left_threshold,
            'right_threshold': self.config.right_threshold,
            'follow_delta_angle': self.config.follow_delta_angle
        }
        
        result = self._make_request('POST', 'initialize', config_data)
        
        if result.get('success'):
            self.is_initialized = True
            print("✅ 面部识别系统初始化成功")
            return True
        else:
            print(f"❌ 面部识别系统初始化失败: {result.get('message')}")
            return False
    
    def start_recognition(self) -> bool:
        """启动面部识别"""
        if not self.is_initialized:
            print("⚠️ 系统未初始化，无法启动识别")
            return False
        
        result = self._make_request('POST', 'start_recognition')
        
        if result.get('success'):
            print("🔍 面部识别已启动")
            return True
        else:
            print(f"❌ 启动面部识别失败: {result.get('message')}")
            return False
    
    def stop_recognition(self) -> bool:
        """停止面部识别"""
        result = self._make_request('POST', 'stop_recognition')
        
        if result.get('success'):
            print("⏹️ 面部识别已停止")
            return True
        else:
            print(f"❌ 停止面部识别失败: {result.get('message')}")
            return False
    
    def get_current_recognition(self) -> Tuple[Optional[str], Optional[float]]:
        """获取当前识别结果"""
        result = self._make_request('GET', 'get_recognition')
        
        if isinstance(result, dict):
            name = result.get('name')
            position = result.get('position')
            return name, position
        else:
            return None, None
    
    def recognize_person(self, frame=None) -> Tuple[Optional[str], Optional[float]]:
        """
        识别人脸 - 兼容原有接口
        注意：这个方法不使用frame参数，而是从服务获取最新的识别结果
        """
        return self.get_current_recognition()
    
    def turn_head(self, angle: float) -> bool:
        """控制机械臂转头"""
        result = self._make_request('POST', 'turn_head', {'angle': angle})
        
        if result.get('success'):
            return True
        else:
            print(f"❌ 转头失败: {result.get('message')}")
            return False
    
    def return_home(self) -> bool:
        """机械臂返回原点"""
        result = self._make_request('POST', 'return_home')
        
        if result.get('success'):
            return True
        else:
            print(f"❌ 返回原点失败: {result.get('message')}")
            return False
    
    def get_current_angle(self) -> Optional[float]:
        """获取机械臂当前角度 - 从服务状态获取"""
        status = self._make_request('GET', 'status')
        # 这里需要服务端添加角度信息，暂时返回None
        return None
    
    def follow_person(self, middle_pixel: Optional[float], recognized_name: str) -> None:
        """
        根据人脸位置控制机械臂跟随
        这个方法在客户端实现逻辑，调用远程的转头API
        """
        # 如果是未知人脸，不进行跟随
        if recognized_name == "Unknown":
            print("[INFO] 检测到未知人脸，不进行跟随")
            return
        
        # 如果没有检测到人脸，返回原点
        if middle_pixel is None:
            print("[INFO] 未检测到人脸，机械臂返回原点")
            self.return_home()
            return
        
        # 如果在跟随区域内，不需要移动
        if self.config.left_threshold <= middle_pixel <= self.config.right_threshold:
            print(f"[INFO] 人脸位于中间区域 (pos: {middle_pixel:.0f})，机械臂保持不动")
            return
        
        # 获取当前角度（这里简化处理，使用默认角度计算）
        current_angle = self.get_current_angle() or 0
        
        # 计算新角度
        if middle_pixel < self.config.left_threshold:
            # 向左转
            new_angle = current_angle + self.config.follow_delta_angle
            if new_angle <= 180:
                print(f"middle_pixel {middle_pixel} 向左移动: {current_angle} -> {new_angle}")
                self.turn_head(new_angle)
            else:
                print(f"已达到左转极限，保持在180度")
                self.turn_head(180)
                
        elif middle_pixel > self.config.right_threshold:
            # 向右转
            new_angle = current_angle - self.config.follow_delta_angle
            if new_angle >= -180:
                print(f"middle_pixel {middle_pixel} 向右移动: {current_angle} -> {new_angle}")
                self.turn_head(new_angle)
            else:
                print(f"已达到右转极限，保持在-180度")
                self.turn_head(-180)
    
    def capture_photo(self, photo_path: str) -> bool:
        """
        截取当前画面照片
        """
        result = self._make_request('POST', 'capture_photo', {'photo_path': photo_path})
        
        if result.get('success'):
            return True
        else:
            print(f"❌ 截图失败: {result.get('message')}")
            return False
    
    def recognize_photo(self, photo_path: str) -> Optional[Dict]:
        """
        识别指定照片中的人脸
        """
        result = self._make_request('POST', 'recognize_photo', {'photo_path': photo_path})
        
        if result.get('success'):
            return {
                'name': result.get('name'),
                'confidence': result.get('confidence', 0.0)
            }
        else:
            print(f"❌ 照片识别失败: {result.get('message')}")
            return None
    
    def cleanup(self) -> None:
        """清理资源"""
        print("🧹 清理面部识别客户端...")
        self.stop_recognition()
        
        # 发送关闭信号给服务端
        self._make_request('POST', 'shutdown')
        print("✅ 面部识别客户端清理完成")

def test_client():
    """测试客户端功能"""
    print("🧪 测试面部识别客户端")
    
    config = FaceRecognitionConfig()
    client = FaceRecognitionClient(config)
    
    # 检查服务状态
    if not client.check_service_status():
        print("❌ 面部识别服务未运行，请先启动 face_recognition_service.py")
        return
    
    # 初始化
    if not client.initialize():
        print("❌ 初始化失败")
        return
    
    # 启动识别
    if not client.start_recognition():
        print("❌ 启动识别失败")
        return
    
    # 测试识别功能
    print("🔍 开始测试识别功能...")
    for i in range(5):
        name, position = client.get_current_recognition()
        print(f"识别结果 {i+1}: 姓名={name}, 位置={position}")
        time.sleep(1)
    
    # 清理
    client.cleanup()
    print("✅ 测试完成")

if __name__ == "__main__":
    test_client()