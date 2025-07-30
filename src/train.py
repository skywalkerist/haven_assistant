import json
import time
import requests
import hashlib
import sys
from requests_toolbelt.multipart.encoder import MultipartEncoder
from voice_cloner import VoiceManager # 导入我们之前创建的管理器

# --- 鉴权函数 (保持不变) ---
def getAuthorization(appId, apikey,timeStamp,data):
    body = json.dumps(data)
    keySign = hashlib.md5((apikey + str(timeStamp)).encode('utf-8')).hexdigest()
    sign = hashlib.md5((keySign + body).encode("utf-8")).hexdigest()
    return sign

def getToken(appid,apikey):
    timeStamp = int(time.time() * 1000)
    body = {"base":{"appid": appid ,"version":"v1","timestamp": str(timeStamp)},"model":"remote"}
    headers = {}
    headers['Authorization'] = getAuthorization(appid,apikey,timeStamp,body)
    headers['Content-Type'] = 'application/json'
    response = requests.post(url='http://avatar-hci.xfyousheng.com/aiauth/v1/token', data= json.dumps(body),headers= headers).text
    resp = json.loads(response)
    if ('000000' == resp['retcode']):
        return resp['accesstoken']
    return None

# --- VoiceTrain 类 (基本保持不变) ---
class VoiceTrain(object):
    def __init__(self,appid,apikey):
        self.appid = appid
        self.apikey = apikey
        self.token = getToken(appid,apikey)
        if not self.token:
            raise Exception("获取Token失败，请检查appid和apikey。")
        self.time = int(time.time()* 1000)
        self.taskId = ''

    def getSign(self,body):
        keySign = hashlib.md5((str(body)).encode('utf-8')).hexdigest()
        sign = hashlib.md5((self.apikey+ str(self.time) + keySign).encode("utf-8")).hexdigest()
        return sign

    def getheader(self,sign):
        return {"X-Sign":sign,"X-Token":self.token,"X-AppId":self.appid,"X-Time":str(self.time)}

    def getText(self):
        textid = 5001
        body = {"textId":textid}
        sign = self.getSign(body)
        headers =self.getheader(sign)
        response = requests.post(url ='http://opentrain.xfyousheng.com/voice_train/task/traintext',json= body,headers=headers).json()
        print("请使用以下官方文本录音，然后进行训练：")
        textlist= response['data']['textSegs']
        for line in textlist:
            print(f"  ID: {line['segId']}, 文本: {line['segText']}")

    def createTask(self, voice_name):
        body={
            "taskName": f"task_{voice_name}_{int(time.time())}",
            "sex" :1,
            "resourceType":12,
            "resourceName" : f"voice_{voice_name}",
            "language":"cn",
        }
        sign = self.getSign(body)
        headers = self.getheader(sign)
        response = requests.post(url ='http://opentrain.xfyousheng.com/voice_train/task/add',json= body,headers=headers).text
        resp = json.loads(response)
        print("创建任务：",resp)
        self.taskId = resp.get('data')
        return self.taskId

    def addAudio(self,audiourl,textId,textSegId):
        if not self.taskId:
            print("❌ 错误: 必须先创建任务(createTask)。")
            return
        body ={
            "taskId":self.taskId,
            "audioUrl": audiourl,
            "textId": textId,
            "textSegId": textSegId
        }
        sign = self.getSign(body)
        headers = self.getheader(sign)
        response = requests.post(url='http://opentrain.xfyousheng.com/voice_train/audio/v1/add', json=body, headers=headers).text
        print(f"添加音频(URL)响应: {response}")

    def submitTask(self):
        body ={"taskId" :self.taskId}
        sign = self.getSign(body)
        headers = self.getheader(sign)
        response = requests.post(url='http://opentrain.xfyousheng.com/voice_train/task/submit', json=body, headers=headers).text
        print(f"提交任务响应: {response}")

    def getProcess(self):
        body = {"taskId": self.taskId}
        sign = self.getSign(body)
        headers = self.getheader(sign)
        response = requests.post(url='http://opentrain.xfyousheng.com/voice_train/task/result', json=body, headers=headers).text
        return json.loads(response)

# --- 新的封装函数 ---
def train_and_register_voice(appid, apikey, voice_name, audio_url, text_id, text_seg_id):
    """
    执行声音训练并自动注册到配置文件中。

    :param appid: 你的AppID
    :param apikey: 你的APIKey
    :param voice_name: 要为这个新声音起的名字 (例如 'xuanwu')
    :param audio_url: 用于训练的音频文件的公开URL
    :param text_id: 官方训练文本集ID
    :param text_seg_id: 录音内容对应的文本段落ID
    :return: 成功则返回新的 res_id，失败则返回 None
    """
    try:
        print(f"--- 开始为 '{voice_name}' 训练新的声音模型 ---")
        voiceTrain = VoiceTrain(appid, apikey)

        # 1. 创建任务
        if not voiceTrain.createTask(voice_name):
            print("❌ 创建训练任务失败。")
            return None
        
        # 2. 添加音频
        voiceTrain.addAudio(audio_url, textId=text_id, textSegId=text_seg_id)

        # 3. 提交任务
        voiceTrain.submitTask()

        # 4. 轮询结果
        print("--- 任务已提交，开始轮询训练结果... ---")
        while True:
            time.sleep(10) # 每10秒查询一次
            resp = voiceTrain.getProcess()
            status = resp.get('data', {}).get('trainStatus')

            if status == -1:
                print("还在训练中，请等待......")
                continue
            
            if status == 1:
                new_res_id = resp['data']['assetId']
                print(f"✅ 训练成功！")
                print(f"  音库名称: '{voice_name}'")
                print(f"  音库ID(res_id): {new_res_id}")

                # 自动注册到配置文件
                print("  正在自动注册到音色库...")
                manager = VoiceManager(config_file='../config/voices.json')
                manager.add_voice(voice_name, new_res_id)
                
                return new_res_id
            
            if status == 0:
                print("❌ 训练失败。")
                print(f"  任务ID: {voiceTrain.taskId}")
                print(f"  失败原因: {resp.get('desc')}")
                return None
            
            # 防止意外的status值导致死循环
            if status not in [-1, 1, 0]:
                print(f"❌ 未知的训练状态: {status}，程序终止。")
                return None

    except Exception as e:
        print(f"执行训练时发生严重错误: {e}")
        return None


# --- 主程序入口 ---
if __name__ == '__main__':
    # 从命令行获取参数，或者使用默认值
    # 用法: python train.py <voice_name> <audio_url>
    if len(sys.argv) < 3:
        print("--- 使用默认参数进行测试 ---")
        voice_name_to_train = 'xuanwu_test'
        # 请确保这个URL是公开可访问的WAV文件
        audio_url_to_train = 'https://mp-503540be-00e4-400c-86f1-957c9c805a91.cdn.bspapp.com/audio-cloning/cloned_voice.wav'
    else:
        voice_name_to_train = sys.argv[1]
        audio_url_to_train = sys.argv[2]

    # 在这里填入你的认证信息
    APPID = 'b32f165e'
    APIKEY = 'bf4caffa0bd087acc04cd63d0ee27fc5'
    
    # 使用官方通用文本集，ID为5001，我们用第26段 "今天天气怎么样"
    TEXT_ID = 5001
    TEXT_SEG_ID = 26

    # 调用封装好的函数
    train_and_register_voice(
        appid=APPID,
        apikey=APIKEY,
        voice_name=voice_name_to_train,
        audio_url=audio_url_to_train,
        text_id=TEXT_ID,
        text_seg_id=TEXT_SEG_ID
    )
