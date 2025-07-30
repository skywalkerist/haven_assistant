import json
import sys
import os
from openai import OpenAI
from voice_cloner import VoiceCloner
from deepseek_dialog import DeepSeekDialog

# 加入你的 myTools 模块路径
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
# from myTools import register, recognize




class Assistant:
    def __init__(self, api_key, base_url, filePath):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "recognize",
                    "description": "用户说要识别人脸时调用，不需要任何参数",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "register",
                    "description": "用户说要注册人脸时调用，采集人脸特征并存储到json数据库中，用户需要提供姓名",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "需要采集人脸的用户ID",
                            }
                        },
                        "required": ["user_id"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_reply",
                    "description": "当需要回答用户问题时调用",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                }
            },
        ]

        self.voiceCloner = VoiceCloner(
                                        app_id='b32f165e',
                                        api_key='bf4caffa0bd087acc04cd63d0ee27fc5',
                                        api_secret='MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
                                        # res_id='54ff6c2_ttsclone-b32f165e-xkras',
                                        text_file='/home/xuanwu/haven_ws/config/reply_deepseek.txt',
                                        output_file='/home/xuanwu/haven_ws/config/reply_deepseek.wav',
                                    )

        self.dialog = DeepSeekDialog(
                                    api_key="sk-fdabadb2973b4795b2444da60e75152f",
                                    input_path="/home/xuanwu/haven_ws/config/user_content.txt",
                                    output_path="/home/xuanwu/haven_ws/config/reply_deepseek.txt"
                                )

    def send_message(self, content):
        messages = [{"role": "user", "content": content}]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=self.tools
        )
        message = response.choices[0].message
        print(f"User>\t{content}")
        print(f"Model>\t{message.content}")

        if hasattr(message, "tool_calls"):
            if not message.tool_calls:
                self.iso_handle_get_reply()
                return
            self.handle_tool_call(message.tool_calls[0])
        else:
            print("没有触发任何工具调用。")

    def iso_handle_get_reply(self):
        self.handle_dialog()

    def handle_tool_call(self, tool_call):
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool Call>\t{tool_name}: {arguments}")

        if tool_name == "register":
            # self.handle_register(arguments)
            os.system("/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/register.py {arguments}")
            
        elif tool_name == "recognize":
            # self.handle_recognize()
            os.system("/home/xuanwu/miniconda3/envs/face/bin/python /home/xuanwu/haven_ws/src/myTools/recognize.py")
        elif tool_name == "get_reply":
            self.handle_dialog()
        else:
            print(f"未知的工具调用：{tool_name}")

    def handle_register(self, args):
        user_id = args.get("user_id")
        if user_id:
            print(f"开始注册人脸：{user_id}")
            register.register_face(user_id)
        else:
            print("缺少 user_id 参数，无法注册。")

    def handle_recognize(self):
        print("开始识别人脸...")
        recognize.recognize_faces()

    def handle_dialog(self):
        print("开始解析对话...")
        self.dialog.get_reply()
        self.voiceCloner.speak()
        self.voiceCloner.play_audio()

    def file2text(self, filePath):
        with open(filePath, "r", encoding="utf-8") as f:
            user_input = f.read().strip()
            return user_input



if __name__ == "__main__":
    assistant = assistant(
        api_key="sk-a4ce2451fc534091aff7704e5498a698",
        base_url="https://api.deepseek.com",
        filePath="xxxxx"
    )

    user_input = "我想识别当前用户的人脸"
    assistant.send_message(self.user_input)
