#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
# 将src目录添加到Python路径中，以便导入模块
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
# 加入你的 myTools 模块路径

from audio_recorder import AudioRecorder
from spark_asr import SparkASR
from deepseek_dialog import DeepSeekDialog
from voice_cloner import VoiceCloner
from deepseekAgent import Assistant

def main():
    # --- 配置 ---
    # 讯飞 API 凭证
    XF_APP_ID = 'b32f165e'
    XF_API_KEY = 'bf4caffa0bd087acc04cd63d0ee27fc5'
    XF_API_SECRET = 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0'
    
    # DeepSeek API 凭证
    DEEPSEEK_API_KEY = "sk-fdabadb2973b4795b2444da60e75152f"

    # 语音克隆资源 ID
    VOICE_CLONE_RES_ID = '54ff6c2_ttsclone-b32f165e-xkras'

    # 文件路径配置
    # 使用os.path.join确保跨平台兼容性
    work_dir = "/home/xuanwu/haven_ws/demo/run_temp"
    audio_file = os.path.join(work_dir, "input.wav")
    asr_result_file = "/home/xuanwu/haven_ws/config/user_content.txt" # os.path.join(work_dir, "asr_result.txt")
    dialog_reply_file = os.path.join(work_dir, "dialog_reply.txt")
    tts_output_file = os.path.join(work_dir, "output.wav")

    # 创建工作目录
    os.makedirs(work_dir, exist_ok=True)

    # --- 步骤 1: 录音 ---
    print("="*10 + " 1/4. 开始录音 " + "="*10)
    recorder = AudioRecorder()
    recorder.start_recording(output_file=audio_file, record_timeout=5)
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        print("❌ 录音失败或文件为空，程序终止。")
        return
    print("✅ 录音完成\n")

    # --- 步骤 2: 语音识别 (ASR) ---
    print("="*10 + " 2/4. 开始语音识别 " + "="*10)
    asr = SparkASR(
        app_id=XF_APP_ID,
        api_key=XF_API_KEY,
        api_secret=XF_API_SECRET,
        audio_file=audio_file,
        output_file=asr_result_file
    )
    asr.recognize()
    if not os.path.exists(asr_result_file) or os.path.getsize(asr_result_file) == 0:
        print("❌ 语音识别失败或结果为空，程序终止。")
        return
    print("✅ 语音识别完成\n")

    # --- 步骤 3: 对话 ---
    print("="*10 + " 3/4. 开始生成对话 " + "="*10)

    assistant = Assistant(
        api_key="sk-a4ce2451fc534091aff7704e5498a698",
        base_url="https://api.deepseek.com",
        filePath=asr_result_file,
        # outputPath=
    )
    user_input = assistant.file2text(asr_result_file)
    assistant.send_message(user_input)

    # dialog = DeepSeekDialog(
    #     api_key=DEEPSEEK_API_KEY,
    #     input_path=asr_result_file,
    #     output_path=dialog_reply_file
    # )
    # dialog.get_reply()
    # if not os.path.exists(dialog_reply_file) or os.path.getsize(dialog_reply_file) == 0:
    #     print("❌ 对话生成失败或结果为空，程序终止。")
    #     return
    # print("✅ 对话生成完成\n")

    # --- 步骤 4: 语音合成 (TTS) & 播放 ---
    # print("="*10 + " 4/4. 开始语音合成 " + "="*10)
    # cloner = VoiceCloner(
    #     app_id=XF_APP_ID,
    #     api_key=XF_API_KEY,
    #     api_secret=XF_API_SECRET,
    #     res_id=VOICE_CLONE_RES_ID,
    #     text_file=dialog_reply_file,
    #     output_file=tts_output_file
    # )
    # cloner.speak()
    # print("✅ 语音合成完成\n")
    
    # cloner.play_audio()

    print("\n=== 全部流程完成 ===")

if __name__ == "__main__":
    main()
