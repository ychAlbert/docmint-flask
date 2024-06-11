import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from ratelimit import limits, sleep_and_retry
from wenxin_ori import Wenxin_LLM  # 假设文心一言的库名为wenxin
from datetime import timedelta

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求



def ratelimit_key(ip):
    return f"novel_ratelimit_{ip}"

@limits(calls=50, period=timedelta(days=1))
@sleep_and_retry
@app.route('/generate', methods=['POST'])
def generate_text():
    if not os.getenv("ERNIE_BOT_ACCESS_TOKEN"):
        return jsonify({"error": "缺少 ERNIE_BOT_ACCESS_TOKEN - 请确保已将其添加到您的 .env 文件中"}), 400


    data = request.get_json()
    prompt = data.get('prompt')
    option = data.get('option')
    command = data.get('command')

    messages = match(option, prompt, command)

    combined_request = format_messages(messages)

    try:
        wenxin = Wenxin_LLM(access_token=os.getenv("ERNIE_BOT_ACCESS_TOKEN"))
        result = wenxin._call(combined_request)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return result

def match(option, prompt, command):
    if option == "continue":
        return ["你是一名AI写作助手，根据已有的文本继续写作。优先从后面的字符开始，限制在200字符内，确保句子完整。适当时使用Markdown格式。", prompt]
    elif option == "improve":
        return ["你是一名AI写作助手，改进已有文本。限制在200字符内，确保句子完整。适当时使用Markdown格式。", f"现有文本是：{prompt}"]
    elif option == "shorter":
        return ["你是一名AI写作助手，缩短已有文本。适当时使用Markdown格式。", f"现有文本是：{prompt}"]
    elif option == "longer":
        return ["你是一名AI写作助手，延长已有文本。适当时使用Markdown格式。", f"现有文本是：{prompt}"]
    elif option == "fix":
        return ["你是一名AI写作助手，修正文本中的语法和拼写错误。限制在200字符内，确保句子完整。适当时使用Markdown格式。", f"现有文本是：{prompt}"]
    elif option == "zap":
        return ["你是一名AI写作助手，根据给定的prompt生成文本。接受用户输入和操作命令，适当时使用Markdown格式。", f"对于这个文本：{prompt}。你需要遵循的命令是：{command}"]
    else:
        return []

def format_messages(messages):
    system_message, user_message = messages
    formatting_request = system_message + ":"
    combined_request = formatting_request + "\n\n" + user_message
    return combined_request


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
