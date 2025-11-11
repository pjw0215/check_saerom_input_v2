import re
import pandas as pd
import numpy as np
from itertools import product
try:  # 모듈 직접 실행 시
    from read_recent_db_file import read_recent_db_file
except ImportError:  # 부모 폴더에서 실행 시
    from .read_recent_db_file import read_recent_db_file

class MatchStandardName():

    def __init__(self, mat_raw, mat_db):
        self.mat_raw = mat_raw
        self.mat_db = mat_db
        self.mat_std = ''

        # 필수 변형 적용
        self.mat_raw = re.sub(r'^\(배\)', '', self.mat_raw)
        self.mat_raw = re.sub(r'\[.*\]', '', self.mat_raw)
        self.mat_raw = re.sub('2차', '', self.mat_raw)

        # db 띄어쓰기 제거
        self.mat_db = self.mat_db.replace(' ', '', regex=True)

        # 변형의 모든 경우를 적용해보며 맞춰보기
        for combi in list(product([False, True], repeat=3)):
            mat = self.mat_raw
            if combi[0]: mat = self.mod1(mat)
            if combi[1]: mat = self.mod2(mat)
            if combi[2]: mat = self.mod3(mat)

            try:
                self.mat_std = self.search_matched_col(mat)
                return None
            except: pass

        self.mat_std = np.nan
        return None

    def mod1(self, mat):
        return re.sub(' ', '', mat)
    
    def mod2(self, mat):
        return re.sub(r'\([^)]*\)', '', mat)

    def mod3(self, mat):
        return re.sub('및그화합물|및함유제제|및함유물질|물질을중량비율1%이상함유한제재|및그무기화합물', '', mat)
    
    def search_matched_col(self, mat):
        found_col = (self.mat_db == mat.lower().strip()).any()
        name_col = found_col.tolist().index(True)
        name_row = (self.mat_db.iloc[:,name_col] == mat.lower().replace(' ','')).tolist().index(True)
        return self.mat_db.iloc[name_row]['대표이름']


def convert_to_list_from_str(mat_list_str, mat_db=pd.DataFrame()):
    if len(mat_db.index) == 0:
        mat_db = read_recent_db_file()

    mat_splitted = re.split(r'(?<!\d)(?<!,[nN]{1})(?<!^[nN])(?<!^\(배\)[nN]),(?![^(]*[)])(?![^\[]*[\]])', mat_list_str)

    def replace_to_std_name(mat_raw, mat_db):
        mat_std = MatchStandardName(mat_raw, mat_db).mat_std
        if not pd.isna(mat_std): return mat_std  # 해당하는 물질이 있으면 대표물질명으로, 없으면 np.nan 반환
        else: return np.nan

    mat_concat = pd.Series(mat_splitted)
    mat_std_converted = mat_concat.apply(replace_to_std_name, mat_db=mat_db)
    not_converted_mat_idx_list = mat_std_converted.index.drop(mat_std_converted.dropna().index)  # 대체되지 않은 물질들
    not_converted_mat_list = mat_concat.loc[not_converted_mat_idx_list].tolist()
    mat_std_concat = mat_std_converted.dropna().tolist()
    if len(not_converted_mat_list) > 0:
        print('* 전환되지 않은 물질명 :', ', '.join(not_converted_mat_list))
    return mat_std_concat


def extract_idx_containing_specific_exam(df_raw, exam, mat_db=pd.DataFrame()):

    if len(mat_db.index) == 0: mat_db = read_recent_db_file()

    def mat_list_include_exam(mat_list_str, exam, mat_db):
        if pd.isna(mat_list_str): return False
        mat_db2 = mat_db.set_index('대표이름')['특수검사항목'].copy()

        std_mat_list = convert_to_list_from_str(mat_list_str, mat_db=mat_db)
        s = mat_db2.loc[std_mat_list].astype(str).str.contains(exam)
        return s.any()

    include_exam = df_raw['특수검진물질'].apply(mat_list_include_exam, exam=exam, mat_db=mat_db)
    
    return df_raw[include_exam]


if __name__ == '__main__':
    # mat_db = pd.read_excel('Database_240314.xlsx', index_col=0)
    # print(convert_to_list_from_str('용접흄'), mat_db)

    # print(convert_to_list_from_str('톨루엔,크실렌,2-부톡시에탄올'))
    print(convert_to_list_from_str('야간작업(가), 테스트, (특)퍼클로로에틸렌(PCE), (특)소음(좌)'))