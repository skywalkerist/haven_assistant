#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态录音功能测试脚本
测试音量阈值法VAD的效果
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio_recorder import AudioRecorder

def test_dynamic_recording():
    """测试动态录音功能"""
    print("=" * 60)
    print("动态录音功能测试")
    print("=" * 60)
    
    recorder = AudioRecorder()
    
    # 显示当前VAD配置
    print("📊 当前VAD配置:")
    for key, value in recorder.vad_config.items():
        print(f"   {key}: {value}")
    
    print("\n🎤 即将开始动态录音测试...")
    print("说话建议：")
    print("- 前2秒是预热期，不会检测静音")
    print("- 2秒后开始说话（3-5秒）")
    print("- 然后保持安静2秒以上")
    print("- 观察是否自动停止录音")
    
    try:
        input("\n按回车键开始测试...")
        
        # 测试动态录音
        test_file = "/tmp/test_dynamic_recording.wav"
        recorder.start_dynamic_recording(
            output_file=test_file,
            enable_vad=True,
            debug_output=True  # 显示详细的VAD信息
        )
        
        # 检查录音结果
        if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            file_size = os.path.getsize(test_file)
            print(f"\n✅ 录音成功！")
            print(f"   文件路径: {test_file}")
            print(f"   文件大小: {file_size} bytes")
            
            # 估算录音时长
            # 假设16kHz, 16bit, 单声道: 32000 bytes/秒
            estimated_duration = file_size / 32000
            print(f"   估算时长: {estimated_duration:.1f}秒")
        else:
            print("\n❌ 录音失败！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")

def test_noise_calibration():
    """测试环境噪音校准"""
    print("\n" + "=" * 60)
    print("环境噪音校准测试")
    print("=" * 60)
    
    recorder = AudioRecorder()
    
    print("🔧 请保持安静，正在校准环境噪音...")
    try:
        recorder._calibrate_noise_level()
        print(f"✅ 校准完成，动态阈值: {recorder.vad_config['silent_threshold']:.4f}")
    except Exception as e:
        print(f"❌ 校准失败: {e}")

def main():
    """主函数"""
    try:
        print("选择测试项目:")
        print("1. 动态录音功能测试")
        print("2. 环境噪音校准测试")
        print("3. 两项都测试")
        
        choice = input("请选择 (1/2/3): ").strip()
        
        if choice == "1":
            test_dynamic_recording()
        elif choice == "2":
            test_noise_calibration()
        elif choice == "3":
            test_noise_calibration()
            test_dynamic_recording()
        else:
            print("无效选择，运行完整测试...")
            test_noise_calibration()
            test_dynamic_recording()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()