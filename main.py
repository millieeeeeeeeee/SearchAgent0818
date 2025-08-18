"""#LineBot + SearchAgent + FlexMessage"""
from urllib.parse import parse_qs
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
    FlexMessage, FlexContainer
)
from linebot.v3.messaging import MessagingApi, MessagingApiBlob, RichMenuRequest, RichMenuArea, RichMenuSize, RichMenuBounds, PostbackAction
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent ,FollowEvent

#package
from utils.agent import *
from utils.user_message import *
from utils.setting_datetime import *
from utils.sheetdata import *
from utils.richmenu_UL_function import *
from utils.richmenu_UM_function import *
from utils.richmenu_UR_function import *
from utils.setting_richmenu import *


app = Flask(__name__)
#varible
import config
access_token = config.access_token
secret = config.secret

#20250804_test
# 初始化 Flask


# 初始化 Messaging API 和 handler
configuration = Configuration(access_token=access_token)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(secret)
blob_api = MessagingApiBlob(api_client)

create_richmenu_for_three()

# 📬 Webhook 接收路由
@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook 處理錯誤：", e)
        abort(400)

    return "OK"

# 🟢 處理第一次加好友（FollowEvent）
@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = hello()
    guide_msg = help()
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text=welcome_msg),
                TextMessage(text=guide_msg)
            ]
        )
    )

# 🟦 處理文字訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    question = event.message.text
    reply = help()
    messaging_api.reply_message(
      ReplyMessageRequest(
          reply_token=event.reply_token,
          messages=[TextMessage(text=str(reply))]
              )
    )

# 🟨 處理 Postback（例如 datetimepicker 或按鈕）
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    print(f"收到 postback：{data}")

    data_dict = {k: v[0] for k, v in parse_qs(data).items()}

    try:
        reply = handle_richmenu_session(event, data_dict)
    except Exception as e:
        reply = TextMessage(text=f"❌ 發生錯誤：{e}")

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply]
        )
    )
