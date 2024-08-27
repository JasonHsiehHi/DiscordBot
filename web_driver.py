from dotenv import load_dotenv
import time
import re
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


from selenium.webdriver.common.desired_capabilities import DesiredCapabilities # 新版不需要

from selenium.webdriver.support.ui import WebDriverWait # 不太好用 有一些元素本身就是不可交互
from selenium.webdriver.support import expected_conditions as EC

# env
load_dotenv()
h73_Workid = os.environ['H73WORKID']
h73_Password = os.environ['H73PASSWORD']
g73_Workid = os.environ['G66WORKID']
g73_Password = os.environ['G66PASSWORD']

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'browser': 'ALL'}  # 捕获所有级别的日志 
# driver = webdriver.Chrome(desired_capabilities=caps) # desired_capabilities 新版已不再使用 
# 不知為何 caps不用當參數 也能影響driver...

driver = None
actions = None

def setup_by_bot():
    global driver, actions
    driver = webdriver.Chrome()  # 執行完後會自動關機 
    actions = ActionChains(driver)
    time.sleep(0.5)
   
def setup():
    global driver, actions
    options = Options()
    options.add_experimental_option("debuggerAddress", "localhost:9222") # remote 才可以避免自動關機
    driver = webdriver.Chrome(options=options)
    actions = ActionChains(driver)
    time.sleep(0.5)

def open_and_login(game_id:str,workid:str, password:str):
    if game_id == "h73":
        driver.get(f"http://h73hmt.gameop.easebar.com/mcs/main.action")
        login(workid, password)
        
        nav_button = driver.find_element(By.XPATH,'//a[@data-widget="pushmenu"]')
        nav_button.click()
        time.sleep(1)
        
        button = driver.find_element(By.XPATH, '//a[@href="logs.action"]')
        button.click()
        time.sleep(1)
        
        # window_size = driver.get_window_size()  # 不用取實際長寬
        # width = window_size['width']
        # height = window_size['height']
        
        actions.move_by_offset(500, 500).click().perform()  # 一般長度為1024px(寬), 896px(長) 
        time.sleep(0.5)
        print("h73 logs page successfully opened.")
        
    elif game_id == "g66":
        entire_name = "g66naxx2tw"
        # TODO 需要分G66和H73 因為點擊元素不同 些許差異是否能用 method 的參數來做

    else:
        print("the game_id doesn't exist.")
        
def login(workid:str, password:str):
    input_workid = driver.find_element(By.ID, "workid")
    input_workid.send_keys(workid)
    
    input_password = driver.find_element(By.ID, "password")
    input_password.send_keys(password)
    
    form_login = driver.find_element(By.ID, "loginForm")
    form_login.submit()
    time.sleep(2)
    
    
# TODO 增加 account_id, role_name 可用不同的indexname
def get_game_log(role_id:str, start_date:str, end_date:str, datatype:str)-> dict:
    iframes = driver.find_elements(By.ID,"main_frame")
    if len(iframes)>0:
        driver.switch_to.frame(iframes[0])
    
    select_indexname = Select(driver.find_element(By.ID, "indexname"))
    select_indexname.select_by_value("role_id")
    
    input_uid = driver.find_element(By.ID, "uid")
    input_uid.clear()
    input_uid.send_keys(role_id)
    
    # timedateFmt: 'yyyyMMddHHmmss ex:20240801235930'
    input_start_date = driver.find_element(By.ID, "start")
    input_start_date.clear()
    input_start_date.send_keys(start_date)
    
    input_end_date = driver.find_element(By.ID, "end")
    input_end_date.clear()
    input_end_date.send_keys(end_date)    
    
    select_datatype = Select(driver.find_element(By.ID, "datatype"))
    select_datatype.select_by_value(datatype)
    
    initial_num = len(driver.get_log('browser')) # 沒用了 原本是為抓取新LOG
    
    btn_submit = driver.find_element(By.XPATH, '//button[text()="查询"]')
    btn_submit.click()
    time.sleep(5)  # 等待一秒，避免频繁检查导致过多资源消耗

    logs = driver.get_log('browser')
    time.sleep(3)
    
    for log in reversed(logs):  # 从最后一条日志开始
        if log['level'] == 'INFO' and "search result" in log['message']:
            print("the log successfully obtained.")
            return log
    
    print("unable to get the log.")
    return logs

def convert_to_log_list(raw_log:str) -> list:
    #TODO "data":[{...},] 1本來的資料就是輸出list格式 好處是可以把多個datatype都放在一起 格式都相同
    pattern = r'\\\"data\\\":\[\{.*?\}\],\\\"size\\\"'
    match = re.search(pattern, raw_log)
    
    prefix_length = len('\\\"data\\\":')
    suffix_length = len(',\\\"size\\\"')

    # 使用字符串切片去除前缀和后缀
    clean_json = match.group()[prefix_length:-suffix_length].replace('\\\"', '"').replace('\\\\n',' ')
    log_list = json.loads(clean_json)
    return log_list

def filter_log_list(values_to_match:dict, log_list:list) -> list:
    # 字串用包含 數字則是比較
    # ex : {'app_channel':"a50", gem_coin:">200"}
    filtered_list=[]
    for log in log_list:
        for key, criterion in values_to_match.items():
            if key in log.keys():
                if type(log[key]) == str:
                    if criterion not in log[key]:
                        break
                else: # type(log[key]) 為數值
                    if not eval(str(log[key])+criterion):
                        break
                    
            filtered_list.append(log)
        
    return filtered_list


def is_in_log_list(values_to_match:dict, log_list:list) -> bool:
    #TODO: 目前的log_list中是否有吻合values_to_match條件的
    pass
def count_in_log_list(values_to_match:dict, log_list:list) -> int:
    #TODO: 目前的log_list中有吻合values_to_match條件的數量
    # 記得取得時應為str 要想辦法轉成dict
    pass

def extract_field_values(fields:list, log_list:list) -> list:
    # 還是list形式 只是轉為2層巢狀list 僅做轉換型式 以方便處理
    extracted_list = []
    for log in log_list:
        elm = []
        for field in fields:
            if field in log.keys():
                elm.append(log[field])
        extracted_list.append(elm)
    return extracted_list


def output_field_values(fields_to_output:list, log_list:list) -> str:
    list_to_output = extract_field_values(fields_to_output, log_list)
    return json.dumps(list_to_output)


def get_game_logs(criteria_list:list) -> list:
    logs = []
    for criterion in criteria_list:
        raw_log = get_game_log(criterion[0],criterion[1],criterion[2],criterion[3])
        time.sleep(1)
        logs.append(raw_log)
    return logs

def get_loglists_some_datatypes(role_id:str, start_date:str, end_date:str, datatypes:list) -> list:
    loglists = []
    for datatype in datatypes:
        raw_log = get_game_log(role_id, start_date, end_date, datatype)
        time.sleep(1)
        log_list = convert_to_log_list(raw_log["message"])
        loglists.append(log_list)
    return loglists  # 用list 只要有順序就好

# return結果 會比get_game_logs多一筆 用以存放output_list 
def get_loglists_precisely(precise_list:list):
    trimmed_list = [sublist[1:5] for sublist in precise_list]
    raw_logs:list = get_game_logs(trimmed_list) # logs 為每一筆查詢的結果
    
    result_dict = {}
    output_list = []
    num_list = []
    for i in range(len(raw_logs)):
        if raw_logs[i]:
            log_list = convert_to_log_list(raw_logs[i]["message"])
            values_to_match:dict = precise_list[i][5]
            
            if values_to_match:
                log_list = filter_log_list(values_to_match, log_list)
                
            result_dict[str(precise_list[i][0])] = log_list
            num_list.append(len(log_list))
            
            output_str = ""
            fields_to_output:list = precise_list[i][6]
            if fields_to_output:
                output_str = output_field_values(fields_to_output, log_list)
            output_list.append(output_str)
            
    result_dict["output_field"]=output_list
    result_dict["num"]=num_list
    return result_dict # 用dict 因為要用index作為key值
    

def quit():
    driver.quit() # 關閉瀏覽器

# === test ===
# from importlib import reload

# import web_driver as wb

if __name__ == '__main__':
    import excel_utils as eu
    setup_by_bot()
    open_and_login("h73",h73_Workid,h73_Password)
    raw_log = get_game_log("150004660","20240728000000","20240810000000","loginrole")


