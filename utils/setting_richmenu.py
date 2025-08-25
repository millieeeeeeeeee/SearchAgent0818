#Flex Message模組
"""RichMenu格式、功能總覽"""
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
    FlexMessage, FlexContainer
)
from linebot.v3.messaging import MessagingApi, MessagingApiBlob, RichMenuRequest, RichMenuArea, RichMenuSize, RichMenuBounds, PostbackAction

from utils.setting_datetime import *
from utils.richmenu_UL_function import *
from utils.richmenu_UM_function import *
from utils.richmenu_UR_function import *


#變數設定
import config
access_token = config.access_token
secret = config.secret


configuration = Configuration(access_token=access_token)
api_client = ApiClient(configuration)
blob_api = MessagingApiBlob(api_client)
messaging_api = MessagingApi(api_client)

def create_richmenu_for_six():
    # 建立 Rich Menu
    create_rich_menu_request = RichMenuRequest(
      size=RichMenuSize(width=2500, height=1686),
      selected=True,
      name="main_menu",
      chat_bar_text="主選單",
      areas=[
          RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                      action=PostbackAction(label="分店查詢", data="session=UL&step=select_branch")),
          RichMenuArea(bounds=RichMenuBounds(x=834, y=0, width=833, height=843),
                      action=PostbackAction(label="日期查詢", data="session=UM&step=select_date")),
          RichMenuArea(bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
                      action=PostbackAction(label="庫存查詢", data="session=UR&step=select_branch")),
          RichMenuArea(bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                      action=PostbackAction(label="銷售排行", data="session=LL&step=select_time")),
          RichMenuArea(bounds=RichMenuBounds(x=834, y=843, width=833, height=843),
                      action=PostbackAction(label="功能2", data="session=LM&step=booking")),
          RichMenuArea(bounds=RichMenuBounds(x=1667, y=843, width=833, height=843),
                      action=PostbackAction(label="功能3", data="session=LR&step=service")),
      ]
    )


    # 建立 Rich Menu
    response = messaging_api.create_rich_menu(create_rich_menu_request)
    rich_menu_id = response.rich_menu_id
    print("✅ 六格Rich Menu 已建立，ID:", rich_menu_id)

    # 上傳圖片
    with open("./images/richmenu_background_six.png", "rb") as image:
      blob_api.set_rich_menu_image(rich_menu_id,
        body=bytearray(image.read()),
        _headers={'Content-Type': 'image/png'})
    print("✅ 圖片已上傳")

    # 設為預設 Rich Menu
    messaging_api.set_default_rich_menu(rich_menu_id)
    print("✅ 已設為預設 Rich Menu")

def create_richmenu_for_three():
    # 建立 Rich Menu
    create_rich_menu_request = RichMenuRequest(
      size=RichMenuSize(width=2500, height=843),
      selected=True,
      name="main_menu",
      chat_bar_text="主選單",
      areas=[
          RichMenuArea(bounds=RichMenuBounds(x=0, y=200, width=833, height=421),
                      action=PostbackAction(label="分店查詢", data="session=UL&step=select_branch")),
          RichMenuArea(bounds=RichMenuBounds(x=834, y=200, width=833, height=421),
                      action=PostbackAction(label="日期查詢", data="session=UM&step=select_date")),
          RichMenuArea(bounds=RichMenuBounds(x=1667, y=200, width=833, height=421),
                      action=PostbackAction(label="庫存查詢", data="session=UR&step=select_branch"))
      ]
    )


    # 建立 Rich Menu
    response = messaging_api.create_rich_menu(create_rich_menu_request)
    rich_menu_id = response.rich_menu_id
    print("✅ 三格Rich Menu 已建立，ID:", rich_menu_id)

    # 上傳圖片
    with open("./images/richmenu_background_three.png", "rb") as image:
      blob_api.set_rich_menu_image(rich_menu_id,
        body=bytearray(image.read()),
        _headers={'Content-Type': 'image/png'})
    print("✅ 圖片已上傳")

    # 設為預設 Rich Menu
    messaging_api.set_default_rich_menu(rich_menu_id)
    print("✅ 已設為預設 Rich Menu")

#功能
def handle_richmenu_session(event, data_dict):
    session = data_dict.get("session")

    if session == "UL":
        return search_from_branch(event, data_dict)
    elif session == "UM":
        return search_from_date(event, data_dict)
    elif session == "UR":
        return search_inventory(event, data_dict)
    else:
        return TextMessage(text=f"⚠️ 尚未實作的功能區塊 session={session}")

"""UL左上"""
def search_from_branch(event, data_dict):
    step = data_dict.get("step")


    if step == "select_branch":
        return UL_get_branch_selector()

    elif step == "select_date":
        branch = data_dict.get("branch", "")
        return UL_get_date_selector(branch)

    elif step == "one_day_show_result":
      branch = data_dict.get("branch", "")
      date = event.postback.params.get("date")
      return UL_one_day_detail_list(branch, date)
    elif step == "last_week_show_result":
      branch = data_dict.get("branch", "")
      start, end = get_last_week_range(today)
      return UL_days_detail_list(branch, start, end)
    elif step == "last_month_show_result":
      branch = data_dict.get("branch", "")
      start, end = get_last_month_range(today)
      return UL_days_detail_list(branch, start, end)

    else:
      return TextMessage(text=f"⚠️ UL無法辨識步驟：{step}")

"""UM中上"""
def search_from_date(event, data_dict):
    step = data_dict.get("step")

    if step == "select_date":
        return UM_get_date_selector()

    elif step == "one_day_show_result":
        date = event.postback.params.get("date")
        return UM_one_day_detail_list(date)

    elif step == "last_week_show_result":
        start, end = get_last_week_range(today)
        return UM_days_detail_list(start, end)

    elif step == "last_month_show_result":
        start, end = get_last_month_range(today)
        return UM_days_detail_list(start, end)

    else:
        return TextMessage(text=f"⚠️ UM無法辨識步驟：{step}")

"""UR右上"""
def search_inventory(event, data_dict):
    step = data_dict.get("step")

    if step == "select_branch":
        return UR_get_branch_selector()
    elif step == "show_result":
        branch = data_dict.get("branch", "")
        return UR_detail_list(branch)

    else:
        return TextMessage(text=f"⚠️ UR無法辨識步驟：{step}")

