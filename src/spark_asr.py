#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _thread as thread
import time
import websocket
import base64
import datetime
import hashlib
import hmac
import json
import ssl
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2

class SparkASR:
    def __init__(self, app_id, api_key, api_secret, audio_file, output_file):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.audio_file = audio_file
        self.output_file = output_file
        self.iat_params = {
            "domain": "slm", "language": "zh_cn", "accent": "mulacc", "result": {
                "encoding": "utf8", "compress": "raw", "format": "json"
            }
        }
        self.full_text = []
        self.ws = None

    def create_url(self):
        url = 'wss://iat.cn-huabei-1.xf-yun.com/v1'
        now = datetime.datetime.now()
        date = format_date_time(time.mktime(now.timetuple()))
        signature_origin = "host: iat.cn-huabei-1.xf-yun.com\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET /v1 HTTP/1.1"
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "iat.cn-huabei-1.xf-yun.com"
        }
        url = url + '?' + urlencode(v)
        return url

    def on_message(self, ws, message):
        msg = json.loads(message)
        code = msg["header"]["code"]
        status = msg["header"]["status"]

        if code != 0:
            print(f"请求错误：{code}")
            ws.close()
            return

        payload = msg.get("payload")
        if payload:
            text_b64 = payload["result"]["text"]
            text_json = json.loads(base64.b64decode(text_b64).decode())
            segment = ''.join(w["w"] for i in text_json["ws"] for w in i["cw"])
            self.full_text.append(segment)

        if status == 2:
            final = ''.join(self.full_text).replace(' ', '')
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(final)
            print(f"text: {final}")
            print(f'识别结果已写入 {self.output_file}')
            ws.close()

    def on_error(self, ws, error):
        print("### error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            frameSize = 1280
            intervel = 0.04
            status = STATUS_FIRST_FRAME
            with open(self.audio_file, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    audio = str(base64.b64encode(buf), 'utf-8')
                    if not audio:
                        status = STATUS_LAST_FRAME
                    
                    if status == STATUS_FIRST_FRAME:
                        d = {"header": {"status": 0, "app_id": self.app_id},
                             "parameter": {"iat": self.iat_params},
                             "payload": {"audio": {"audio": audio, "sample_rate": 16000, "encoding": "raw"}}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"header": {"status": 1, "app_id": self.app_id},
                             "payload": {"audio": {"audio": audio, "sample_rate": 16000, "encoding": "raw"}}}
                        ws.send(json.dumps(d))
                    elif status == STATUS_LAST_FRAME:
                        d = {"header": {"status": 2, "app_id": self.app_id},
                             "payload": {"audio": {"audio": audio, "sample_rate": 16000, "encoding": "raw"}}}
                        ws.send(json.dumps(d))
                        break
                    time.sleep(intervel)
        thread.start_new_thread(run, ())

    def recognize(self):
        websocket.enableTrace(False)
        wsUrl = self.create_url()
        self.ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == '__main__':
    # 示例用法
    asr = SparkASR(
        app_id='b32f165e',
        api_secret='MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
        api_key='bf4caffa0bd087acc04cd63d0ee27fc5',
        audio_file='output.wav',
        output_file='result.txt'
    )
    asr.recognize()
