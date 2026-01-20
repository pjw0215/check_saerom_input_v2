import pandas as pd
from M0_check_list import CHECK_RULES
from M1_run_rules import run_rules
from M2_PFT_check import PFT_check
from M3_R_issue_check import R_issue_check

def check_list(excel_path):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('future.no_silent_downcasting', True)

    df_raw = pd.read_excel(excel_path, dtype={'챠트번호': str})
    
    abnormal_list, missing_keys, empty_keys = run_rules(df_raw, CHECK_RULES)
    if missing_keys: print(f'\n- 미실시 : {', '.join(missing_keys)}')
    if empty_keys: print(f'\n- 이상소견 없음 : {', '.join(empty_keys)}')
    print('\n'+'\n\n'.join(abnormal_list)+'\n')
    
    PFT_check(df_raw)
    R_issue_check(df_raw)


if __name__ == '__main__':
    EXCEL_PATH = r"C:\Users\MyCom\Documents\통합 문서1.xlsx"
    check_list(EXCEL_PATH)