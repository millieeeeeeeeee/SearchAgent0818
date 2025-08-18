"""UL分店查詢"""
import json
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
    FlexMessage, FlexContainer
)
from utils.sheetdata import *


def UL_get_branch_selector():
    branches = ["台北中山店", "台中西屯店", "台南中西區店", "全部"]

    buttons = []
    for branch in branches:
        buttons.append({
            "type": "button",
            "action": {
                "type": "postback",
                "label": branch,
                "data": f"session=UL&step=select_date&branch={branch}"
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

def UL_get_date_selector(branch):
    flex_content = {
      "type": "bubble",
      "header": {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": "#A1C7E0",
        "contents": [
          {
            "type": "text",
            "text": f"{branch}",
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
              "data": f"session=UL&step=last_week_show_result&branch={branch}"
            }
          },
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "上月",
              "data": f"session=UL&step=last_month_show_result&branch={branch}"
            }
          },
          {
            "type": "button",
            "action": {
              "type": "datetimepicker",
              "label": "選擇日期",
              "data": f"session=UL&step=one_day_show_result&branch={branch}",
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

def UL_query_branch_data(branch, date):
    return f"✅ 成功查詢！\n分店：{branch}\n日期：{date}"

def UL_days_detail_list(branch, start, end):
    df = merged_df()
    matched = df[(df["日期"] >= start) & (df["日期"] <= end)]

    if branch == "全部":
        filtered = matched.copy()
    else:
        filtered = matched[matched["分店"] == branch]

    # 銷售量總和（依商品）
    original_order = filtered["商品名稱"].drop_duplicates().tolist()
    sales_summary = filtered.groupby("商品名稱", as_index=False)["銷售量"].sum()
    sales_summary = sales_summary.set_index("商品名稱").loc[original_order].reset_index()

    # 營業額總和
    if branch == "全部":
        revenue_df = filtered.drop_duplicates(subset=["分店", "日期"])
        revenue = revenue_df["營業額"].sum()
    else:
        revenue = filtered["營業額"].sum()

    # 商品資料列（每列一個 Box）
    product_boxes = []
    for _, row in sales_summary.iterrows():
        product_boxes.append({
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": row["商品名稱"], "color": "#aaaaaa", "size": "sm", "align": "start"},
                {"type": "text", "text": str(row["銷售量"]), "color": "#666666", "size": "sm", "align": "center"},
            ]
        })

    # 日期文字顯示範圍
    start=start.strftime('%Y-%m-%d')
    end=end.strftime('%Y-%m-%d')
    date_range = f"{start} ~ {end}"

    # Bubble 結構
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": branch,
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "flex": 2
                }
            ],
            "margin": "lg",
            "spacing": "lg",
            "backgroundColor": "#4F9D9D"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "text",
                            "text": date_range,
                            "weight": "bold",
                            "size": "lg",
                            "align": "start"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": "營業額", "size": "md"},
                        {"type": "text", "text": f"${revenue:,}", "align": "start"}
                    ],
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "xs",
                    "spacing": "sm",
                    "contents": [
                        {"type": "separator"},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "產品", "align": "start"},
                                {"type": "text", "text": "銷售量", "align": "center"}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": product_boxes
                        }
                    ]
                }
            ]
        }
    }

    return FlexMessage(
        alt_text=f"{branch} {date_range} 銷售報告",
        contents=FlexContainer.from_json(json.dumps(bubble))
    )

def UL_one_day_detail_list(branch, date):
    if branch == "全部":
      df=merged_df()
      matched=df[df["日期"] == date]
      original_order = matched["商品名稱"].drop_duplicates().tolist()
      matched = matched.groupby("商品名稱", as_index=False)["銷售量"].sum()
      matched = matched.set_index("商品名稱").loc[original_order].reset_index()

      revenue_df=df[df["日期"] == date].drop_duplicates(subset=["分店"])
      revenue = revenue_df["營業額"].sum()
    else:
      df=merged_df()
      matched = df[(df["分店"] == branch) & (df["日期"] == date)]
      revenue = matched["營業額"].iloc[0]

    # 商品資料列（每列一個 Box）
    product_boxes = []
    for _, row in matched.iterrows():
        product_boxes.append({
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": row["商品名稱"], "color": "#aaaaaa", "size": "sm", "align": "start"},
                {"type": "text", "text": str(row["銷售量"]), "color": "#666666", "size": "sm", "align": "center"},
            ]
        })

    # Bubble 結構
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": branch,
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "flex": 2
                }
            ],
            "margin": "lg",
            "spacing": "lg",
            "backgroundColor": "#4F9D9D"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "text",
                            "text": date,
                            "weight": "bold",
                            "size": "lg",
                            "align": "start"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": "營業額", "size": "md"},
                        {"type": "text", "text": f"${revenue:,}", "align": "start"}
                    ],
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "xs",
                    "spacing": "sm",
                    "contents": [
                        {"type": "separator"},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "產品", "align": "start"},
                                {"type": "text", "text": "銷售量", "align": "center"}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": product_boxes
                        }
                    ]
                }
            ]
        }
    }

    return FlexMessage(
        alt_text=f"{branch} {date} 銷售報告",
        contents=FlexContainer.from_json(json.dumps(bubble))
    )
