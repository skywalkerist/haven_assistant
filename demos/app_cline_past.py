import requests
import time
import json
import sys
import os
import base64

# 将src目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from marker_manager import MarkerManager
from audio_recorder import AudioRecorder
from train import train_and_register_voice
from voice_cloner import VoiceManager # 导入用于管理voices.json的类

# --- 配置区 ---
# 请将这里替换成你的uniCloud服务空间的URL化域名
UNICLOUD_BASE_URL = "https://fc-mp-503540be-00e4-400c-86f1-957c9c805a91.next.bspapp.com"
# 轮询间隔（秒）
POLL_INTERVAL = 1

# --- 全局变量 ---
marker_manager = MarkerManager()

# --- 函数定义区 ---

def call_unicloud_function(function_name, data={}):
    """调用指定的uniCloud云函数"""
    url = f"{UNICLOUD_BASE_URL}/{function_name}"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[Error] 调用云函数 {function_name} 时发生网络错误: {e}")
        return None

def update_command_status(command_id, status, result=None, error_message=None):
    """更新指令状态"""
    print(f"[Info] 更新指令 {command_id} 状态为: {status}")
    payload = {"commandId": command_id, "status": status}
    if result is not None:
        payload["result"] = result
    if error_message is not None:
        payload["errorMessage"] = error_message
    
    return call_unicloud_function('pollCommand', payload)

def process_task(command):
    """处理从云端获取的任务"""
    command_id = command['_id']
    task_name = command['task']
    params = command.get('params', {})
    
    print(f"--- [新任务] ---")
    print(f"  ID: {command_id}")
    print(f"  任务: {task_name}")
    print(f"  参数: {params}")

    # 只有需要连接机器人的任务才执行连接操作
    if task_name in ['get_marker_list', 'add_marker', 'delete_marker']:
        if not marker_manager.connect():
            print("[Error] 无法连接到机器人。")
            update_command_status(command_id, "failed", error_message="无法连接到机器人")
            return
    
    try:
        result_data = None
        error_msg = None

        if task_name == 'get_marker_list':
            response = marker_manager.get_marker_list()
            if response and response.get('status') == 'OK':
                result_data = response.get('results', {})
                print(result_data)
            else:
                error_msg = response.get('error_message', '获取点位列表失败')

        elif task_name == 'add_marker':
            name = params.get('name')
            if name:
                response = marker_manager.insert_marker_at_current_pos(name)
                if not (response and response.get('status') == 'OK'):
                    error_msg = response.get('error_message', '添加点位失败')
            else:
                error_msg = "缺少点位名称参数 'name'"

        elif task_name == 'delete_marker':
            name = params.get('name')
            if name:
                response = marker_manager.delete_marker(name)
                if not (response and response.get('status') == 'OK'):
                    error_msg = response.get('error_message', '删除点位失败')
            else:
                error_msg = "缺少点位名称参数 'name'"

        elif task_name == 'record_audio':
            # 1. 生成唯一文件名
            timestamp = int(time.time())
            unique_filename = f"cloned_voice_{timestamp}.wav"
            
            # 2. 录音
            recorder = AudioRecorder(sample_rate=24000)
            output_dir = os.path.join(os.path.dirname(__file__), 'run_temp')
            output_file = os.path.join(output_dir, unique_filename) # 使用新文件名
            
            print(f"开始录音，时长15秒，保存至 {output_file}")
            recorder.start_recording(output_file=output_file, record_timeout=15)
            
            # 3. 读取文件并进行Base64编码
            try:
                with open(output_file, 'rb') as f:
                    file_content_base64 = base64.b64encode(f.read()).decode('utf-8')
                # 可选：删除本地临时文件
                # os.remove(output_file)
            except Exception as e:
                error_msg = f"读取录音文件失败: {e}"
            
            # 4. 上传到云存储
            if not error_msg:
                print(f"正在上传录音文件 '{unique_filename}' 到云存储...")
                upload_result = call_unicloud_function('uploadAudio', {
                    'fileName': unique_filename, # 传递唯一文件名
                    'fileContent': file_content_base64
                })
                
                if upload_result and upload_result.get('success'):
                    result_data = {'audioUrl': upload_result.get('url')}
                    print(f"文件上传成功, URL: {result_data['audioUrl']}")
                else:
                    error_msg = "上传文件到云端失败"
        
        elif task_name == 'train_voice':
            voice_name = params.get('voiceName')
            audio_url = params.get('audioUrl')

            if not voice_name or not audio_url:
                error_msg = "缺少 'voiceName' 或 'audioUrl' 参数"
            else:
                print(f"开始调用声音训练，名称: {voice_name}, URL: {audio_url}")
                # 注意：这里的APPID和APIKEY需要与train.py中的一致
                # 你也可以将它们作为配置项读取，而不是硬编码
                APPID = 'b32f165e'
                APIKEY = 'bf4caffa0bd087acc04cd63d0ee27fc5'
                TEXT_ID = 5001
                TEXT_SEG_ID = 26 # 对应 "今天天气怎么样"

                res_id = train_and_register_voice(
                    appid=APPID,
                    apikey=APIKEY,
                    voice_name=voice_name,
                    audio_url=audio_url,
                    text_id=TEXT_ID,
                    text_seg_id=TEXT_SEG_ID
                )
                
                if res_id:
                    print(f"声音 '{voice_name}' 训练成功，ID: {res_id}")
                    result_data = {'res_id': res_id}
                else:
                    error_msg = "声音训练失败，请检查录音质量或服务状态"
        
        elif task_name == 'get_voices_config':
            try:
                # 注意：这里的路径是相对于 app_client.py 的
                config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'voices.json')
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result_data = {'fileContent': content}
                print("成功读取 voices.json 文件内容。")
            except Exception as e:
                error_msg = f"读取 voices.json 文件失败: {e}"

        elif task_name == 'set_voices_config':
            new_default_name = params.get('default_voice')
            if not new_default_name:
                error_msg = "缺少 'default_voice' 参数"
            else:
                try:
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'voices.json')
                    
                    # 读取JSON文件
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # 检查新默认值是否存在
                    if new_default_name in config:
                        # 更新default键的值为新名字对应的ID
                        config['default'] = config[new_default_name]
                        
                        # 写回JSON文件
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config, f, ensure_ascii=False, indent=4)
                        
                        print(f"成功将默认音色设置为: {new_default_name}")
                    else:
                        error_msg = f"音色名称 '{new_default_name}' 不存在于配置文件中"

                except Exception as e:
                    error_msg = f"更新 voices.json 文件失败: {e}"

        else:
            error_msg = f"未知的任务名称: {task_name}"

        # 根据执行结果更新状态
        if error_msg:
            update_command_status(command_id, "failed", error_message=error_msg)
        else:
            update_command_status(command_id, "completed", result=result_data)
            print("[Success] 任务执行成功。")

    finally:
        # 如果连接了机器人才断开
        if task_name in ['get_marker_list', 'add_marker', 'delete_marker']:
            marker_manager.disconnect()
        print("-----------------")


# --- 主循环 ---

if __name__ == '__main__':
    print("树莓派客户端已启动，开始轮询云端任务...")
    while True:
        try:
            print(f"\n正在查询新任务... ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            poll_result = call_unicloud_function('pollCommand')
            
            if poll_result and poll_result.get('success'):
                command = poll_result.get('command')
                if command:
                    process_task(command)
                else:
                    print("没有待处理的任务。")
            else:
                print("从云端获取任务失败，请检查网络或云函数日志。")

            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n程序已停止。")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")
            time.sleep(POLL_INTERVAL * 2)
