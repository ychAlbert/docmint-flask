import requests
import json
import time


def request_and_save_image(text, access_token):
    # 图片生成请求函数
    def request_img_generation(text, access_token):
        url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2img"
        params = {"access_token": access_token}
        payload = json.dumps({"text": text, "resolution": "1024*1024", "style": "写实风格"})
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(url, params=params, headers=headers, data=payload)
        return response.json() if response.status_code == 200 else None

    # 通过taskId获取图片的函数
    def get_img_from_baidu(taskId, access_token):
        url = f"https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImg"
        params = {"access_token": access_token}
        payload = json.dumps({"taskId": taskId})
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, params=params, headers=headers, data=payload)
        return response.json() if response.status_code == 200 else None

    # 提交图片生成请求
    response_data = request_img_generation(text, access_token)

    if response_data and 'data' in response_data and 'taskId' in response_data['data']:
        taskId = response_data['data']['taskId']
        print(f"图片生成任务提交成功，taskId: {taskId}")

        # 模拟简单等待时间，等待图片生成完成，时间可根据实际情况调整
        print("等待图片生成...")
        time.sleep(10)  # 延时等待图片生成

        # 获取生成的图片信息
        img_response_data = get_img_from_baidu(taskId, access_token)
        if img_response_data and 'data' in img_response_data and 'img' in img_response_data['data']:
            img_url = img_response_data['data']['img']

            if img_url:
                # 下载并保存图片
                img_data = requests.get(img_url)
                if img_data.status_code == 200:
                    filename = img_url.split('/')[-1].split('?')[0]  # 删除URL参数

                    with open(filename, 'wb') as file:
                        file.write(img_data.content)
                    print(f"图片已保存为: {filename}")
                else:
                    print(f"获取图片失败，状态码: {img_data.status_code}")
            else:
                print("未找到图片URL")
        else:
            print("获取taskId生成的图片失败")
    else:
        print("图片生成任务提交失败")


# 使用示例
access_token = "24.1de471b4316c4c7215bf320dc7cf58c9.2592000.1719315406.282335-73535109"  # 替换为你的access_token
request_and_save_image("猫", access_token)