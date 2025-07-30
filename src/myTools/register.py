# -*- coding: utf-8 -*-
#!/home/xuanwu/miniconda/envs/face/bin/python
import cv2
import numpy as np
import json
import os
from insightface.app import FaceAnalysis
from typing import List, Optional
import sys
import time

sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
from pyorbbecsdk import *
from utils import frame_to_bgr_image

DB_PATH = "/home/xuanwu/haven_ws/src/resources/face_db.json"
# 优化：降低检测分辨率到320x320
app = FaceAnalysis(name='buffalo_l', allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=-1, det_size=(320, 320))  # ctx_id=0 使用GPU，-1 使用CPU

images_num = 0

# def pad_to_square(img):
#     """将图像填充为正方形"""
#     h, w = img.shape[:2]
#     size = max(h, w)
#     padded_img = np.zeros((size, size, 3), dtype=img.dtype)
#     padded_img[0:h, 0:w] = img
#     return padded_img


def write_json(data: dict, file_path: str):
    """将数据写入JSON文件（格式化）"""
    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write('\n')


def select_capture_mode() -> str:
    """选择采集模式"""
    print("\n请选择采集模式:")
    print("1. 实时视频采集（Orbbec）")
    print("2. 使用文件夹中的照片采集")
    return input("请输入选项 (1/2): ").strip()


def capture_from_video() -> Optional[List[np.ndarray]]:
    """使用 Orbbec 相机实时采集人脸"""
    config = Config()
    pipeline = Pipeline()

    try:
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        try:
            color_profile: VideoStreamProfile = profile_list.get_video_stream_profile(640, 0, OBFormat.RGB, 30)
        except OBError as e:
            print(e)
            color_profile = profile_list.get_default_video_stream_profile()
            print("color profile: ", color_profile)
        config.enable_stream(color_profile)
    except Exception as e:
        print("[ERROR] 初始化 Orbbec 相机失败:", e)
        return None

    pipeline.start(config)
    print("\n[提示] 请正对Orbbec相机，按 'c' 采集，按 'q' 退出")
    embeddings = []
    global images_num
    pastTime = time.time()  # ✅ 初始化时间戳
    while True:
        try:
            frames: FrameSet = pipeline.wait_for_frames(100)
            if frames is None:
                continue

            color_frame = frames.get_color_frame()
            if color_frame is None:
                continue

            frame = frame_to_bgr_image(color_frame)
            if frame is None:
                continue

            # frame = pad_to_square(color_frame)
            display_frame = frame.copy()

            faces = app.get(frame)
            for face in faces:
                bbox = face.bbox.astype(int)
                cv2.rectangle(display_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)

            cv2.putText(display_frame, "The camera will capture the face every three seconds. ",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Face Registration", display_frame)

            key = cv2.waitKey(1) & 0xFF

            currentTime = time.time()
            if images_num == 10:
                break
            if currentTime - pastTime > 3:
                if not faces:
                    print("[警告] 未检测到人脸，请调整位置")
                    continue

                # 使用第一个检测到的人脸
                face = faces[0]

                pastTime = currentTime

                # 检查关键点
                if not hasattr(face, 'kps') or face.kps is None:
                    print("[错误] 人脸关键点检测失败")
                    continue

                # 直接使用 InsightFace 提供的对齐后特征
                if hasattr(face, 'normed_embedding'):
                    # 优化：确保使用float32精度
                    emb = face.normed_embedding.astype(np.float32)
                    embeddings.append(emb)
                    images_num += 1
                    print(f"[成功] 已采集 {len(embeddings)} 张人脸")
                else:
                    print("[错误] 无法获取人脸特征")
        except KeyboardInterrupt:
            break

    cv2.destroyAllWindows()
    pipeline.stop()
    return embeddings if embeddings else None


def capture_from_folder(folder_path: str) -> Optional[List[np.ndarray]]:
    """从文件夹批量采集人脸"""
    if not os.path.exists(folder_path):
        print(f"[错误] 文件夹不存在: {folder_path}")
        return None

    embeddings = []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(valid_extensions):
            continue

        image_path = os.path.join(folder_path, filename)
        img = cv2.imread(image_path)
        if img is None:
            print(f"[警告] 无法读取图片: {filename}")
            continue

        faces = app.get(img)
        if not faces:
            print(f"[警告] 图片中未检测到人脸: {filename}")
            continue

        face = faces[0]
        if hasattr(face, 'normed_embedding'):
            # 优化：确保使用float32精度
            embeddings.append(face.normed_embedding.astype(np.float32))
            print(f"[成功] 已处理: {filename}")
        else:
            print(f"[错误] 无法提取特征: {filename}")

    return embeddings if embeddings else None


def register_face(user_id: str, mode: str = '1', folder_path: str = None):
    """
    注册人脸信息
    :param user_id: 用户名
    :param mode: 采集模式（'1' 视频采集，'2' 文件夹采集）
    :param folder_path: mode=2 时需要的图片文件夹路径
    """
    # 加载数据库
    face_db = {}
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r') as f:
            face_db = json.load(f)

    # 选择采集模式
    # mode = select_capture_mode()

    if mode == '1':
        embeddings = capture_from_video()
    elif mode == '2':
        folder = r"/home/xuanwu/face_projects/images"
        embeddings = capture_from_folder(folder)
    else:
        print("[错误] 无效选项")
        return

    if embeddings:
        # user_id = input("\n请输入注册用户名: ").strip()
        # 优化：确保使用float32精度计算平均值
        avg_embedding = np.mean(np.array(embeddings, dtype=np.float32), axis=0)
        face_db[user_id] = avg_embedding.tolist()
        write_json(face_db, DB_PATH)
        print(f"\n[成功] 用户 '{user_id}' 已注册，共 {len(embeddings)} 张样本")
    else:
        print("\n[警告] 未采集到有效人脸数据")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="人脸注册脚本") 

    parser.add_argument("user_id", type=str, help="用户名")
    args = parser.parse_args()
    register_face(args.user_id)
