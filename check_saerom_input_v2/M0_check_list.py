CHECK_RULES = {
    "메모": {
        "target_columns": ['기타 특이사항', '특수기타메모', '청력정밀 특이사항'],
        "exclude_exact": ['무'],
        "exclude_regex": [],
    },
    
    "흉부X선": {
        "target_columns": ['흉부X선'],
        "exclude_exact": ['특이사항없음'],
        "exclude_regex": ['Within normal limit'],
    },

    "심전도": {
        "target_columns": ['ECG'],
        "exclude_exact": ['특이사항무'],
        "exclue_regex": [],
    },

    "혈뇨": {
        "target_columns": ['BLD (뇨잠혈)'],
        "exclude_exact": [],
        "exclude_regex": ['음성', '약양성', '1+'],
        "data_filter": lambda df: df[df['성별MF'] == 'F'].copy()   # 여성만 필터
    },
}