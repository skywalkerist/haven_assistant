#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的录音功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from fixed_audio_recorder import FixedAudioRecorder

def test_recording_with_demo():
    """测试录音功能并播放录音结果"""
    print("=" * 50)
    print("录音功能测试")
    print("=" * 50)
    
    # 创建录音器
    recorder = FixedAudioRecorder()
    
    if recorder.input_device_index is None:
        print("❌ 没有可用的音频设备，测试失败")
        return False
    
    # 测试录音
    output_file = "/home/xuanwu/haven_ws/demos/temp/test_record.wav"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("请准备说话，录音将持续5秒...")
    input("按Enter键开始录音...")
    
    success = recorder.start_recording(output_file, record_timeout=5)
    
    if success:
        print(f"✅ 录音成功！文件保存在: {output_file}")
        
        # 检查文件
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"文件大小: {file_size} 字节")
            
            # 尝试播放录音（如果有aplay）
            try:
                import subprocess
                print("正在播放录音...")
                subprocess.run(['aplay', output_file])
            except:
                print("无法播放录音（aplay不可用）")
        
        return True
    else:
        print("❌ 录音失败")
        return False

if __name__ == "__main__":
    test_recording_with_demo()