# 语音转文字

# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import pyaudio
import time
import websocket


# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280  # 或者可以根据实际需求调整
    end_tag = "<end_of_stream>"
    audio = pyaudio.PyAudio()

    def __init__(self):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self):
        # 开启麦克风录音
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, input=True,
                                 frames_per_buffer=self.CHUNK)

        print("Streaming started...")

        try:
            while True:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.ws.send(data)

                # 睡眠一小段时间以模拟音频数据流的实时性
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Streaming stopped")

        finally:
            # 发送结束标志
            self.ws.send(bytes(self.end_tag.encode('utf-8')))
            print("Send end tag success")

            # 停止录音
            stream.stop_stream()
            stream.close()

        # 关闭websocket连接
        self.ws.close()

        # 终止PyAudio会话
        self.audio.terminate()

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    # 先解析result_dict["data"]这一层字符串型JSON数据
                    data_dict = json.loads(result_dict["data"])
                    words = []
                    # 现在我们可以遍历data_dict中的词组来获取真正的文本内容
                    for ws in data_dict["cn"]["st"]["rt"][0]["ws"]:
                        for cw in ws["cw"]:
                            words.append(cw["w"])
                    sentence = ''.join(words)
                    print("Recognition result: " + sentence)  # 打印语音识别结果文本内容

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")


if __name__ == '__main__':
    logging.basicConfig()

    app_id = "76846f38"
    api_key = "937bf8b18367aa489483aa5f2aea14c5"

    client = Client()
    client.send()
