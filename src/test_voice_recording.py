#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音录音功能测试脚本
"""

import sys
import os
sys.path.append('/home/xuanwu/haven_ws/src')

from audio_recorder import AudioRecorder

def test_audio_recording():
    """测试音频录音功能"""
    print("🎤 测试音频录音功能")
    print("=" * 40)
    
    try:
        recorder = AudioRecorder()
        
        print("🔧 音频录音器初始化成功")
        print("📋 录音配置:")
        print(f"  采样率: {recorder.sample_rate} Hz")
        print(f"  声道数: {recorder.channels}")
        print(f"  缓冲区: {recorder.frames_per_buffer}")
        
        # 测试录音
        test_file = "/tmp/test_recording.wav"
        print(f"\n🎤 开始测试录音...")
        print("💡 请开始说话，系统会自动检测语音结束")
        print("⏰ 最多录音15秒")
        
        recorder.start_dynamic_recording(
            output_file=test_file,
            enable_vad=True,
            debug_output=True  # 启用调试输出查看VAD工作情况
        )
        
        print("✅ 录音完成")
        
        # 检查录音文件
        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"📁 录音文件: {test_file}")
            print(f"📊 文件大小: {file_size} 字节")
            
            if file_size > 1000:
                print("✅ 录音文件大小正常，可以进行语音识别")
            else:
                print("⚠️ 录音文件太小，可能没有录到有效语音")
        else:
            print("❌ 录音文件未生成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 语音录音系统测试")
    print("=" * 50)
    
    print("\n📋 测试说明:")
    print("• 这个测试将验证音频录音功能")
    print("• 请确保麦克风工作正常")
    print("• 说话时音量适中，环境相对安静")
    print("• 系统会自动检测语音结束")
    
    input("\n按 Enter 键开始测试...")
    
    success = test_audio_recording()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 语音录音功能测试成功！")
        print("💡 现在可以在超级智能体中使用真实的语音对话了")
    else:
        print("⚠️ 语音录音功能测试失败")
        print("💡 请检查麦克风设置和权限")
    print("=" * 50)

if __name__ == "__main__":
    main()