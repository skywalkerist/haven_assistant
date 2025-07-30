#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from openai import OpenAI
import os

class DeepSeekDialog:
    def __init__(self, api_key, input_path, output_path):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.input_path = input_path
        self.output_path = output_path

    def get_reply(self):
        if not os.path.exists(self.input_path):
            print(f"Error: Input file not found at {self.input_path}")
            return

        with open(self.input_path, "r", encoding="utf-8") as f:
            user_content = f.read().strip()

        if not user_content:
            print("Error: Input file is empty.")
            return
            
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个养老助手,名字叫做小猪，熟悉生活常识和养老知识。请用普通文本回答,不要使用Markdown格式,不要有特殊符号,且回答限制在100个汉字以内。"},
                {"role": "user", "content": user_content}
            ],
            stream=False
        )

        reply = response.choices[0].message.content
        print(f"reply: {reply}")

        output_dir = os.path.dirname(self.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(reply)

        print(f"已把回复写入 {self.output_path}")

if __name__ == '__main__':
    # 示例用法
    dialog = DeepSeekDialog(
        api_key="sk-fdabadb2973b4795b2444da60e75152f",
        input_path="result.txt",
        output_path="reply_deepseek.txt"
    )
    dialog.get_reply()
