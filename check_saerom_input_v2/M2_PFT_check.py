import pandas as pd
from tabulate import tabulate
import os

## 기존 측정불가의 경우를 고려하지 않는 상태!! ##

EXCEL_PATH = r"C:\Users\MyCom\Documents\통합 문서1.xlsx"

dirname = os.path.split(os.path.abspath(__file__))[0]
os.chdir(dirname)

FVC_COL = r'%FVC'
FEV1_COL = r'%FEV'
RATIO_COL = 'FEV1/FVC(%)'
RESULT_COL = '폐활량결과'

OBS_RESULT = '폐쇄성환기장애'
RES_RESULT = '제한성환기장애'
COMB_RESULT = '혼합성환기장애'

def PFT_check(df_raw):   
    try:
        df_PFT = df_raw[[FVC_COL, FEV1_COL, RATIO_COL, '폐활량결과']].dropna(how='all').copy()
    except KeyError as err:
        print(f'- 폐기능 검사 시행자가 없습니다.')
        print()
        return

    ''' 필터 '''
    FVC_low = df_PFT[FVC_COL] < 80
    ratio_low = df_PFT[RATIO_COL] < 70
    U_filt = df_PFT[[FVC_COL, FEV1_COL]].isna().all(axis=1)


    normal_filt = (~U_filt & ~FVC_low & ~ratio_low)
    res_filt = (FVC_low & ~ratio_low)
    obs_filt = (~FVC_low & ratio_low)
    comb_filt = (FVC_low & ratio_low)

    ''' D여부 검토 '''
    D_list = []
    df_res = df_PFT.loc[res_filt].copy()
    D_list.extend(df_res[df_res[FVC_COL] < 50].index.tolist())
    df_obs = df_PFT.loc[obs_filt].copy()
    D_list.extend(df_obs[df_obs[FEV1_COL] < 50].index.tolist())
    df_comb = df_PFT.loc[comb_filt].copy()
    D_list.extend(df_comb[df_comb[FEV1_COL] < 50].index.tolist())

    if len(D_list) > 0:
        print('* PFT D판정 대상자가 있습니다.')
        print(tabulate(df_raw.loc[D_list, ['챠트번호', '검진일자', '검진번호', '성명', FVC_COL, FEV1_COL, RATIO_COL, RESULT_COL]].set_index('챠트번호'), headers='keys', tablefmt='psql'))
        print()
    else:
        print('- PFT D 없음')
        print()

    ''' 서술형 결과 입력 오류 검토 '''
    df_normal_error = (df_PFT.loc[normal_filt, RESULT_COL] != '정상')
    df_res_error = (df_PFT.loc[res_filt, RESULT_COL] != RES_RESULT)
    df_obs_error = (df_PFT.loc[obs_filt, RESULT_COL] != OBS_RESULT)
    df_comb_error = (df_PFT.loc[comb_filt, RESULT_COL] != COMB_RESULT)
    # df_U_error = (df_PFT.loc[U_filt, RESULT_COL] != '측정불가')
    
    # 출력할 idx 만들기
    error_idx_list = []
    error_idx_list.extend(df_normal_error[df_normal_error].index.tolist())  # 정상이 되어야 하나 다른 경우
    error_idx_list.extend(df_res_error[df_res_error].index.tolist())  # 제한성이 되어야 하나 다른 경우
    error_idx_list.extend(df_obs_error[df_obs_error].index.tolist())  # 폐쇄성이 되어야 하나 다른 경우
    error_idx_list.extend(df_comb_error[df_comb_error].index.tolist())  # 혼합성이 되어야 하나 다른 경우
    # error_idx_list.extend(df_U_error[df_U_error].index.tolist())  # U가 되어야 하나 다른 경우

    if len(error_idx_list) > 0:
        print('* PFT 서술형 결과에 오류가 있습니다.')
        print(tabulate(df_raw.loc[error_idx_list, ['챠트번호', '검진일자', '검진번호', '성명', FVC_COL, RATIO_COL, RESULT_COL]].set_index('챠트번호'), headers='keys', tablefmt='psql'))
        print()
    else:
        print('- PFT 서술형 입력오류 없음')
        print()


if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    df = pd.read_excel(EXCEL_PATH, dtype={'챠트번호': str})
    PFT_check(df)