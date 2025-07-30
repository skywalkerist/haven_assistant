#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyaudio
import wave
import time
import os
import logging
import math
import struct
import numpy as np
from ctypes import *
from contextlib import contextmanager

# 日志配置
logging.basicConfig()
logger = logging.getLogger("audio_recorder")
logger.setLevel(logging.INFO)

# 提示音配置
# BEEP_START = 1000  # 开始提示音频率(Hz)
# BEEP_END = 800     # 结束提示音频率(Hz)
# BEEP_DURATION = 0.3  # 提示音时长(秒)

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

class AudioRecorder:
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
        
        # VAD (Voice Activity Detection) 参数
        self.vad_config = {
            'silent_threshold': 0.01,      # 静音阈值
            'silent_duration': 2.0,        # 连续静音时长(秒)
            'min_recording_time': 0.5,     # 最小录音时长(秒)
            'max_recording_time': 15.0,    # 最大录音时长(秒)
            'noise_calibration_time': 1.0, # 环境噪音校准时间(秒)
            'adaptive_threshold': True,     # 是否使用自适应阈值
            'warmup_time': 2.0,            # 预热期时长(秒) - 此期间不进行静音检测
        }

    def _calculate_rms_volume(self, audio_data):
        """计算音频数据的RMS音量"""
        try:
            # 转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            if len(audio_array) == 0:
                return 0.0
            
            # 归一化到[-1, 1]
            normalized = audio_array.astype(np.float32) / 32768.0
            
            # 计算RMS (Root Mean Square)
            rms = np.sqrt(np.mean(normalized ** 2))
            
            return rms
        except Exception as e:
            logger.warning(f"Error calculating RMS volume: {e}")
            return 0.0

    def _calibrate_noise_level(self):
        """校准环境噪音水平，动态设置静音阈值"""
        logger.info("🔧 正在校准环境噪音水平...")
        
        noise_samples = []
        calibration_frames = int(self.vad_config['noise_calibration_time'] * self.sample_rate / self.frames_per_buffer)
        
        try:
            with no_alsa_error():
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.frames_per_buffer
                )
            
            for _ in range(calibration_frames):
                audio_data = stream.read(self.frames_per_buffer)
                volume = self._calculate_rms_volume(audio_data)
                noise_samples.append(volume)
                time.sleep(0.05)  # 50ms间隔
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # 计算环境噪音统计
            avg_noise = np.mean(noise_samples)
            noise_std = np.std(noise_samples)
            max_noise = np.max(noise_samples)
            
            # 动态设置阈值：平均噪音 + 3倍标准差，但不低于基础阈值
            if self.vad_config['adaptive_threshold']:
                adaptive_threshold = max(0.005, avg_noise + 3 * noise_std, max_noise * 1.5)
                self.vad_config['silent_threshold'] = adaptive_threshold
            
            logger.info(f"🔧 环境噪音校准完成:")
            logger.info(f"   平均噪音: {avg_noise:.4f}")
            logger.info(f"   最大噪音: {max_noise:.4f}")
            logger.info(f"   静音阈值: {self.vad_config['silent_threshold']:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 噪音校准失败: {e}")
            logger.info(f"使用默认阈值: {self.vad_config['silent_threshold']:.4f}")
            return False

    def start_dynamic_recording(self, output_file, enable_vad=True, debug_output=False):
        """
        开始动态录音（支持VAD语音活动检测）
        
        Args:
            output_file: 输出文件路径
            enable_vad: 是否启用语音活动检测
            debug_output: 是否输出调试信息
        """
        logger.info("🎤 开始动态录音...")
        
        # 环境噪音校准
        # if enable_vad and self.vad_config['adaptive_threshold']:
        #     self._calibrate_noise_level()
        self.vad_config['silent_threshold']=0.05
        self.is_recording = True
        self.recorded_frames = []
        
        # VAD状态变量
        total_silent_time = 0.0
        total_recording_time = 0.0
        chunk_duration = self.frames_per_buffer / self.sample_rate  # 每个音频块的时长
        
        try:
            with no_alsa_error():
                self.audio = pyaudio.PyAudio()
                self.stream = self.audio.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.frames_per_buffer
                )

            logger.info("🎤 录音开始，请说话...")
            start_time = time.time()
            
            while self.is_recording:
                try:
                    # 读取音频数据
                    audio_data = self.stream.read(self.frames_per_buffer)
                    self.recorded_frames.append(audio_data)
                    total_recording_time += chunk_duration
                    
                    if enable_vad:
                        # 计算当前音频块的音量
                        current_volume = self._calculate_rms_volume(audio_data)
                        
                        # 检查是否还在预热期
                        in_warmup_period = total_recording_time < self.vad_config['warmup_time']
                        
                        if in_warmup_period:
                            # 预热期内不进行静音检测，但可以显示音量信息
                            if debug_output:
                                remaining_warmup = self.vad_config['warmup_time'] - total_recording_time
                                print(f"🔥 预热期: 还剩{remaining_warmup:.1f}s (音量: {current_volume:.4f})")
                        else:
                            # 预热期结束，开始正常的静音检测
                            if current_volume < self.vad_config['silent_threshold']:
                                total_silent_time += chunk_duration
                                if debug_output:
                                    print(f"🔇 静音检测: {total_silent_time:.1f}s (音量: {current_volume:.4f})")
                            else:
                                total_silent_time = 0.0  # 重置静音计时
                                if debug_output:
                                    print(f"🔊 语音检测: 音量={current_volume:.4f}")
                            
                            # 停止条件判断（只在预热期结束后检查）
                            if total_recording_time >= self.vad_config['min_recording_time']:
                                if total_silent_time >= self.vad_config['silent_duration']:
                                    logger.info(f"✅ 检测到语音结束 (静音{total_silent_time:.1f}s)，停止录音")
                                    break
                        
                        # 超过最大录音时长（无论是否在预热期都要检查）
                        if total_recording_time >= self.vad_config['max_recording_time']:
                            logger.info(f"⏰ 达到最大录音时长({self.vad_config['max_recording_time']}s)，强制停止")
                            break
                    else:
                        # 不使用VAD，传统固定时长录音
                        if total_recording_time >= 10.0:  # 默认10秒
                            logger.info("⏰ 固定录音时长结束")
                            break
                    
                except Exception as e:
                    logger.error(f"录音过程中出错: {e}")
                    break

        except KeyboardInterrupt:
            logger.info("⚠️ 录音被用户中断")
        except Exception as e:
            logger.error(f"❌ 录音初始化失败: {e}")
        finally:
            self._stop_recording()
            
            # 显示录音统计
            logger.info(f"📊 录音统计:")
            logger.info(f"   总录音时长: {total_recording_time:.1f}秒")
            if enable_vad:
                logger.info(f"   预热期时长: {min(self.vad_config['warmup_time'], total_recording_time):.1f}秒")
                logger.info(f"   最终静音时长: {total_silent_time:.1f}秒")
                logger.info(f"   使用的静音阈值: {self.vad_config['silent_threshold']:.4f}")
            
            self._save_wav(output_file)

    # 保持原有的 start_recording 方法以确保向后兼容

    # def _play_beep(self): # frequency, duration
        
        # """播放指定频率的提示音"""
        # try:
        #     sample_count = int(self.sample_rate * duration)
        #     samples = [int(32767 * 0.5 * math.sin(2 * math.pi * frequency * x / self.sample_rate)) 
        #               for x in range(sample_count)]
        #     beep_data = b''.join(struct.pack('h', sample) for sample in samples)
            
        #     with no_alsa_error():
        #         beep_stream = self.audio.open(
        #             format=self.audio_format,
        #             channels=self.channels,
        #             rate=self.sample_rate,
        #             output=True
        #         )
        #         beep_stream.write(beep_data)
        #         beep_stream.stop_stream()
        #         beep_stream.close()
        # except Exception as e:
        #     logger.warning(f"Could not play beep: {str(e)}")

    def start_recording(self, output_file, record_timeout=10, interrupt_check=lambda: False):
        self.is_recording = True
        self.recorded_frames = []
        
        def audio_callback(in_data, frame_count, time_info, status):
            self.recorded_frames.append(in_data)
            return (None, pyaudio.paContinue)

        try:
            with no_alsa_error():
                self.audio = pyaudio.PyAudio()
                self.stream = self.audio.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.frames_per_buffer,
                    stream_callback=audio_callback
                )

            logger.info("Playing start beep...")
            # self._play_beep() # BEEP_START, BEEP_DURATION
            time.sleep(0.2)
            
            logger.info("Recording started...")
            start_time = time.time()
            
            while self.is_recording:
                if (time.time() - start_time) > record_timeout:
                    logger.info("Recording stopped: reached timeout")
                    break
                if interrupt_check():
                    logger.info("Recording stopped by interrupt")
                    break
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Recording stopped by user")
        finally:
            self._stop_recording()
            logger.info("Playing end beep...")
            # self._play_beep(BEEP_END, BEEP_DURATION)
            self._save_wav(output_file)

    def _stop_recording(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio is not None:
            self.audio.terminate()
        self.is_recording = False

    def _save_wav(self, filename):
        if not self.recorded_frames:
            logger.warning("No audio data to save")
            return

        dirname = os.path.dirname(filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.recorded_frames))
        
        logger.info(f"Audio saved to {os.path.abspath(filename)}")

if __name__ == "__main__":
    recorder = AudioRecorder()
    
    try:
        print("准备开始录音...")
        recorder.start_recording(
            output_file="output.wav",
            record_timeout=5
        )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        print("程序结束")
