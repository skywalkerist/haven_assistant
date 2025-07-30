import requests
import time
import json
import sys
import os
import base64
import wave
import struct

# 将src目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from marker_manager import MarkerManager
from move_controller import MoveController
from audio_recorder import AudioRecorder
from train import train_and_register_voice
from voice_cloner import VoiceManager
from spark_asr import SparkASR
from deepseek_dialog import DeepSeekDialog

# --- 配置区 ---
UNICLOUD_BASE_URL = "https://fc-mp-503540be-00e4-400c-86f1-957c9c805a91.next.bspapp.com"
POLL_INTERVAL = 3
SPARK_APP_ID = 'b32f165e'
SPARK_API_SECRET = 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0'
SPARK_API_KEY = 'bf4caffa0bd087acc04cd63d0ee27fc5'
DEEPSEEK_API_KEY = "sk-fdabadb2973b4795b2444da60e75152f"

# --- 全局变量 ---
marker_manager = MarkerManager()
move_controller = MoveController()
RUN_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'run_temp')
os.makedirs(RUN_TEMP_DIR, exist_ok=True)

# --- 辅助函数 ---
def add_wav_header(pcm_data, sample_rate=16000, channels=1, sample_width=2):
    """为原始PCM数据添加WAV文件头"""
    wav_header = bytearray()
    # RIFF chunk
    wav_header.extend(b'RIFF')
    # ChunkSize
    wav_header.extend(struct.pack('<I', len(pcm_data) + 36))
    wav_header.extend(b'WAVE')
    # fmt sub-chunk
    wav_header.extend(b'fmt ')
    wav_header.extend(struct.pack('<I', 16))  # Subchunk1Size for PCM
    wav_header.extend(struct.pack('<H', 1))   # AudioFormat (PCM)
    wav_header.extend(struct.pack('<H', channels))
    wav_header.extend(struct.pack('<I', sample_rate))
    wav_header.extend(struct.pack('<I', sample_rate * channels * sample_width)) # ByteRate
    wav_header.extend(struct.pack('<H', channels * sample_width)) # BlockAlign
    wav_header.extend(struct.pack('<H', sample_width * 8)) # BitsPerSample
    # data sub-chunk
    wav_header.extend(b'data')
    wav_header.extend(struct.pack('<I', len(pcm_data)))
    
    return wav_header + pcm_data

# --- 云函数交互 ---
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

# --- 任务处理 ---
def process_task(command):
    """处理从云端获取的任务"""
    command_id = command['_id']
    task_name = command['task']
    params = command.get('params', {})
    
    print(f"--- [新任务] ---")
    print(f"  ID: {command_id}")
    print(f"  任务: {task_name}")
    print(f"  参数: {params.keys()}") # 只打印参数的键，避免base64刷屏

    # 只有需要连接机器人的任务才执行连接操作
    robot_tasks = ['get_marker_list', 'add_marker', 'delete_marker', 'move_to_point']
    if task_name in robot_tasks:
        if not marker_manager.connect():
            print("[Error] 无法连接到机器人。")
            update_command_status(command_id, "failed", error_message="无法连接到机器人")
            print("-----------------")
            return

    try:
        result_data = None
        error_msg = None

        if task_name == 'speech_to_text':
            audio_url = params.get('audioUrl')
            if not audio_url:
                error_msg = "缺少 audioUrl 参数"
            else:
                try:
                    # 1. 从URL下载PCM文件
                    print(f"正在从 {audio_url} 下载音频...")
                    response = requests.get(audio_url, timeout=20)
                    response.raise_for_status()
                    pcm_data = response.content
                    print("音频下载成功。")

                    # 2. 添加WAV头并保存为临时文件
                    wav_data = add_wav_header(pcm_data)
                    temp_wav_path = os.path.join(RUN_TEMP_DIR, f"asr_input_{command_id}.wav")
                    with open(temp_wav_path, 'wb') as f:
                        f.write(wav_data)
                    
                    # 3. 调用语音识别
                    print("正在调用讯飞 ASR...")
                    temp_result_path = os.path.join(RUN_TEMP_DIR, f"asr_result_{command_id}.txt")
                    asr = SparkASR(
                        app_id=SPARK_APP_ID, api_secret=SPARK_API_SECRET, api_key=SPARK_API_KEY,
                        audio_file=temp_wav_path, output_file=temp_result_path
                    )
                    asr.recognize()

                    # 4. 读取识别结果
                    if os.path.exists(temp_result_path):
                        with open(temp_result_path, 'r', encoding='utf-8') as f:
                            recognized_text = f.read().strip()
                        
                        os.remove(temp_wav_path)
                        os.remove(temp_result_path)
                        
                        if recognized_text:
                            print(f"语音识别结果: '{recognized_text}'，转为对话任务。")
                            dialogue_command = command.copy()
                            dialogue_command['task'] = 'dialogue'
                            dialogue_command['params'] = {'text': recognized_text}
                            return process_task(dialogue_command)
                        else:
                            error_msg = "语音识别结果为空"
                    else:
                        error_msg = "语音识别失败，未生成结果文件"
                except requests.exceptions.RequestException as e:
                    error_msg = f"下载音频文件失败: {e}"
                except Exception as e:
                    error_msg = f"处理音频时发生未知错误: {e}"
        
        elif task_name == 'dialogue':
            user_text = params.get('text')
            if not user_text:
                error_msg = "缺少 text 参数"
            else:
                # 1. 将用户文本写入临时文件
                temp_input_path = os.path.join(RUN_TEMP_DIR, f"dialogue_input_{command_id}.txt")
                with open(temp_input_path, 'w', encoding='utf-8') as f:
                    f.write(user_text)

                # 2. 调用AI对话
                print("正在调用 DeepSeek AI 对话...")
                temp_reply_path = os.path.join(RUN_TEMP_DIR, f"dialogue_reply_{command_id}.txt")
                dialog = DeepSeekDialog(
                    api_key=DEEPSEEK_API_KEY,
                    input_path=temp_input_path,
                    output_path=temp_reply_path
                )
                dialog.get_reply()

                # 3. 读取AI回复
                if os.path.exists(temp_reply_path):
                    with open(temp_reply_path, 'r', encoding='utf-8') as f:
                        ai_reply = f.read().strip()
                    result_data = {'text': ai_reply}
                    # 清理临时文件
                    os.remove(temp_input_path)
                    os.remove(temp_reply_path)
                else:
                    error_msg = "AI对话失败，未生成回复文件"

        elif task_name == 'get_marker_list':
            response = marker_manager.get_marker_list()
            if response and response.get('status') == 'OK':
                result_data = response.get('results', {})
                print(f"成功获取到 {len(result_data)} 个标记点")
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

        elif task_name == 'move_to_point':
            marker_name = params.get('marker_name')
            if not marker_name:
                error_msg = "缺少点位名称参数 'marker_name'"
            else:
                print(f"开始移动到点位: {marker_name}")
                # 连接移动控制器
                if move_controller.connect():
                    try:
                        # 执行移动指令
                        response = move_controller.move_to_marker(marker_name)
                        if response and response.get('status') == 'OK':
                            result_data = {'message': f'成功移动到点位 {marker_name}'}
                            print(f"成功移动到点位: {marker_name}")
                        else:
                            error_msg = response.get('error_message', f'移动到点位 {marker_name} 失败')
                    except Exception as e:
                        error_msg = f"移动过程中发生错误: {str(e)}"
                    finally:
                        move_controller.disconnect()
                else:
                    error_msg = "无法连接到机器人移动控制系统"

        elif task_name == 'record_audio':
            # 1. 生成唯一文件名
            timestamp = int(time.time())
            unique_filename = f"cloned_voice_{timestamp}.wav"
            
            # 2. 录音
            recorder = AudioRecorder(sample_rate=24000)
            output_file = os.path.join(RUN_TEMP_DIR, unique_filename)
            
            print(f"开始录音，时长15秒，保存至 {output_file}")
            recorder.start_recording(output_file=output_file, record_timeout=15)
            
            # 3. 读取文件并进行Base64编码
            try:
                with open(output_file, 'rb') as f:
                    file_content_base64 = base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                error_msg = f"读取录音文件失败: {e}"
            
            # 4. 上传到云存储
            if not error_msg:
                print(f"正在上传录音文件 '{unique_filename}' 到云存储...")
                upload_result = call_unicloud_function('uploadAudio', {
                    'fileName': unique_filename,
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
                TEXT_ID = 5001
                TEXT_SEG_ID = 26  # 对应 "今天天气怎么样"

                res_id = train_and_register_voice(
                    appid=SPARK_APP_ID,
                    apikey=SPARK_API_KEY,
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

        elif task_name == 'get_profiles_config':
            try:
                error_msg = None  # 初始化error_msg变量
                # 修正路径：app_client.py在demos目录下，profiles在demos/data/profiles
                profiles_dir = os.path.join(os.path.dirname(__file__), 'data', 'profiles')
                print(f"[Debug] 查找profiles目录: {profiles_dir}")
                
                if not os.path.exists(profiles_dir):
                    print(f"[Error] profiles目录不存在: {profiles_dir}")
                    # 尝试绝对路径作为备选
                    profiles_dir_abs = "/home/xuanwu/haven_ws/demos/data/profiles"
                    if os.path.exists(profiles_dir_abs):
                        profiles_dir = profiles_dir_abs
                        print(f"[Info] 使用绝对路径: {profiles_dir}")
                    else:
                        error_msg = f"人员档案目录不存在: {profiles_dir}"
                
                if not error_msg:
                    profiles_data = []
                    print(f"[Info] 开始读取profiles目录: {profiles_dir}")
                    # 遍历profiles目录中的所有json文件
                    for filename in os.listdir(profiles_dir):
                        if filename.endswith('_profile.json'):
                            file_path = os.path.join(profiles_dir, filename)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    profile = json.load(f)
                                    # 添加文件名作为标识
                                    profile['profile_id'] = filename.replace('_profile.json', '')
                                    profiles_data.append(profile)
                                    print(f"[Info] 成功读取档案: {filename}")
                            except Exception as file_error:
                                print(f"读取档案文件 {filename} 失败: {file_error}")
                                continue
                    
                    result_data = {'profiles': profiles_data}
                    print(f"成功读取 {len(profiles_data)} 个人员档案。")
            except Exception as e:
                error_msg = f"读取人员档案失败: {e}"
                print(f"[Error] {error_msg}")

        elif task_name == 'update_profile':
            profile_id = params.get('profile_id')
            profile_data = params.get('profile_data')
            
            if not profile_id or not profile_data:
                error_msg = "缺少 'profile_id' 或 'profile_data' 参数"
            else:
                try:
                    error_msg = None  # 初始化error_msg变量
                    # 修正路径：与get_profiles_config保持一致
                    profiles_dir = os.path.join(os.path.dirname(__file__), 'data', 'profiles')
                    if not os.path.exists(profiles_dir):
                        # 尝试绝对路径作为备选
                        profiles_dir_abs = "/home/xuanwu/haven_ws/demos/data/profiles"
                        if os.path.exists(profiles_dir_abs):
                            profiles_dir = profiles_dir_abs
                        else:
                            error_msg = f"人员档案目录不存在: {profiles_dir}"
                            
                    if not error_msg:
                        file_path = os.path.join(profiles_dir, f"{profile_id}_profile.json")
                        
                        # 添加更新时间
                        profile_data['last_interaction'] = time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                        
                        # 写入文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(profile_data, f, ensure_ascii=False, indent=4)
                        
                        print(f"成功更新人员档案: {profile_id}")
                        result_data = {'message': f'成功更新 {profile_id} 的档案'}
                        
                except Exception as e:
                    error_msg = f"更新人员档案失败: {e}"

        elif task_name == 'get_patrol_routes':
            try:
                config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'patrol_routes.json')
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result_data = {'fileContent': content}
                print("成功读取 patrol_routes.json 文件内容。")
            except Exception as e:
                error_msg = f"读取 patrol_routes.json 文件失败: {e}"

        elif task_name == 'save_patrol_route':
            route_data = params.get('route')
            if not route_data:
                error_msg = "缺少 'route' 参数"
            else:
                try:
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'patrol_routes.json')
                    
                    # 读取现有配置文件
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except FileNotFoundError:
                        # 如果文件不存在，创建初始结构
                        config = {"routes": [], "active_route": None}
                    
                    # 添加新路线
                    route_data['id'] = f"route_{len(config['routes']) + 1}"
                    route_data['created_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    config['routes'].append(route_data)
                    
                    # 写回配置文件
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    
                    result_data = {'route_id': route_data['id']}
                    print(f"成功保存巡逻路线: {route_data['name']}")
                    
                except Exception as e:
                    error_msg = f"保存巡逻路线失败: {e}"

        elif task_name == 'start_patrol':
            route_id = params.get('route_id')
            if not route_id:
                error_msg = "缺少 'route_id' 参数"
            else:
                try:
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'patrol_routes.json')
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # 查找指定路线
                    target_route = None
                    for route in config['routes']:
                        if route['id'] == route_id:
                            target_route = route
                            break
                    
                    if not target_route:
                        error_msg = f"找不到路线 ID: {route_id}"
                    else:
                        marker_list = [point['name'] for point in target_route['points']]
                        print(f"开始执行巡逻路线: {target_route['name']}, 点位: {marker_list}")
                        
                        # 连接移动控制器并开始巡逻
                        if move_controller.connect():
                            try:
                                response = move_controller.patrol_markers(marker_list)
                                if response and response.get('status') == 'OK':
                                    result_data = {'message': f'成功开始巡逻路线: {target_route["name"]}'}
                                    print(f"巡逻已启动: {target_route['name']}")
                                else:
                                    error_msg = response.get('error_message', '启动巡逻失败')
                            except Exception as e:
                                error_msg = f"巡逻启动过程中发生错误: {str(e)}"
                            finally:
                                move_controller.disconnect()
                        else:
                            error_msg = "无法连接到机器人移动控制系统"
                            
                except Exception as e:
                    error_msg = f"读取巡逻路线配置失败: {e}"

        elif task_name == 'stop_patrol':
            print("停止当前巡逻任务")
            # 连接移动控制器并停止巡逻
            if move_controller.connect():
                try:
                    response = move_controller.cancel_move()
                    if response and response.get('status') == 'OK':
                        result_data = {'message': '成功停止巡逻'}
                        print("巡逻已停止")
                    else:
                        error_msg = response.get('error_message', '停止巡逻失败')
                except Exception as e:
                    error_msg = f"停止巡逻过程中发生错误: {str(e)}"
                finally:
                    move_controller.disconnect()
            else:
                error_msg = "无法连接到机器人移动控制系统"

        else:
            error_msg = f"未知的任务名称: {task_name}"

        # 根据执行结果更新状态
        if error_msg:
            update_command_status(command_id, "failed", error_message=error_msg)
        else:
            update_command_status(command_id, "completed", result=result_data)
            print("[Success] 任务执行成功。")

    except Exception as e:
        print(f"[FATAL] 任务处理时发生严重错误: {e}")
        update_command_status(command_id, "failed", error_message=str(e))
    finally:
        # 如果连接了机器人才断开
        if task_name in robot_tasks:
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
