from flask import Flask, request, abort, jsonify ,json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage ,TemplateSendMessage, ButtonsTemplate ,PostbackEvent
from api.weather import Weather
from api.chatgpt import ChatGPT
from os.path import join
import os ,platform

if os.name == 'nt':
    with open('data/key.json', 'r',encoding="utf-8") as file:
        data = json.load(file)

    line_bot_api =LineBotApi(data["LINE_CHANNEL_ACCESS_TOKEN"])
    line_handler =WebhookHandler(data["LINE_CHANNEL_SECRET"])
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

@app.route('/api/v1/sysinfo')
def sysinfo_get():
    with open('data/sysinfo.json', mode='r') as my_file:
        text = my_file.read()
        return jsonify(text)
    
@app.route('/api/v1/sysinfo', methods=['POST'])
def sysinfo_post():
    output = request.get_json()
    
    with open('data/sysinfo.json', 'w') as f:
        json.dump(data, f)
    return jsonify({'message': 'JSON file written successfully'})


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
        if event.message.text == "安靜" or event.message.text == "quiet":
            working_status = False
        else:
            working_status = True
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=data[event.message.text]))
        return

    # if event.message.text == "安靜":
    #     working_status = False
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text="啟用chatgpt服務，請跟我說 「啟動」 謝謝~"))
    #     return
    # if event.message.text == "啟動":
    #     working_status = True
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text="chatgpt 目前可以為您服務囉~"))
    #     return
    
    if event.message.text == 'menu':
        line_bot_api.reply_message(event.reply_token, make_select_message())
        return
    
    if event.message.text == 'weather':
        line_bot_api.reply_message(event.reply_token, Weather.get_data("臺南"))
        return
    
    

    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))
        

@line_handler.add(PostbackEvent)
def on_postback(line_event):
    data = line_event.postback.data
    line_bot_api.reply_message(line_event.reply_token, TextSendMessage("{0}を選択しましたね！".format(data)))


def getSystemInfo():    
        info={}
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['processor']=platform.processor()
        return json.dumps(info)

def make_select_message():
    return TemplateSendMessage(
        alt_text="選択肢",
        template=ButtonsTemplate(
            title="選択肢のテスト",
            text="下から1つ選んでね！",
            actions=[
                {
                    "type": "postback",
                    "data": "morning",
                    "label": "朝"
                },
                {
                    "type": "postback",
                    "data": "noon",
                    "label": "昼"
                },
                {
                    "type": "postback",
                    "data": "night",
                    "label": "夜"
                }
            ]
        )
    )

if __name__ == "__main__":
    app.run()
