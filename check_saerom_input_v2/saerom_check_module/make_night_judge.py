import pandas as pd
import numpy as np
import os

pd.options.mode.chained_assignment = None  # ⚠️ pandas의 SettingWithCopyWarning을 무시
import warnings
warnings.filterwarnings('ignore')

SBP = '혈압(최고)'
DBP = '혈압(최저)'
GLUCOSE = 'Glocose(FBS)'
A1C = 'HbA1C'
TOTAL = 'Total'
TG = 'TG'
HDL = 'HDL-C'


def make_night_judge(df):

    # A1C 컬럼이 없는 경우가 있으므로, 없으면 만들어준다.
    if A1C not in df.columns:
        df[A1C] = np.nan

    # 실측정한 케이스가 없는 경우 컬럼이 없으므로 생성해준다.
    if 'LDL-C' not in df.columns:
        df['LDL-C'] = np.nan

    # 실측정값(LDL-C)을 우선으로하고, 없을 경우 계산값(LDL(계산식)을 사용
    df['LDL_combined'] = df['LDL-C'].combine_first(df['LDL(계산식)'])
    
    # 위에서부터 순서대로 적용됨. 예를들어 HT-R2부터 정의하고, 남은것에서 HT-DN1 정의하는 방식..
    HTN_filt_list = [
        [('HT-R2'), (df['1.고혈압약물치료'] == 1) & ((df[SBP] >= 160) | (df[DBP] >= 110))],
        [('HT-DN1'), (df['1.고혈압약물치료'] == 1)],
        [('HT-R1'), (df[SBP] >= 160) | (df[DBP] >= 100)],
        [('HT-DN2'), (df[SBP] >= 140) | (df[DBP] >= 90)],
    ]

    DM_filt_list = [
        [('DM-DN2'), (df[GLUCOSE] < 60)],
        [('DM-R2'), (df['1.당뇨 약물치료'] == 1) & ((df[GLUCOSE] >= 300) | (df[A1C] >= 10))],
        [('DM-DN1'), (df['1.당뇨 약물치료'] == 1)],
        [('DM-DN3'), (df[GLUCOSE] >= 126) | (df[A1C] >= 6.5)],
        [('DM-CN1'), (df[GLUCOSE] >= 110)]
    ]

    LIPID_filt_list = [
        [('LP-DN1'), (df['1.이상지질혈증 약물치료'] == 1)],
        [('LP-DN2'), (df[TG] >= 500)],
        [('LP-DN2'), (df['LDL_combined'] >= 160)],
        [('LP-CN1'), (df[TOTAL] > 240)],
        [('LP-CN1'), (df['LDL_combined'] >= 130)],
        [('LP-CN1'), (df[TG] > 200)],
        [('LP-CN1'), (df[HDL] < 40)]
    ]

    # DAESA_filt_list = [
    #     [('LP-CN2'), (df['대사증후군결과'] == '대사증후군의심')]
    # ]

    def judge_each_exam(df, filt_list):
        df_result = pd.DataFrame()
        for judge, filt in filt_list:
            df_temp = pd.DataFrame(index=df[filt].index, columns=['결과']).fillna(judge)
            df_result = df_result.combine_first(df_temp)
        return df_result

    df_judge_concat = pd.concat([
        judge_each_exam(df, HTN_filt_list).set_axis(['HTN'], axis=1),
        judge_each_exam(df, DM_filt_list).set_axis(['DM'], axis=1),
        judge_each_exam(df, LIPID_filt_list).set_axis(['LIPID'], axis=1),
        # judge_each_exam(df, DAESA_filt_list).set_axis(['DAESA'], axis=1)
    ], axis=1).sort_index()
    
    df_judge_concat['야간심혈 판정수'] = df_judge_concat.count(axis=1)

    return df_judge_concat


def read_df_opinion():
    try: module_folder = os.path.abspath(os.path.dirname(__file__))  # .py
    except NameError: module_folder = os.getcwd()  # .ipynb

    df_opinion = pd.read_excel(os.path.join(module_folder, 'night_opinion.xlsx'), index_col=0)
    df_opinion = df_opinion.set_index('소견코드')
    
    return df_opinion


def _build_row_info(row, df_opinion):
    # --- HTN, DM, LIPID 코드 모으기 ---
    codes = row[['HTN', 'DM', 'LIPID']].dropna().tolist()
    if not codes:
        return pd.Series({'소견': np.nan, '조치': np.nan, '입력코드': np.nan})

    # --- df_opinion에서 우선순위 정렬 ---
    ordered = (
        df_opinion.loc[codes]
        .sort_values(by='우선순위', ascending=True)
    )

    # --- 필요한 값들 추출 ---
    opinion = ' / '.join(ordered['소견명'].drop_duplicates())
    action  = ' / '.join(ordered['조치명'].drop_duplicates())
    top_input_code = ordered.iloc[0]['입력코드']   # 가장 우선순위 높은 코드

    return pd.Series({
        '소견': opinion,
        '조치': action,
        '입력코드': top_input_code
    })


def make_opinion_and_action(df_night_judge):
    df_opinion = read_df_opinion()

    # df_night_judge 전체에 적용
    df_night_judge[['소견', '조치', '입력코드']] = df_night_judge.apply(_build_row_info, df_opinion=df_opinion, axis=1)

    return df_night_judge