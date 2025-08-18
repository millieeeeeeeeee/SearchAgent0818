"""UM日期查詢"""
import json
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
    FlexMessage, FlexContainer
)
from utils.sheetdata import *


def get_date_selector():
    flex_content = {
        "type": "bubble",
        "header": {
          "type": "box",
          "layout": "vertical",
          "backgroundColor": "#A1C7E0",
          "contents": [
            {
              "type": "text",
              "text": "日期查詢",
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
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "datetimepicker",
                "label": "選擇日期",
                "data": "session=UM&step=show_result",
                "mode": "date",
                "max": "2024-08-31",
                "min": "2024-07-01"
              }
            }
          ]
        }
      }

    flex_json_str = json.dumps(flex_content)
    flex_container = FlexContainer.from_json(flex_json_str)

    return FlexMessage(
        alt_text="請選擇日期",
        contents=flex_container
    )

def UM_get_date_selector():
    flex_content = {
      "type": "bubble",
      "header": {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": "#A1C7E0",
        "contents": [
          {
            "type": "text",
            "text": "日期查詢",
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
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "上週",
              "data": "session=UM&step=last_week_show_result"
            }
          },
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "上月",
              "data": "session=UM&step=last_month_show_result"
            }
          },
          {
            "type": "button",
            "action": {
              "type": "datetimepicker",
              "label": "選擇日期",
              "data": "session=UM&step=one_day_show_result",
              "mode": "date",
              "max": "2024-08-31",
              "min": "2024-07-01"
            }
          }
        ]
      }
    }

    flex_json_str = json.dumps(flex_content)
    flex_container = FlexContainer.from_json(flex_json_str)

    return FlexMessage(
        alt_text="請選擇日期",
        contents=flex_container
    )

def UM_days_detail_list(start, end):
    df=merged_df()
    matched = df[["日期", "分店", "營業額"]]
    matched = matched[(matched["日期"] >= start) & (matched["日期"] <= end)]
    normal_rows = matched.drop_duplicates()
    original_order = normal_rows["分店"].drop_duplicates().tolist()
    normal_rows = normal_rows.groupby("分店", as_index=False)["營業額"].sum()
    normal_rows = normal_rows.set_index("分店").loc[original_order].reset_index()
    hq_row = pd.DataFrame([{
        "分店": "總計",
        "營業額": normal_rows["營業額"].sum()
        }])

    # 日期文字顯示範圍
    start=start.strftime('%Y-%m-%d')
    end=end.strftime('%Y-%m-%d')
    date_range = f"{start} ~ {end}"

    # 第一行：表頭
    contents = [{
        "type": "box",
        "layout": "baseline",
        "contents": [
            {"type": "text", "text": "分店", "align": "center", "color": "#aaaaaa"},
            {"type": "text", "text": "營業額", "align": "center", "color": "#aaaaaa"}
        ]
    }]

    # 加入各分店資料
    for _, row in normal_rows.iterrows():
        contents.append({
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": row["分店"], "align": "center"},
                {"type": "text", "text": f"${(row['營業額']):,}", "align": "center"}
            ],
            "margin": "sm"
        })

    # 加入分隔線 + 總部資料
    if not hq_row.empty:
        hq = hq_row.iloc[0]
        contents.append({
            "type": "separator",
            "color": "#000000",
            "margin": "md"
        })
        contents.append({
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": hq["分店"], "align": "center"},
                {"type": "text", "text": f"${(hq['營業額']):,}", "align": "center"}
            ],
            "margin": "md"
        })

    # 組合 Flex Bubble
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#4F9D9D",
            "contents": [
                {
                    "type": "text",
                    "text": date_range,
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
            "contents": contents
        }
    }

    # 轉為 FlexMessage
    flex_json_str = json.dumps(bubble, ensure_ascii=False)
    flex_container = FlexContainer.from_json(flex_json_str)

    return FlexMessage(
        alt_text=f"{date_range} 各分店營業額",
        contents=flex_container
    )

def UM_one_day_detail_list(date):
    df=merged_df()
    matched = df[["日期", "分店", "營業額"]]
    normal_rows = matched[matched["日期"] == date].drop_duplicates(subset=["分店"])
    revenue=matched["營業額"].sum()
    hq_row = pd.DataFrame([{
        "分店": "總計",
        "營業額": normal_rows["營業額"].sum()
        }])

    # 第一行：表頭
    contents = [{
        "type": "box",
        "layout": "baseline",
        "contents": [
            {"type": "text", "text": "分店", "align": "center", "color": "#aaaaaa"},
            {"type": "text", "text": "營業額", "align": "center", "color": "#aaaaaa"}
        ]
    }]

    # 加入各分店資料
    for _, row in normal_rows.iterrows():
        contents.append({
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": row["分店"], "align": "center"},
                {"type": "text", "text": f"${(row['營業額']):,}", "align": "center"}
            ],
            "margin": "sm"
        })

    # 加入分隔線 + 總部資料
    if not hq_row.empty:
        hq = hq_row.iloc[0]
        contents.append({
            "type": "separator",
            "color": "#000000",
            "margin": "md"
        })
        contents.append({
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": hq["分店"], "align": "center"},
                {"type": "text", "text": f"${(hq['營業額']):,}", "align": "center"}
            ],
            "margin": "md"
        })

    # 組合 Flex Bubble
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#4F9D9D",
            "contents": [
                {
                    "type": "text",
                    "text": date,
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
            "contents": contents
        }
    }

    # 轉為 FlexMessage
    flex_json_str = json.dumps(bubble, ensure_ascii=False)
    flex_container = FlexContainer.from_json(flex_json_str)

    return FlexMessage(
        alt_text=f"{date} 各分店營業額",
        contents=flex_container
    )