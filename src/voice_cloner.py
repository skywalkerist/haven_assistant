#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import websocket
import json
import hashlib
import base64
import hmac
import ssl
import os
import sys
from urllib.parse import urlencode
from datetime import datetime, timezone

class VoiceManager:
    def __init__(self, config_file='../config/voices.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file)
        self.voices = self._load_config()

    def _load_config(self):
        """加载声音配置文件"""
        if not os.path.exists(self.config_file):
            print(f"❌ 配置文件不存在: {self.config_file}")
            return {}
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"❌ 配置文件格式错误: {self.config_file}")
            return {}

    def get_res_id(self, voice_name):
        """根据名称获取res_id"""
        return self.voices.get(voice_name)

    def add_voice(self, voice_name, res_id):
        """添加或更新一个声音配置"""
        self.voices[voice_name] = res_id
        self._save_config()
        print(f"✅ 已添加/更新声音 '{voice_name}'")

    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.voices, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")

class VoiceCloner:
    def __init__(self, app_id, api_key, api_secret, text_file, output_file, voice_name='default', config_path='../config/voices.json'):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.text_file = text_file
        self.output_file = output_file
        self.ws = None
        self.text_to_speak = ""

        # 从VoiceManager获取res_id
        self.voice_manager = VoiceManager(config_file=config_path)
        self.res_id = self.voice_manager.get_res_id(voice_name)
        if not self.res_id:
            sys.exit(f"❌ 无法在配置文件中找到名为 '{voice_name}' 的声音。")
        
        print(f"🎤 使用声音: '{voice_name}' (res_id: {self.res_id[:15]}...)")


    def _create_url(self):
        host = 'cn-huabei-1.xf-yun.com'
        path = '/v1/private/voice_clone'
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        sign_origin = f'host: {host}\ndate: {date}\nGET {path} HTTP/1.1'
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode(), sign_origin.encode(), hashlib.sha256).digest()
        ).decode()
        authorization = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization.encode()).decode()
        return f'wss://{host}{path}?{urlencode({"host": host, "date": date, "authorization": authorization})}'

    def on_message(self, ws, msg):
        data = json.loads(msg)
        if data['header']['code'] != 0:
            print(f'❌ 合成失败: {data}')
            ws.close()
            return
        
        pcm = base64.b64decode(data['payload']['audio']['audio'])
        with open(self.output_file, 'ab') as f:
            f.write(pcm)
            
        if data['payload']['audio']['status'] == 2:
            print(f'✅ 合成完成，已保存 {self.output_file}')
            ws.close()

    def on_error(self, ws, e):
        print('❌', e)

    def on_close(self, ws, a, b):
        pass

    def on_open(self, ws):
        ws.send(json.dumps({
            "header": {"app_id": self.app_id, "res_id": self.res_id, "status": 2},
            "parameter": {
                "tts": {
                    "vcn": "x5_clone", "volume": 50, "speed": 50, "pitch": 50,
                    "audio": {"encoding": "raw", "sample_rate": 16000, "channels": 1, "bit_depth": 16}
                }
            },
            "payload": {
                "text": {"encoding": "utf8", "compress": "raw", "format": "plain", "status": 2,
                         "text": base64.b64encode(self.text_to_speak.encode()).decode()}
            }
        }))

    def speak(self):
        if not os.path.isfile(self.text_file):
            sys.exit(f'❌ 未找到 {self.text_file}')
        with open(self.text_file, encoding='utf-8') as f:
            self.text_to_speak = f.read().strip()
            print(f"朗读内容: {self.text_to_speak}")

        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        ws_url = self._create_url()
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})

    def play_audio(self):
        if os.path.exists(self.output_file):
            print("正在播放...")
            os.system(f'aplay -f S16_LE -r 16000 -c 1 {self.output_file}')
        else:
            print("❌ 未生成音频文件")

if __name__ == '__main__':
    # 使用方法:
    # 1. 直接运行，使用默认声音 'default'
    # python voice_cloner.py
    # 2. 在命令行指定要使用的声音名称
    # python voice_cloner.py your_voice_name
    
    voice_to_use = 'default'
    if len(sys.argv) > 1:
        voice_to_use = sys.argv[1]

    cloner = VoiceCloner(
        app_id='b32f165e',
        api_key='bf4caffa0bd087acc04cd63d0ee27fc5',
        api_secret='MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
        voice_name=voice_to_use,
        text_file='/home/xuanwu/haven_ws/config/greeting.txt',
        output_file='/home/xuanwu/haven_ws/config/greeting.wav',
        config_path='../config/voices.json'
    )
    cloner.speak()
    cloner.play_audio()
