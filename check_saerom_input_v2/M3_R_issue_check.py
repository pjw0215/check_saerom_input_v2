import pandas as pd
import numpy as np
from tabulate import tabulate
import os

EXCEL_PATH = r"C:\Users\MyCom\Documents\통합 문서1.xlsx"

dirname = os.path.split(os.path.abspath(__file__))[0]
os.chdir(dirname)


def has_R_issue(result):
    if pd.isna(result) or not isinstance(result, str):
        return np.nan
        
    R_issue_list = []

    mat_judge_list = result.split(' ,')
    for mat_judge in mat_judge_list:
        mat_judge = mat_judge.strip()
        
        if ':' not in mat_judge:  # 판정 없는 경우
            continue

        mat, judge = mat_judge.split(':')
        if ('추가' in judge) and ('소음' not in mat):  # 재검인데 소음 재검이 아닌 것들을 리턴
            R_issue_list.append(mat.strip())
    
    if len(R_issue_list) == 0:
        return np.nan
    else:
        return ', '.join(R_issue_list)
    

def R_issue_check(df_raw):
    df_raw['소음외R'] = df_raw['특수검진소견'].apply(has_R_issue)
    R_issue_list = df_raw['소음외R'].dropna().index.tolist()

    if len(R_issue_list) > 0:
        print('* 소음외 R판정 대상자가 있습니다.')
        print(tabulate(df_raw.loc[R_issue_list, ['챠트번호', '검진일자', '검진번호', '성명', '소음외R']].set_index('챠트번호'), headers='keys', tablefmt='psql'))
        print()
    else:
        print('- 소음외 R 없음')
        print()


if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    df = pd.read_excel(EXCEL_PATH, dtype={'챠트번호': str})
    R_issue_check(df)