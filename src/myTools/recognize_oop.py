# -*- coding: utf-8 -*-
# !/home/xuanwu/miniconda/envs/face/bin/python
import cv2
import numpy as np
import json
import os
import sys
import requests
import time
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass

# 确保 insightface 和 pyorbbecsdk 可导入
try:
    from insightface.app import FaceAnalysis
    from pyorbbecsdk import *
except ImportError as e:
    print(f"[ERROR] 缺少必要的库: {e}")
    print("请确保您已在正确的 Python 环境中安装了 'insightface' 和 'pyorbbecsdk'。")
    sys.exit(1)

# 确保 orbbec sdk 的 utils 可用
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
try:
    from utils import frame_to_bgr_image
except ImportError:
    print("\n[ERROR] 无法从指定路径导入 'frame_to_bgr_image'。")
    print("请确认 '/home/xuanwu/pyorbbecsdk/examples' 路径是否正确。")
    sys.exit(1)

# 确保 lumi_url 模块可用
try:
    import lumi_url
except ImportError:
    print("\n[ERROR] 无法导入 'lumi_url.py' 模块。")
    print("请确保 'lumi_url.py' 文件与此脚本位于同一目录下。")
    sys.exit(1)


@dataclass
class RecognitionConfig:
    """人脸识别系统配置类"""
    db_path: str = "/home/xuanwu/haven_ws/src/resources/face_db.json"
    recognition_threshold: float = 0.4
    left_threshold: int = 300
    right_threshold: int = 340
    follow_delta_angle: int = 15
    target_camera_sn: str = "AY8V74300ED"
    det_size: Tuple[int, int] = (320, 320)
    esc_key: int = 27


class FaceRecognitionSystem:
    """面向对象的人脸识别跟随系统"""
    
    def __init__(self, config: Optional[RecognitionConfig] = None):
        """
        初始化人脸识别系统
        
        Args:
            config: 系统配置，如果为None则使用默认配置
        """
        self.config = config or RecognitionConfig()
        self.face_analyzer = None
        self.pipeline = None
        self.face_db = {}
        self.db_users = []
        self.db_vectors_normalized = None
        self.current_angle = 0
        self.is_running = False
        
    def _batch_cosine_distance(self, query_emb: np.ndarray, db_vectors_norm: np.ndarray) -> np.ndarray:
        """
        批量计算余弦距离，使用numpy广播优化性能
        
        Args:
            query_emb: 查询向量
            db_vectors_norm: 预归一化的数据库向量
            
        Returns:
            余弦距离数组
        """
        query_emb = np.asarray(query_emb, dtype=np.float32)
        query_norm = np.linalg.norm(query_emb)
        
        if query_norm == 0:
            return np.ones(len(db_vectors_norm))
            
        query_normalized = query_emb / query_norm
        cosine_similarities = np.dot(db_vectors_norm, query_normalized)
        cosine_distances = 1 - cosine_similarities
        
        return cosine_distances
    
    def load_face_database(self) -> bool:
        """
        加载人脸数据库
        
        Returns:
            加载是否成功
        """
        try:
            if not os.path.exists(self.config.db_path):
                print(f"[ERROR] 数据库文件不存在：{self.config.db_path}")
                return False
                
            with open(self.config.db_path, 'r') as f:
                self.face_db = json.load(f)
            
            # 预处理人脸数据库
            self.db_users = list(self.face_db.keys())
            if self.db_users:
                db_vectors = np.array(list(self.face_db.values()), dtype=np.float32)
                db_norms = np.linalg.norm(db_vectors, axis=1, keepdims=True)
                self.db_vectors_normalized = db_vectors / db_norms
                
            print(f"[INFO] 加载了 {len(self.db_users)} 个用户的人脸数据")
            return True
            
        except Exception as e:
            print(f"[ERROR] 加载人脸数据库失败: {e}")
            return False
    
    def initialize_face_analyzer(self) -> bool:
        """
        初始化InsightFace模型
        
        Returns:
            初始化是否成功
        """
        try:
            print("[INFO] 正在初始化 InsightFace 模型...")
            self.face_analyzer = FaceAnalysis(name='buffalo_l', allowed_modules=['detection', 'recognition'])
            self.face_analyzer.prepare(ctx_id=0, det_size=self.config.det_size)
            print("[SUCCESS] InsightFace 模型初始化完成。")
            return True
            
        except Exception as e:
            print(f"[ERROR] InsightFace 模型初始化失败: {e}")
            return False
    
    def initialize_camera(self) -> bool:
        """
        初始化Orbbec相机
        
        Returns:
            初始化是否成功
        """
        try:
            print("[INFO] 正在初始化 Orbbec 相机...")
            context = Context()
            device_list = context.query_devices()
            
            if device_list.get_count() == 0:
                print("[ERROR] 未找到任何 Orbbec 相机。")
                return False
                
            selected_device = device_list.get_device_by_serial_number(self.config.target_camera_sn)
            self.pipeline = Pipeline(selected_device)
            
            config = Config()
            profile_list = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
            color_profile = profile_list.get_video_stream_profile(640, 0, OBFormat.RGB, 30)
            config.enable_stream(color_profile)
            self.pipeline.start(config)
            
            print(f"[SUCCESS] Orbbec 相机 (SN: {self.config.target_camera_sn}) 已打开")
            return True
            
        except Exception as e:
            print(f"[ERROR] 初始化 Orbbec 相机失败: {e}")
            return False
    
    def recognize_person(self, frame: np.ndarray) -> Tuple[Optional[str], Optional[float]]:
        """
        在给定的图像帧中检测和识别人脸
        
        Args:
            frame: 图像帧
            
        Returns:
            (识别出的用户名, 人脸中心点x坐标)
        """
        if self.face_analyzer is None:
            return None, None
            
        faces = self.face_analyzer.get(frame)
        if not faces:
            return None, None
        
        # 找到最大的人脸
        largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))
        
        emb = largest_face.normed_embedding.astype(np.float32)
        bbox = largest_face.bbox.astype(int)
        middle_point = (bbox[0] + bbox[2]) / 2
        
        # 批量计算距离
        if len(self.db_users) > 0:
            distances = self._batch_cosine_distance(emb, self.db_vectors_normalized)
            best_idx = np.argmin(distances)
            min_dist = distances[best_idx]
            best_user = self.db_users[best_idx]
        else:
            best_user = "Unknown"
            min_dist = float('inf')
        
        if min_dist > self.config.recognition_threshold:
            best_user = "Unknown"
        
        return best_user, middle_point
    
    def get_current_angle(self) -> Optional[float]:
        """获取机械臂当前角度"""
        try:
            response = requests.get(lumi_url.LUMI_GETSTATE_URL, timeout=2)
            response.raise_for_status()
            angle = response.json()[2]["pos"]
            self.current_angle = angle
            return angle
        except requests.RequestException as e:
            print(f"[WARNING] 获取机械臂角度失败: {e}")
            return None
    
    def turn_head(self, angle: float) -> bool:
        """
        控制机械臂转头到指定角度
        
        Args:
            angle: 目标角度
            
        Returns:
            操作是否成功
        """
        
        response = requests.post(
            lumi_url.LUMI_MOVETO_URL,
            json={"pos": [0.0, 0, angle, 0], "vel": 100, "acc": 50},
            timeout=5
        )
        print(f"转头到角度 {angle}: {response.text}")
        self.current_angle = angle
        return True
    
    
    def return_home(self) -> bool:
        """机械臂返回原点"""
        try:
            requests.post(
                lumi_url.LUMI_MOVETO_URL,
                json={"pos": [0.0, 0, 0, 0], "vel": 100, "acc": 100},
                timeout=5
            )
            self.current_angle = 0
            print("[INFO] 机械臂已返回原点")
            return True
        except requests.RequestException as e:
            print(f"[WARNING] 机械臂归位失败: {e}")
            return False
    
    def follow_person(self, middle_pixel: Optional[float], recognized_name: str) -> None:
        """
        根据人脸位置控制机械臂跟随（修复了角度跳转问题）
        
        Args:
            middle_pixel: 人脸中心点x坐标
            recognized_name: 识别出的用户名
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
        
        # 获取当前角度
        current_angle = self.get_current_angle()
        if current_angle is None:
            return
        
        # 计算新角度（修复逻辑）
        if middle_pixel < self.config.left_threshold:
            # 向左转
            new_angle = current_angle + self.config.follow_delta_angle
            # 限制角度范围
            if new_angle <= 180:
                print(f"middle_pixel {middle_pixel} 向左移动: {current_angle} -> {new_angle}")
                self.turn_head(new_angle)
            else:
                print(f"已达到左转极限，保持在180度")
                self.turn_head(180)
                
        elif middle_pixel > self.config.right_threshold:
            # 向右转
            new_angle = current_angle - self.config.follow_delta_angle
            # 限制角度范围
            if new_angle >= -180:
                print(f"middle_pixel {middle_pixel} 向右移动: {current_angle} -> {new_angle}")
                self.turn_head(new_angle)
            else:
                print(f"已达到右转极限，保持在-180度")
                self.turn_head(-180)
    
    def draw_visualization(self, frame: np.ndarray, recognized_name: Optional[str], 
                          middle_pixel: Optional[float]) -> np.ndarray:
        """
        在帧上绘制可视化信息
        
        Args:
            frame: 输入帧
            recognized_name: 识别结果
            middle_pixel: 人脸中心点
            
        Returns:
            绘制后的帧
        """
        display_frame = frame.copy()
        
        if recognized_name:
            # 绘制人脸框和标签
            faces = self.face_analyzer.get(frame)
            if faces:
                largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))
                bbox = largest_face.bbox.astype(int)
                
                # 颜色选择
                color = (0, 255, 0) if recognized_name != "Unknown" else (0, 0, 255)
                
                # 绘制人脸框
                cv2.rectangle(display_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                
                # 显示识别结果
                cv2.putText(display_frame, recognized_name, (bbox[0], bbox[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
                # 显示中心点
                if middle_pixel is not None:
                    center_y = bbox[1] + (bbox[3] - bbox[1]) // 2
                    cv2.circle(display_frame, (int(middle_pixel), center_y), 5, (255, 255, 0), -1)
        else:
            cv2.putText(display_frame, "No face detected", (30, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 显示跟随区域线
        cv2.line(display_frame, (self.config.left_threshold, 0), 
                (self.config.left_threshold, display_frame.shape[0]), (255, 0, 0), 2)
        cv2.line(display_frame, (self.config.right_threshold, 0), 
                (self.config.right_threshold, display_frame.shape[0]), (255, 0, 0), 2)
        
        # 显示当前角度
        cv2.putText(display_frame, f"Angle: {self.current_angle:.1f}", (30, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return display_frame
    
    def initialize_arm(self) -> bool:
        """初始化机械臂"""
        try:
            print("[INFO] 正在初始化机械臂...")
            requests.post(lumi_url.LUMI_RESET_URL, json={}, timeout=5)
            requests.post(lumi_url.LUMI_ENABLE_URL, json={"enable": 1}, timeout=5)
            self.return_home()
            print("[SUCCESS] 机械臂初始化完成！")
            return True
        except requests.RequestException as e:
            print(f"[ERROR] 机械臂初始化失败: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        初始化整个系统
        
        Returns:
            初始化是否成功
        """
        # 初始化机械臂
        if not self.initialize_arm():
            return False
        
        # 加载人脸数据库
        if not self.load_face_database():
            return False
        
        # 初始化人脸分析器
        if not self.initialize_face_analyzer():
            return False
        
        # 初始化相机
        if not self.initialize_camera():
            return False
        
        return True
    
    def run(self, show_window: bool = True) -> None:
        """
        运行主循环
        
        Args:
            show_window: 是否显示窗口
        """
        if not self.initialize():
            print("[ERROR] 系统初始化失败")
            return
        
        self.is_running = True
        print("[INFO] 系统开始运行，按 'q' 或 ESC 退出")
        
        try:
            while self.is_running:
                frames = self.pipeline.wait_for_frames(100)
                if frames is None:
                    continue
                    
                color_frame = frames.get_color_frame()
                if color_frame is None:
                    continue
                
                frame = frame_to_bgr_image(color_frame)
                if frame is None:
                    print("[WARNING] 无法转换图像帧")
                    continue
                
                # 人脸识别
                recognized_name, middle_pixel = self.recognize_person(frame)
                
                if recognized_name:
                    print(f"[RESULT] 识别到的人物: {recognized_name}")
                
                # 机械臂跟随
                self.follow_person(middle_pixel, recognized_name)
                
                # 可视化
                if show_window:
                    display_frame = self.draw_visualization(frame, recognized_name, middle_pixel)
                    cv2.imshow("Face Recognition System", display_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == self.config.esc_key:
                        break
                
                time.sleep(0.05)  # 短暂延时
                
        except KeyboardInterrupt:
            print("\n[INFO] 检测到 Ctrl+C 中断")
        finally:
            self.cleanup()
    
    def stop(self) -> None:
        """停止系统运行"""
        self.is_running = False
    
    def cleanup(self) -> None:
        """清理资源"""
        print("[INFO] 正在关闭系统...")
        
        if self.pipeline:
            self.pipeline.stop()
        
        cv2.destroyAllWindows()
        print("[SUCCESS] 系统已关闭")


def main():
    """主函数示例"""
    # 创建配置
    config = RecognitionConfig(
        recognition_threshold=0.6,
        follow_delta_angle=15,
        left_threshold=300,
        right_threshold=340
    )
    
    # 创建系统实例
    system = FaceRecognitionSystem(config)
    
    # 运行系统
    system.run(show_window=True)


if __name__ == "__main__":
    main()