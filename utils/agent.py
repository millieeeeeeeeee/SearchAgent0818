"""回答Agent"""
import pandas as pd
import pygsheets
import requests
from datetime import datetime, timedelta


#變數設定
today = datetime(2024, 9, 1)

GPT_API_KEY = "sk-tGDJdkhp45o5rnAmC021091179F1444d958d035a5dA8DfF5"
GPT_ENDPOINT = "https://free.v36.cm/v1/chat/completions"

GPT_headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json"
    }



def PhaseI_Parser_gpt(question):
  prompt = f"""
  你是一個資料查詢問題剖析器，目的是將一段自然語言問題，解析成結構化的 JSON 格式，用於後續資料處理。
  請針對每個問題，萃取下列欄位：

  目前系統時間設定為 2024/09/01，資料涵蓋時間為 2024/07/01～2024/08/31，請依此判斷時間。

  - `question_type`: 問題的類型，可為：
    - `"查詢"`：查找具體資料，例如「某店的營業額」、「某商品的銷售量」
    - `"統計"`：需整合多筆資料後回答，例如「總銷售量」、「平均營業額」
    - `"比較"`：兩組以上資料的比較，例如「A店比B店多幾份」、「這週比上週成長」
    - `"建議"`：請求系統提出建議，例如「要下架哪些品項」、「推薦熱銷商品」
    - `"篩選"`：需要根據條件篩出資料，例如「找出銷售為0的商品」、「哪些店庫存過剩」

  - `target_metric`: 使用者最關心的核心指標，例如：「營業額」「銷售量」「庫存量」「成長率」「是否該下架」

  - `filters`: 限制條件，**可有零或多個物件**包含：
    - 日期 ：以「%Y/%M/%D」形式呈現。若問題中未明確提及時間日期，請設為空物件。
    - 分店
    - 商品名稱
    - 其他（如「庫存過剩」「銷售為0」「熱賣」「飲品」））
    - 若無篩選條件請設為空物件

  - `required_tables`: 需要用到哪幾張表：
    - `"每日營業額"`
    - `"每日商品銷售量"`
    - `"目前庫存量"`

  - `chunk_strategy`: 根據問題重點選擇 chunk 方式：
    - `"chunk_day"`：以「日期」為主，例如比較週成長、時間趨勢
    - `"chunk_branch"`：以「分店」為主，例如比較店別績效
    - `"chunk_merchdise"`：以「商品」為主，例如找熱銷、滯銷、建議下架商品

  ---
  請輸出 **乾淨的 JSON 格式**，不要加上說明或註解。
  以下是使用者問題：{question}
  """
  payload = {
      "model": "gpt-3.5-turbo",#gpt-3.5-turbo
      "messages": [
          {"role": "user", "content": prompt}
      ]
  }
  response = requests.post(GPT_ENDPOINT, headers=GPT_headers, json=payload)
  response.raise_for_status()
  result = response.json()
  parsed_dict = eval(result["choices"][0]["message"]["content"])
  return parsed_dict

def chunk_revenue(parsed_dict,df):
  filters = parsed_dict.get("filters", {})
  date = filters.get("日期")
  branch = filters.get("分店")
  merchandise = filters.get("商品名稱")

  if date and "日期" in df.columns:
    df = df[df["日期"] == date]
  if branch :
    df = df.melt(id_vars=["日期"],var_name="分店",value_name="營業額")
    df = df[df["分店"] == branch]
  df['日期'] = pd.to_datetime(df['日期'], format='mixed').dt.date
  lines = ["《每日營業額》"]
  for _, row in df.iterrows():
      line = f"- 分店：{row['分店']}｜日期：{row['日期']}｜營業額：{row['營業額']}"
      lines.append(line)
  return "\n".join(lines)

def chunk_product(parsed_dict,df):
  filters = parsed_dict.get("filters", {})
  date = filters.get("日期")
  branch = filters.get("分店")
  merchandise = filters.get("商品名稱")

  if date and "日期" in df.columns:
    df = df[df["日期"] == date]
  if merchandise and "商品名稱" in df.columns:
    df = df[df["商品名稱"] == merchandise]
  if branch :
    df = df.melt(id_vars=["日期", "商品名稱"],var_name="分店",value_name="銷售量")
    df = df[df["分店"] == branch]
  df['日期'] = pd.to_datetime(df['日期'], format='mixed').dt.date
  lines = ["《每日商品銷售量》"]
  for _, row in df.iterrows():
      line = f"- 分店：{row['分店']}｜日期：{row['日期']}｜商品名稱：{row['商品名稱']}｜銷售量：{row['銷售量']}"
      lines.append(line)
  return "\n".join(lines)


def chunk_stock(parsed_dict,df):
  filters = parsed_dict.get("filters", {})
  date = filters.get("日期")
  branch = filters.get("分店")
  merchandise = filters.get("商品名稱")

  df = df.melt(id_vars=["商品名稱"],var_name="分店",value_name="庫存量")
  df.insert(0, "日期", today.strftime('%Y-%m-%d'))
  if merchandise:
    df = df[df["商品名稱"] == merchandise]
  if branch:
    df = df[df["分店"] == branch]

  lines = ["《每日商品銷售量》"]
  for _, row in df.iterrows():
      line = f"- 分店：{row['分店']}｜日期：{row['日期']}｜商品名稱：{row['商品名稱']}｜庫存量：{row['庫存量']}"
      lines.append(line)
  return "\n".join(lines)

def PhaseII_DataSelector(parsed_dict):
  required_tables = parsed_dict.get("required_tables", [])
  gc = pygsheets.authorize(service_account_file='./gen-lang-client-0700041250-71d7360e4469.json')

  survey_url = 'https://docs.google.com/spreadsheets/d/1QmpmeFcAqCEwW9lJUuEd40gD27SvlMoUSyzp7jvhG-E/edit?usp=sharing'
  sh = gc.open_by_url(survey_url)

  data = []
  for table_name in required_tables:
    df = sh.worksheet_by_title(table_name).get_as_df(start='A1', index_colum=None, empty_value='', include_tailing_empty=False)
    if table_name=='每日營業額':
      line=chunk_revenue(parsed_dict,df)
    elif table_name=='每日商品銷售量':
      line=chunk_product(parsed_dict,df)
    elif table_name=='目前庫存量':
      line=chunk_stock(parsed_dict,df)
    data.append(line)
  return "\n\n".join(data)


def PhaseIII_Answer_gpt(question,data,parsed_dict):
  prompt = f"""
      你是一位資料分析師，幫助使用者查詢便當店銷售資料。
      請根據以下便當店每日營業數據與商品銷售/庫存記錄:{data}
      使用者問題如下：
      「{question}」
      可以參考問題分析後的格式:
      {parsed_dict}

      用簡潔的話完整回答我問題
      """
  payload = {
      "model": "gpt-3.5-turbo",
      "messages": [
          {"role": "user", "content": prompt}
      ]
  }
  response = requests.post(GPT_ENDPOINT, headers=GPT_headers, json=payload)
  result = response.json()
  return result["choices"][0]["message"]["content"]

#整合 PhaseI~III
def final_gpt(question):
  parsed_dict=PhaseI_Parser_gpt(question)
  print(f"PhaseI_Parser_gpt 完成 {parsed_dict}")
  data=PhaseII_DataSelector(parsed_dict)
  print(f"PhaseII_DataSelector 完成 {data}")
  answer=PhaseIII_Answer_gpt(question,data,parsed_dict)
  return answer