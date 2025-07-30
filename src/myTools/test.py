# -*- coding: utf-8 -*-
# !/home/xuanwu/miniconda/envs/face/bin/python
import cv2
import numpy as np
import json
import os
import sys
import requests
import time

# 确保 insightface 和 pyorbbecsdk 可导入
try:
    from insightface.app import FaceAnalysis
    from pyorbbecsdk import *
except ImportError as e:
    print(f"[ERROR] 缺少必要的库: {e}")
    print("请确保您已在正确的 Python 环境中安装了 'insightface' 和 'pyorbbecsdk'。")
    sys.exit(1)

# 确保 orbbec sdk 的 utils 可用
# 请根据您的实际路径修改
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


# --- 全局常量和配置 ---
DB_PATH = "/home/xuanwu/taskAgent/config/face_db.json"
RECOGNITION_THRESHOLD = 0.4  # 识别阈值，越低越严格
ESC_KEY = 27
LEFT_THRESHOLD = 300  # 跟随判定的左边界
RIGHT_THRESHOLD = 340 # 跟随判定的右边界
FOLLOW_DELTA_ANGLE = 60   # 每次跟随转动的角度
TARGET_CAMERA_SN = "AY8V74300ED"  # 目标相机序列号


# --- 核心功能函数 ---

def cosine_distance(a, b):
    """计算两个向量的余弦距离"""
    a = np.asarray(a)
    b = np.asarray(b)
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_recognized_person(frame, face_analyzer, face_database, threshold):
    """
    在给定的图像帧中检测和识别人脸。

    Args:
        frame: 从相机获取的图像帧 (BGR格式)。
        face_analyzer: InsightFace 的 FaceAnalysis 实例。
        face_database: 从 JSON 文件加载的人脸数据库。
        threshold: 用于人脸识别的余弦距离阈值。

    Returns:
        tuple: (recognized_name, middle_point)
               - recognized_name (str): 识别出的用户名，如果未识别到则为 "Unknown"，
                                        如果没有检测到人脸则为 None。
               - middle_point (float): 检测到的最主要人脸的水平中心点像素坐标，
                                       如果没有检测到人脸则为 None。
    """
    faces = face_analyzer.get(frame)
    if not faces:
        return None, None  # 没有检测到人脸

    # 找到并处理画面中最大的人脸
    largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))

    emb = largest_face.normed_embedding
    bbox = largest_face.bbox.astype(int)
    middle_point = (bbox[0] + bbox[2]) / 2

    best_user = "Unknown"
    min_dist = float('inf')

    for user, vec in face_database.items():
        dist = cosine_distance(emb, vec)
        if dist < min_dist:
            min_dist = dist
            best_user = user

    if min_dist > threshold:
        best_user = "Unknown"

    return best_user, middle_point


# --- 机械臂控制函数 ---

def arm_init():
    """初始化机械臂，包括使能和归位。"""
    print("[INFO] 正在初始化机械臂...")
    try:
        requests.post(lumi_url.LUMI_RESET_URL, json={}, timeout=5)
        requests.post(lumi_url.LUMI_ENABLE_URL, json={"enable": 1}, timeout=5)
        return_home()
        print("[SUCCESS] 机械臂初始化完成！")
    except requests.RequestException as e:
        print(f"[ERROR] 机械臂初始化失败: {e}")
        sys.exit(1)

def get_current_angle():
    """获取机械臂当前的角度"""
    try:
        response = requests.get(lumi_url.LUMI_GETSTATE_URL, timeout=2)
        response.raise_for_status()
        return response.json()[2]["pos"]
    except requests.RequestException as e:
        print(f"[WARNING] 获取机械臂角度失败: {e}")
        return None

def return_home():
    """控制机械臂返回原点位置"""
    try:
        requests.post(
            lumi_url.LUMI_MOVETO_URL,
            json={"pos": [0.0, 0, 0, 0], "vel": 100, "acc": 100},
            timeout=5
        )
    except requests.RequestException as e:
        print(f"[WARNING] 机械臂归位失败: {e}")

def turnHead(angle):
    response = requests.post(
                    lumi_url.LUMI_MOVETO_URL,
                    json={"pos": [0.0, 0, angle, 0], "vel": 20, "acc": 20},
                )
    print(f"LUMI_STATUS_URL:{response.text}")

def follow_person(middle_pixel):
    """根据人脸中心点控制机械臂进行跟随"""
    if middle_pixel is None or not (LEFT_THRESHOLD <= middle_pixel <= RIGHT_THRESHOLD):
        angle = get_current_angle()
        if angle is None:
            return
        if middle_pixel is None:
            print("[INFO] 未检测到人脸，机械臂返回原点。")
            return_home()
            return
        # new_angle = angle
        if middle_pixel < LEFT_THRESHOLD:
            # print(f"初步进入向左移函数,angle:{angle}")
            if -180 <= angle <= 180 - FOLLOW_DELTA_ANGLE:
                print(f"middle_pixel{middle_pixel}向左移动")
                angle += FOLLOW_DELTA_ANGLE
                turnHead(angle)
                # response = requests.post(
                #     lumi_url.LUMI_MOVETO_URL,
                #     json={"pos": [0.0, 0, angle, 0], "vel": 20, "acc": 20},
                # )
                # print(f"LUMI_STATUS_URL:{response.text}")
            
            if angle < 180 - FOLLOW_DELTA_ANGLE:
                turnHead(180)
            elif angle == 180:
                return_home()
            # else:
            #     break
        # while middle_pixel > right_threshold:
        elif middle_pixel > RIGHT_THRESHOLD:
            # print(f"初步进入向右移函数,angle:{angle}")
            if 180 >= angle >= -180 + FOLLOW_DELTA_ANGLE:
                print(f"middle_pixel{middle_pixel}向右移动")
                angle -= FOLLOW_DELTA_ANGLE
                response = requests.post(
                    lumi_url.LUMI_MOVETO_URL,
                    json={"pos": [0.0, 0, angle - 5, 0], "vel": 20, "acc": 20},
                )
                print(f"LUMI_STATUS_URL:{response.text}")
            if angle < -180 + FOLLOW_DELTA_ANGLE:
                return_home()
    else:
        print(f"[INFO] 人脸位于中间区域 (pos: {middle_pixel:.0f})，机械臂保持不动。")


# --- 主程序 ---

def main():
    # 1. 初始化机械臂
    arm_init()

    # 2. 加载人脸数据库
    print("[INFO] 正在加载人脸数据库...")
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] 数据库文件不存在：{DB_PATH}")
        sys.exit(1)
    with open(DB_PATH, 'r') as f:
        face_db = json.load(f)
    print("[SUCCESS] 人脸数据库加载完成。")

    # 3. 初始化 InsightFace 模型
    print("[INFO] 正在初始化 InsightFace 模型...")
    app = FaceAnalysis(name='buffalo_l', allowed_modules=['detection', 'recognition'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("[SUCCESS] InsightFace 模型初始化完成。")

    # 4. 初始化 Orbbec 相机
    print("[INFO] 正在初始化 Orbbec 相机...")
    pipeline = None
    try:
        context = Context()
        device_list = context.query_devices()
        if device_list.get_count() == 0:
            print("[ERROR] 未找到任何 Orbbec 相机。")
            sys.exit(1)
        selected_device = device_list.get_device_by_serial_number(TARGET_CAMERA_SN)
        pipeline = Pipeline(selected_device)
        config = Config()
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        color_profile = profile_list.get_video_stream_profile(640, 0, OBFormat.RGB, 30)
        config.enable_stream(color_profile)
        pipeline.start(config)
        print(f"[SUCCESS] Orbbec 相机 (SN: {TARGET_CAMERA_SN}) 已打开") # 按 'q' 或 ESC 退出
    except OBError as e:
        print(f"[ERROR] 初始化 Orbbec 相机失败: {e}")
        if pipeline:
            pipeline.stop()
        sys.exit(1)

    # 5. 主循环
    try:
        while True:
            frames = pipeline.wait_for_frames(100)
            if frames is None:
                continue
            color_frame = frames.get_color_frame()
            if color_frame is None:
                continue

            frame = frame_to_bgr_image(color_frame)
            if frame is None:
                print("[WARNING] 无法转换图像帧")
                continue

            # 调用新函数来获取识别结果
            recognized_name, middle_pixel = get_recognized_person(frame, app, face_db, RECOGNITION_THRESHOLD)
            
            if recognized_name:
                 print(f"[RESULT] 识别到的人物: {recognized_name}")

            # 根据识别结果控制机械臂
            follow_person(middle_pixel)
            
            # 按 'q' 或 ESC 退出循环
            # 注意：由于没有显示cv2窗口，此退出方式无效。程序将通过 Ctrl+C 退出。
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord('q') or key == ESC_KEY:
            #     break
            
            time.sleep(0.1) # 短暂延时，避免过于频繁地发送请求

    except KeyboardInterrupt:
        print("\n[INFO] 检测到 Ctrl+C 中断。")
    finally:
        # 6. 清理资源
        print("[INFO] 正在关闭程序...")
        if pipeline:
            pipeline.stop()
        print("[SUCCESS] 程序已退出。")


if __name__ == "__main__":
    main()
