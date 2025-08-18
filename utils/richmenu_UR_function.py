"""UR庫存查詢"""
import json
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
    FlexMessage, FlexContainer
)
from utils.sheetdata import *


def UR_get_branch_selector():
    branches = ["台北中山店", "台中西屯店", "台南中西區店"]

    buttons = []
    for branch in branches:
        buttons.append({
            "type": "button",
            "action": {
                "type": "postback",
                "label": branch,
                "data": f"session=UR&step=show_result&branch={branch}"
            }
        })

    flex_content = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#A1C7E0",
            "contents": [
                {
                    "type": "text",
                    "text": "📍 請選擇分店",
                    "align": "center",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#000000"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": buttons
        }
    }

    flex_json_str = json.dumps(flex_content)
    flex_container = FlexContainer.from_json(flex_json_str)

    return FlexMessage(
        alt_text="請選擇分店",
        contents=flex_container
    )

def UR_detail_list(branch):
    df = df3()
    merged=df[["商品名稱",branch,"總部"]]

    #目前假設為2024-09-01，之後可更換
    #today = datetime.now().strftime("%Y-%m-%d")
    today = datetime(2024, 9, 1).strftime("%Y-%m-%d")

    # Header row
    contents = [
        {
            "type": "box",
            "layout": "baseline",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "商品", "weight": "bold", "flex": 3, "size": "sm"},
                {"type": "text", "text": branch, "weight": "bold", "flex": 3, "size": "sm", "align": "center"},
                {"type": "text", "text": "總部", "weight": "bold", "flex": 2, "size": "sm", "align": "center"},
            ]
        }
    ]

    # 資料列
    for _, row in merged.iterrows():
        contents.append({
            "type": "box",
            "layout": "baseline",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": str(row["商品名稱"]), "flex": 3, "size": "sm"},
                {"type": "text", "text": str(row[branch]), "flex": 3, "size": "sm", "align": "center"},
                {"type": "text", "text": str(row["總部"]), "flex": 2, "size": "sm", "align": "center"},
            ]
        })

    # 建立 bubble 結構
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#4F9D9D",
            "contents": [
                {"type": "text", "text": f"{today}｜商品庫存", "weight": "bold", "color": "#ffffff", "align": "center"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": contents
        }
    }

    # 封裝成 Flex Message
    flex_json_str = json.dumps(bubble)
    flex_container = FlexContainer.from_json(flex_json_str)

    return FlexMessage(
        alt_text=f"{today}｜{branch} 商品庫存",
        contents=flex_container
    )
