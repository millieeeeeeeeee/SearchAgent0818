"""googlesheet資料處理"""
import pandas as pd
import pygsheets
import config

SERVICE_ACCOUNT_JSON = config.SERVICE_ACCOUNT_JSON

#合併三張表資料
def merged_df():
  gc = pygsheets.authorize(credentials=SERVICE_ACCOUNT_JSON)

  survey_url = 'https://docs.google.com/spreadsheets/d/1QmpmeFcAqCEwW9lJUuEd40gD27SvlMoUSyzp7jvhG-E/edit?usp=sharing'
  sh = gc.open_by_url(survey_url)

  # 載入每張表
  df1 = sh.worksheet_by_title('每日營業額').get_as_df(start='A1', index_colum=None, empty_value='', include_tailing_empty=False)
  df2 = sh.worksheet_by_title('每日商品銷售量').get_as_df(start='A1', index_colum=None, empty_value='', include_tailing_empty=False)
  df3 = sh.worksheet_by_title('目前庫存量').get_as_df(start='A1', index_colum=None, empty_value='', include_tailing_empty=False)

  # 寬轉長格式
  df1_long = df1.melt(id_vars="日期", var_name="分店", value_name="營業額")
  df2_long = df2.melt(id_vars=["日期", "商品名稱"], var_name="分店", value_name="銷售量")

  # 合併df1,df2為一張總表->merged
  merged = df1_long.merge(df2_long, on=["日期", "分店"], how="left")
  merged['日期'] = pd.to_datetime(merged['日期'], format='mixed')

  return merged

def df3():
  gc = pygsheets.authorize(credentials=SERVICE_ACCOUNT_JSON)

  survey_url = 'https://docs.google.com/spreadsheets/d/1QmpmeFcAqCEwW9lJUuEd40gD27SvlMoUSyzp7jvhG-E/edit?usp=sharing'
  sh = gc.open_by_url(survey_url)

  # 載入第三張表
  df3 = sh.worksheet_by_title('目前庫存量').get_as_df(start='A1', index_colum=None, empty_value='', include_tailing_empty=False)

  return df3
