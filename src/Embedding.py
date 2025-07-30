# encoding: UTF-8

import time
import requests
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import pickle
import json
import chardet
import numpy as np


## 本demo中调用embedding服务,对应两个方法：
#   方法区分通过body中的domain参数值控制的
#       query：将用户问题转换为向量数组
#       para：将知识库内容转换为向量数组


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# 生成鉴权url
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    # print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    # print(signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    # print(authorization_origin)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)


def get_Body(appid,text,style):
    org_content = json.dumps(text).encode('utf-8')
    # print(org_content)

    body= {
    "header": {
        "app_id": appid,
        "uid": "39769795890",
        "status": 3
    },
    "parameter": {
        "emb": {
            "domain": style ,
            "feature": {
                "encoding": "utf8"
            }
        }
    },
    "payload": {
        "messages": {
            "text": base64.b64encode(json.dumps(text).encode('utf-8')).decode()
        }
    }
    }
    # print(body)
    return body



# 发起请求并返回结果
def get_embq_embedding(text,appid,apikey,apisecret):
    host = 'https://emb-cn-huabei-1.xf-yun.com/'
    url = assemble_ws_auth_url(host,method='POST',api_key=apikey,api_secret=apisecret)
    content = get_Body(appid,text,"query")
    print(time.time())
    response = requests.post(url,json=content,headers={'content-type': "application/json"}).text
    print(time.time())
    return response


def get_embp_embedding(text,appid,apikey,apisecret):
    host = 'https://emb-cn-huabei-1.xf-yun.com/'
    url = assemble_ws_auth_url(host,method='POST',api_key=apikey,api_secret=apisecret)
    content = get_Body(appid,text,"para")
    print(time.time())
    response = requests.post(url,json=content,headers={'content-type': "application/json"}).text
    print(time.time())
    return response

# 解析结果并输出
def parser_Message(message):
    data = json.loads(message)
    # print("data" + str(message))
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
    else:
        sid = data['header']['sid']
        # print("本次会话的id为：" + sid)
        text_base = data["payload"]["feature"]["text"]
        # 使用base64.b64decode()函数将text_base解码为字节串text_data
        text_data = base64.b64decode(text_base)
        # 创建一个np.float32类型的数据类型对象dt，表示32位浮点数。
        dt = np.dtype(np.float32)
        # 使用newbyteorder()方法将dt的字节序设置为小端（"<"）
        dt = dt.newbyteorder("<")
        # 使用np.frombuffer()函数将text_data转换为浮点数数组text，数据类型为dt。
        text = np.frombuffer(text_data, dtype=dt)

        # # 打印向量维度
        # print(len(text))

        print("返回的向量化数组为:")
        # print(text)
        return text


if __name__ == '__main__':
    #运行前请配置以下鉴权三要素，获取途径：https://console.xfyun.cn/services/bm3
    APPID ='b32f165e'
    APISecret = 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0'
    APIKEY = 'bf4caffa0bd087acc04cd63d0ee27fc5'
    desc = {"messages":[{"content":"这段话的内容变成向量化是什么样的","role":"user"}]}
    # 当上传文档时 ，需要将文本切分为多块，然后将切分的chunk 填充到上面的content中
    # get_embp_embedding   是将文本、知识库内容进行向量化的服务
    res = get_embp_embedding(desc,appid=APPID,apikey=APIKEY,apisecret=APISecret)

    # ques ={"messages":[{"content":"这段话的内容变成向量化是什么样的","role":"user"}]}
    # #get_embq_embedding   是将用户问题进行向量化的服务
    # res = get_embq_embedding(text=ques,appid=APPID,apikey=APIKEY,apisecret=APISecret)
    # print(res)
    parser_Message(res)
