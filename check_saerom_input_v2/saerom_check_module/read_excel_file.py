import pandas as pd

def read_excel_file(EXCEL_PATH):

    df = pd.read_excel(EXCEL_PATH, dtype={'챠트번호': str, '검진일자': str})
    df = df[df['"1"특수"2"배치"3"수시"4"임시"5"추적검사'].notna()]  # 특수 배치 수시 임시 추적검사만 남김 (일검은 제외)

    if len(df.index) == 0:
        raise Exception('** 날짜 및 출장 조건에 맞는 수검자가 없습니다. **')
    
    return df