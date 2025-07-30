#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyaudio
import wave
import time
import os
import logging
from ctypes import *
from contextlib import contextmanager

# 日志配置
logging.basicConfig()
logger = logging.getLogger("audio_recorder")
logger.setLevel(logging.INFO)

# 屏蔽ALSA错误
def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class FixedAudioRecorder:
    def __init__(self, sample_rate=16000, channels=1, 
                 audio_format=pyaudio.paInt16, frames_per_buffer=2048):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = audio_format
        self.frames_per_buffer = frames_per_buffer
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.recorded_frames = []
        
        # 自动检测可用的音频输入设备
        self.input_device_index = self._find_input_device()
        
    def _find_input_device(self):
        """自动找到可用的音频输入设备"""
        try:
            with no_alsa_error():
                audio = pyaudio.PyAudio()
                
                print("🔍 检测可用的音频输入设备...")
                input_devices = []
                
                for i in range(audio.get_device_count()):
                    device_info = audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        input_devices.append(i)
                        print(f"  设备 {i}: {device_info['name']} (输入通道: {device_info['maxInputChannels']})")
                
                audio.terminate()
                
                if input_devices:
                    # 优先选择USB音频设备
                    usb_devices = []
                    with no_alsa_error():
                        audio = pyaudio.PyAudio()
                        for device_idx in input_devices:
                            device_info = audio.get_device_info_by_index(device_idx)
                            if 'USB' in device_info['name'].upper() or 'AUDIO' in device_info['name'].upper():
                                usb_devices.append(device_idx)
                        audio.terminate()
                    
                    if usb_devices:
                        selected_device = usb_devices[0]
                        print(f"✅ 选择USB音频设备: {selected_device}")
                        return selected_device
                    else:
                        selected_device = input_devices[0]
                        print(f"✅ 选择默认音频设备: {selected_device}")
                        return selected_device
                else:
                    print("❌ 未找到可用的音频输入设备")
                    return None
                    
        except Exception as e:
            print(f"❌ 音频设备检测失败: {e}")
            return None

    def start_recording(self, output_file, record_timeout=10, interrupt_check=lambda: False):
        """开始录音"""
        if self.input_device_index is None:
            print("❌ 没有可用的音频输入设备")
            return False
            
        self.is_recording = True
        self.recorded_frames = []
        
        try:
            with no_alsa_error():
                self.audio = pyaudio.PyAudio()
                
                # 获取设备信息
                device_info = self.audio.get_device_info_by_index(self.input_device_index)
                print(f"📡 使用设备: {device_info['name']}")
                
                # 尝试不同的采样率
                supported_rates = [16000]
                actual_rate = self.sample_rate
                
                for rate in supported_rates:
                    try:
                        # 测试是否支持该采样率
                        test_stream = self.audio.open(
                            format=self.audio_format,
                            channels=self.channels,
                            rate=rate,
                            input=True,
                            input_device_index=self.input_device_index,
                            frames_per_buffer=self.frames_per_buffer
                        )
                        test_stream.close()
                        actual_rate = rate
                        print(f"✅ 使用采样率: {actual_rate} Hz")
                        break
                    except Exception as e:
                        print(f"采样率 {rate} 不支持: {e}")
                        continue
                
                # 创建音频流
                self.stream = self.audio.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=actual_rate,
                    input=True,
                    input_device_index=self.input_device_index,
                    frames_per_buffer=self.frames_per_buffer
                )

            print("🎤 开始录音...")
            start_time = time.time()
            
            # 同步录音方式，更稳定
            while self.is_recording:
                if (time.time() - start_time) > record_timeout:
                    print("⏰ 录音超时")
                    break
                if interrupt_check():
                    print("🛑 录音被中断")
                    break
                
                try:
                    # 读取音频数据
                    data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                    if data:
                        self.recorded_frames.append(data)
                except Exception as e:
                    print(f"读取音频数据失败: {e}")
                    break

        except KeyboardInterrupt:
            print("🛑 用户中断录音")
        except Exception as e:
            print(f"❌ 录音失败: {e}")
            return False
        finally:
            self._stop_recording()
            success = self._save_wav(output_file, actual_rate)
            return success

    def _stop_recording(self):
        """停止录音"""
        self.is_recording = False
        
        if self.stream is not None:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
            
        if self.audio is not None:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None

    def _save_wav(self, filename, actual_rate):
        """保存WAV文件"""
        if not self.recorded_frames:
            print("❌ 没有录音数据可保存")
            return False

        try:
            # 确保目录存在
            dirname = os.path.dirname(filename)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            
            # 创建临时pyaudio实例获取样本宽度
            with no_alsa_error():
                temp_audio = pyaudio.PyAudio()
                sample_width = temp_audio.get_sample_size(self.audio_format)
                temp_audio.terminate()
            
            # 保存WAV文件
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(actual_rate)
                wf.writeframes(b''.join(self.recorded_frames))
            
            # 检查文件大小
            file_size = os.path.getsize(filename)
            print(f"✅ 音频已保存: {os.path.abspath(filename)} (大小: {file_size} 字节)")
            
            return file_size > 1000  # 至少1KB才算成功
            
        except Exception as e:
            print(f"❌ 保存音频文件失败: {e}")
            return False

def test_recording():
    """测试录音功能"""
    print("🧪 测试录音功能...")
    recorder = FixedAudioRecorder()
    
    if recorder.input_device_index is None:
        print("❌ 测试失败：没有可用的音频设备")
        return False
    
    test_file = "/tmp/test_recording.wav"
    print("请说话，录音5秒...")
    
    success = recorder.start_recording(test_file, record_timeout=5)
    
    if success and os.path.exists(test_file):
        file_size = os.path.getsize(test_file)
        print(f"✅ 录音测试成功！文件大小: {file_size} 字节")
        return True
    else:
        print("❌ 录音测试失败")
        return False

if __name__ == "__main__":
    test_recording()