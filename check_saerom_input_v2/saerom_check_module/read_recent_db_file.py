import re
import os
import pandas as pd

def read_recent_db_file(folder=None):
    if folder == None:
        try: module_folder = os.path.abspath(os.path.dirname(__file__))  # .py
        except NameError: module_folder = os.getcwd()  # .ipynb

        db_file_list = list(filter(re.compile('^Database_[0-9]{6}.*.xlsx$').match, os.listdir(module_folder)))
        recent_db_file = sorted(db_file_list)[-1]
        recent_db_path = os.path.join(module_folder, recent_db_file)
        print('## DB파일 로드 :', recent_db_path, '##')
        df = pd.read_excel(recent_db_path, index_col=0)
    else:
        db_file_list = list(filter(re.compile('^Database_[0-9]{6}.*.xlsx$').match, os.listdir(folder)))
        recent_db_file = sorted(db_file_list)[-1]
        recent_db_path = os.path.join(folder, recent_db_file)
        print('## DB파일 로드 :', recent_db_path, '##')
        df = pd.read_excel(recent_db_path, index_col=0)
    return df

if __name__ == '__main__':
    read_recent_db_file()