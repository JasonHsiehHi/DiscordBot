import discord
from discord.ext import commands
import httplib2
import os
from apiclient import discovery
import anthropic

from . import excel_utils
from . import web_driver

from dotenv import load_dotenv

load_dotenv()
# Google Sheets API env
GoogleAPIKey = os.environ['GOOLEAPIKEY']
SpreadsheetId = os.environ['SHEET_ID']  # 要使用哪一個Sheet和Range全由env決定
DatabaseRange = os.environ['DATABASERANGE']

# Claude API env
ClaudeAPIKey = os.environ['CLAUDEAPIKEY']

#DiscordBot env
TOKEN = os.environ['TOKEN']

#Google API
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
service = discovery.build(  # servive只是獲取權限訪問Google的API而已
    'sheets',
    'v4',
    http=httplib2.Http(),
    discoveryServiceUrl=discoveryUrl,
    developerKey=GoogleAPIKey)

#Claude API
client = anthropic.Anthropic(
    api_key=ClaudeAPIKey,
)

#Discord API
intent=discord.Intents.all()
clientBot = commands.Bot(command_prefix = "/",intents=intent)

# pronmpt設定
def get_default_prompt(sheet_content):
    pronmpt = f'''\
        1.回答時，僅能依據目前收集到的資料內容，若當前資料內容不足以作出判斷，則告知可能仍缺少的資料內容
        2.回答時，應盡量保持簡潔明瞭
        3.回答時，若多筆資料內容相互牴觸，則以時間最新的資料內容為準
        4.回答後，不能沒有任何依據，必須附上所參考的資料內容，須包含該篇資料內容的時間、來源、標題三項
        5.回答後，最後都必須告知遊戲後續仍可能會參考玩家反饋狀況作出適當調整
        以下為資料內容：
        {sheet_content}
    '''
    return pronmpt


# TODO: 增加可依據時間區間決定所需資料內容
def get_sheets_data(): 
    result = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=DatabaseRange).execute()
    values = result.get('values', [])
    headers = values[0]
    data = values[1:]
    sheet_content = f"Headers: {headers}\n"
    sheet_content += "\n".join([", ".join(row) for row in data])
    
    return sheet_content

# TODO:為減少每次讀取的資料量 應分為2次訪問 第1次判斷要訪問那些資料(以類別分類)，第2次在針對這些資料訪問
def send_to_claude(message_prompt, default_prompt):
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.1, # 數值範圍在0~1之間，數值越低則依據精確事實回答；數值越高則多樣性回答
            messages=[
                {"role": "user", "content": f"{message_prompt}\n{default_prompt}"}
            ]
        )

    except anthropic.APIError as e: # API 錯誤（例如無效的請求、認證錯誤等）
        response = f"API錯誤: {str(e)}"

    except anthropic.APIConnectionError as e: # 連接錯誤（例如網絡問題）
        response = f"連接錯誤: {str(e)}"

    except Exception as e: # 其他未預期的錯誤
        response = f"發生未知錯誤: {str(e)}"

    response = message.content[0].text
    return response


sheet_content = get_sheets_data()
default_prompt = get_default_prompt(sheet_content)


# 起動時呼叫
@clientBot.event
async def on_ready():                       
    print(f'Logged in as {clientBot.user}')

# TODO: 新增refresh 和 list 方法
# async def refresh(ctx):
# async def list(ctx):


@clientBot.command()
async def ask(ctx ,game_id:str ,* ,message:str=None):
    await ctx.send("仍在施工中!")
    return

    if ctx.author.bot: # 送信者為Bot時無視
        return
    if ctx.guild == None: # 不能私訊詢問
        return

    if not message:
        await ctx.send("沒有提問任何問題")

    response = send_to_claude(message, default_prompt)
    await ctx.send(response)

# TODO: 要能決定gameid 這樣才能選擇在g66和h73中使用
@clientBot.command()
async def h73_ask(ctx ,* ,message:str=None):
    await ask(ctx, "h73", message=message)
    
@clientBot.command()
async def g66_ask(ctx ,* ,message:str=None):
    await ask(ctx, "g66", message=message)


@clientBot.command()
async def h73_log(ctx ,* ,message:str=None):
    if ctx.author.bot: # 送信者為Bot時無視
        return
    if ctx.guild == None: # 不能私訊詢問
        return
    
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(('.xlsx', '.xls')):
            file_bytes = await attachment.read()
            precise_list = excel_utils.conver_to_criteria(file_bytes)
            result_dict = web_driver.get_loglists_precisely(precise_list)
            
            send_time = message.created_at
            formatted_time = send_time.strftime("%Y%m%d%H%M%S")
            excel_utils.write_log_to_excel(formatted_time, result_dict)
            
            # 回應用戶，展示文件中的數據
            await message.channel.send(f"讀取文件: {attachment.filename}\n輸出文件如下:\noutput_{formatted_time}.xlsx")



@clientBot.command()
async def g66_log(ctx ,* ,message:str=None):
    await ctx.send("仍在施工中!")
    return


"""
 此方法會監聽所有對話 不實用且會導致效能耗損
@client.event
async def on_message(message):
    if message.author == client.user: # 扣除bot自己發送的對話 壁面無限迴圈
        return
"""

# === test ===
# from importlib import reload

if __name__ == '__main__':
    clientBot.run(TOKEN) # Bot起動
    
