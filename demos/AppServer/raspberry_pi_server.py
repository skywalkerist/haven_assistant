import requests
import time
import json

# --- 配置区 ---
# 请将这里替换成你的uniCloud服务空间的URL化域名
# 格式为: https://xxxxxxxx.next.bspapp.com
UNICLOUD_BASE_URL = "https://fc-mp-503540be-00e4-400c-86f1-957c9c805a91.next.bspapp.com"
# 轮询间隔（秒）
POLL_INTERVAL = 5

# --- 函数定义区 ---

def call_unicloud_function(function_name, data={}):
    """
    调用指定的uniCloud云函数
    """
    url = f"{UNICLOUD_BASE_URL}/{function_name}"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        response.raise_for_status()  # 如果HTTP状态码是4xx或5xx，则抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"调用云函数 {function_name} 时发生网络错误: {e}")
        return None

def process_task(task):
    """
    处理从云端获取的任务
    """
    message_id = task['id']
    content = task['content']
    
    print(f"--- [新任务] ---")
    print(f"  ID: {message_id}")
    print(f"  内容: {content}")
    
    # 在这里执行你的树莓派硬件操作，比如控制GPIO等
    # ...
    
    # 准备回复内容
    reply_text = "树莓派收到"
    print(f"  回复: {reply_text}")
    
    # 调用云函数，将结果写回数据库
    print("  正在将结果同步到云端...")
    update_result = call_unicloud_function('updateMessageStatus', {
        'messageId': message_id,
        'reply': reply_text
    })
    
    if update_result and update_result.get('success'):
        print("  [成功] 结果已同步至云端。")
    else:
        print("  [失败] 结果同步失败。")
    print("-----------------")

# --- 主循环 ---

if __name__ == '__main__':
    print("树莓派客户端已启动，开始轮询云端任务...")
    while True:
        try:
            print(f"\n正在查询新任务... ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            result = call_unicloud_function('getPendingMessage')
            
            if result and result.get('success'):
                if result.get('taskFound'):
                    process_task(result['message'])
                else:
                    print("没有待处理的任务。")
            else:
                print("从云端获取任务失败，请检查网络或云函数日志。")

            # 等待指定时间后再次轮询
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n程序已停止。")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")
            time.sleep(POLL_INTERVAL * 2) # 发生错误时，等待更长时间
