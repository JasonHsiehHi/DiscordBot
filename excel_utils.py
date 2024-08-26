import pandas as pd
from io import BytesIO
import json

def conver_to_criteria(file_for_log) -> list:
    if isinstance(file_for_log, bytes):
        excel_data = pd.read_excel(BytesIO(file_for_log))
    else:  # path_to_file:str
        excel_data = pd.read_excel(file_for_log)
        
    if excel_data['optional_values_to_match'].isna().any():
        excel_data = excel_data.fillna("{}")
    if excel_data['optional_fields_to_output'].isna().any():
        excel_data = excel_data.fillna("[]")
        
    excel_data['optional_values_to_match'] = excel_data['optional_values_to_match'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    excel_data['optional_fields_to_output'] = excel_data['optional_fields_to_output'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    
    precise_list = excel_data.apply(list, axis=1).tolist()
    return precise_list

def write_log_to_excel(send_time:str,outputs_for_sheet:dict):
    with pd.ExcelWriter(f'./output/output_{send_time}.xlsx', engine='xlsxwriter') as writer:
        for key, output in outputs_for_sheet.items():
            df = pd.DataFrame(output)
            df.to_excel(writer, sheet_name=key, index=False)
    print("excel completed!")
    
def input_excel_and_conver(file_path:str) -> list:
    precise_list = conver_to_criteria(file_path) # './input/file_name.xlsx'
    return precise_list


# === test ===
# from importlib import reload

# import excel_utils as eu

if __name__ == '__main__':
    precise_list = input_excel_and_conver("./input/H73_xzxgain_for_lost.xlsx")
    print(precise_list)
    precise_list2 = input_excel_and_conver("./input/H73_jinghua_reward_for_lost.xlsx")
    print(precise_list2)