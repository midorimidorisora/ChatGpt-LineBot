from flask import Flask, request, abort, jsonify ,json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from api.chatgpt import ChatGPT
from os.path import join
import os ,platform

if os.name == 'nt':
    with open('data/key.json', 'r',encoding="utf-8") as file:
        data = json.load(file)

    line_bot_api =data["LINE_CHANNEL_ACCESS_TOKEN"]
    line_handler =data["LINE_CHANNEL_SECRET"]
else:
    line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))



working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/')
def home():
    return json.loads(getSystemInfo())

@app.route('/api')
def api():
    with open('data/cmdlist.json', mode='r') as my_file:
        text = my_file.read()
        return jsonify(text)

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    
    if event.message.type != "text":
        return

    with open('data/cmdlist.json', 'r',encoding="utf-8") as file:
        data = json.load(file)
    print(data)

    if event.message.text in data :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=data[event.message.text]))
        return

    if event.message.text == "安靜":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝您的使用，若需要我的服務，請跟我說 「啟動」 謝謝~"))
        return
    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="chatgpt 目前可以為您服務囉~"))
        return
    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))

def getSystemInfo():
    
        info={}
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['processor']=platform.processor()
        return json.dumps(info)


if __name__ == "__main__":
    app.run()
