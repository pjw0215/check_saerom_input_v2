import pandas as pd
import numpy as np

class PTAJudge():

    def __init__(self):
        self.adquate_BC_test = None

        self.second_exam = None
        self.exceed_40_at_3_4_6k = None
        self.noise_induced = None
        self.D1 = None
        self.AC25 = None
        self.AC40 = None
        self.BC25 = None
        self.ABG = None
        self.deafness = None
        

    def result(self):
        if (self.second_exam == False) or ((self.exceed_40_at_3_4_6k == False) and (self.AC25 == False)):
            return 'A', '정상'
        
        elif (self.noise_induced == True) and (self.D1 == False) and (self.exceed_40_at_3_4_6k == True) and (self.ABG == False):
            return 'C1', '소음성난청 주의'
        
        elif (self.noise_induced == True) and (self.D1 == False) and (self.exceed_40_at_3_4_6k == True) and (self.ABG == True):
            return 'C1', '혼합성난청 주의'
        
        elif (self.noise_induced == True) and (self.D1 == True) and (self.AC40 == False) and (self.ABG == False):
            return 'D1', '소음성난청'
        
        elif (self.noise_induced == True) and (self.D1 == True) and (self.AC40 == True) and (self.ABG == False) and (self.deafness == False):
            return 'D1', '중등도 소음성난청'

        elif (self.noise_induced == True) and (self.D1 == True) and (self.AC40 == False) and (self.ABG == True) and (self.deafness == False):
            return 'D1', '혼합성난청'
        
        elif (self.noise_induced == True) and (self.D1 == True) and (self.AC40 == True) and (self.ABG == True) and (self.deafness == False):
            return 'D1', '중등도 혼합성난청'
        
        elif ((self.noise_induced == False) or ((self.noise_induced == True) and (self.exceed_40_at_3_4_6k == False)))  and (self.AC25 == True) and (self.AC40 == False) and (self.ABG == False):
            return 'C2', '감각신경성난청 주의'
        
        elif (self.noise_induced == False) and (self.AC25 == True) and (self.AC40 == False) and (self.BC25 == True) and (self.ABG == True):
            return 'C2', '혼합성난청 주의'
        
        elif (self.noise_induced == False) and (self.AC25 == True) and (self.AC40 == False) and (self.BC25 == False) and (self.ABG == True):
            return 'C2', '전음성난청 주의'

        elif ((self.noise_induced == False) or (self.deafness == True)) and (self.AC40 == True) and (self.ABG == False):
            return 'D2', '감각신경성난청'
        
        elif ((self.noise_induced == False) or (self.deafness == True)) and (self.AC40 == True) and (self.BC25 == True) and (self.ABG == True):
            return 'D2', '혼합성난청'
        
        elif ((self.noise_induced == False) or (self.deafness == True)) and (self.AC40 == True) and (self.BC25 == False) and (self.ABG == True):
            return 'D2', '전음성난청'
        
        else: return '판정불가', '판정불가'

class PureToneAudiometry():

    def __init__(self, series_input):
        # 변수 정의1
        self.Lt_AC_col = ['AC 0.5k(Lt)', 'AC 1k(Lt)', 'AC 2k(Lt)', 'AC 3k(Lt)', 'AC 4k(Lt)', 'AC 6k(Lt)']
        self.Rt_AC_col = ['AC 0.5k(Rt)', 'AC 1k(Rt)', 'AC 2k(Rt)', 'AC 3k(Rt)', 'AC 4k(Rt)', 'AC 6k(Rt)']
        self.Lt_BC_col = ['BC 0.5k(Lt)', 'BC 1k(Lt)', 'BC 2k(Lt)', 'BC 3k(Lt)', 'BC 4k(Lt)']
        self.Rt_BC_col = ['BC 0.5k(Rt)', 'BC 1k(Rt)', 'BC 2k(Rt)', 'BC 3k(Rt)', 'BC 4k(Rt)']
        self.BC_Hz = ['0.5k', '1k', '2k', '3k', '4k']  # 골도를 시행하는 주파수
        
        # 변수 정의2
        self.Lt, self.Rt = PTAJudge(), PTAJudge()

        # df 설정
        self.df_Lt, self.df_Rt = self.__split_Lt_and_Rt__(series_input)  # 원본
        self.df_Lt_BC_Hz, self.df_Rt_BC_Hz = self.__make_df_side_BC_Hz__()  # BC를 시행하는 Hz만 남김 (6kHz 제외)
        self.df_Lt_ABG, self.df_Rt_ABG = self.__make_df_side_ABG__()  # BC_Hz를 변경해 999를 수치화, 비어있는 골도를 채우고, ABG도 구함
    
        # 판정에 필요한 변수 정의
        for df_side, df_side_ABG, side in ((self.df_Lt, self.df_Lt_ABG, self.Lt), (self.df_Rt, self.df_Rt_ABG, self.Rt)):
            self.__declare_second_exam__(df_side, side)
            self.__declare_exceed_40_at_3_4_6k__(df_side, side)
            self.__declare_ABG__(df_side_ABG, side)
            self.__declare_noise_induced__(df_side, df_side_ABG, side)
            self.__declare_D1__(df_side, side)
            self.__declare_AC25__(df_side, side)
            self.__declare_AC40__(df_side, side)
            self.__declare_BC25__(df_side_ABG, side)
            self.__declare_deafness__(df_side, side)
    
        # 어느 쪽 골도를 시행해야하는지, 필요한 골도검사가 모두 시행되었나 확인
        BC_should_be_done = self.__which_side_should_be_done_BC_test__()
        if 'Lt' in BC_should_be_done: self.__declare_adequate_BC_test__(self.df_Lt_BC_Hz, self.Lt)
        if 'Rt' in BC_should_be_done: self.__declare_adequate_BC_test__(self.df_Rt_BC_Hz, self.Rt)

    
    # df 설정 메소드
    def __split_Lt_and_Rt__(self, series_input):
        return_list = []
        for side in ['Lt', 'Rt']:
            if side == 'Lt': AC_col, BC_col, remove_str = self.Lt_AC_col, self.Lt_BC_col, '(Lt)'
            else: AC_col, BC_col, remove_str = self.Rt_AC_col, self.Rt_BC_col, '(Rt)'
        
            df_temp1 = series_input[AC_col].copy()  # 기도
            df_temp1.index = [idx.replace('AC ','').replace(remove_str,'') for idx in df_temp1.index]
            df_temp2 = series_input[BC_col].copy()  # 골도
            df_temp2.index = [idx.replace('BC ','').replace(remove_str,'') for idx in df_temp2.index]

            df_temp = pd.concat([df_temp1, df_temp2], axis=1).set_axis(['AC', 'BC'], axis=1)
            df_temp.index.name = side
            df_temp = df_temp.astype(float)
            return_list.append(df_temp)
        return return_list

    # df 정의하기
    def __make_df_side_BC_Hz__(self):
        return self.df_Lt.loc[self.BC_Hz,:], self.df_Rt.loc[self.BC_Hz,:]

    def __make_df_side_ABG__(self):
        return_list = []
        for df_temp in [self.df_Lt_BC_Hz, self.df_Rt_BC_Hz]:
            # 기도 NR의 경우, 최대출력+5는 듣는다고 가정
            df_AC_max = pd.Series([125, 125, 125, 125, 125], index=['0.5k', '1k', '2k', '3k', '4k'])  # 6k는 골도가 없으므로 쓸일이 없다
            df_temp['AC'] = df_temp['AC'].replace(999, np.nan).combine_first(df_AC_max)

            # BC가 공란인 것은 AC와 동일하다고 판단 (AC가 20미만인 경우)
            df_temp['BC'] = df_temp['BC'].combine_first(df_temp['AC'])

            # 골도가 최대출력을 넘은 경우, 최대출력+5는 듣지만, ABG는 모른다고 판단
            freq_list_BC_max_exceeded = df_temp[df_temp['BC'] == 999].index.tolist()  # 최대출력을 넘는 골도 주파수를 기억해둠
            df_BC_max = pd.Series([65, 75, 75, 75, 75], index=['0.5k', '1k', '2k', '3k', '4k']).astype(float)
            df_temp['BC'] = df_temp['BC'].replace(999, np.nan).combine_first(df_BC_max)  # 골도가 최대출력을 넘은경우, 최대출력+5는 듣는다고 가정
            df_temp['ABG'] = df_temp['AC'] - df_temp['BC']
            df_temp.loc[freq_list_BC_max_exceeded, 'ABG'] = np.nan
            return_list.append(df_temp)
        return return_list
    
    # 조건 설정 메소드
    def __declare_second_exam__(self, df_side, side):
        if any([(df_side.loc['2k', 'AC'] >= 30), (df_side.loc['3k', 'AC'] >= 40), (df_side.loc['4k', 'AC'] >= 40)]):
            side.second_exam = True
        else: side.second_exam = False

    def __declare_exceed_40_at_3_4_6k__(self, df_side, side):
        if any([(df_side.loc['3k', 'AC'] >= 40), (df_side.loc['4k', 'AC'] >= 40), (df_side.loc['6k', 'AC'] >= 40)]):
            side.exceed_40_at_3_4_6k = True
        else: side.exceed_40_at_3_4_6k = False
    
    def __declare_ABG__(self, df_side, side):
        # 모든 저주파(0.5k, 1k, 2k)에서 15미만의 개별ABG을 보이면 고주파 개별ABG이 크더라도 전체ABG는 없는 것으로 판단
        if (df_side.loc[['0.5k', '1k', '2k'], 'ABG'] < 15).all():
            # print('저주파 ABG 15미만')
            side.ABG = False
            return

        # 4개의 개별ABG을 검사했다면, 적어도 4-CAB_BE(일단0으로)개 만큼은 개별ABG이 10초과이어야 함. 그렇지 않으면 전체ABG은 없는 것으로 판단
        count_each_ABG_exceed_10 = (df_side['ABG'].dropna() > 10).sum()
        count_considering_freq = len(df_side['ABG'].dropna())
        CAN_BE_IGNORED_COUNT_EVEN_IF_THERE_IS_ABG = 1 if count_considering_freq >=5 else 0  # 4개까지는 모두 있어야 5개부터는 하나는 봐줘

        if not (count_each_ABG_exceed_10 >= count_considering_freq - CAN_BE_IGNORED_COUNT_EVEN_IF_THERE_IS_ABG):
            # print('ABG이 10미만인 개별 주파수 존재')
            side.ABG = False
            return
        
        if df_side['ABG'].mean() >= 15:
            # print('ABG 평균 15이상으로 있음')
            side.ABG = True
            return
        else:
            # print('ABG 없음')
            side.ABG = False
            return

    def __declare_noise_induced__(self, df_side, df_side_ABG, side):
        if side.ABG == True:
            temp = df_side_ABG['BC'].combine_first(df_side_ABG['AC'])  # 골도가 있다면 골도로, 없다면 기도로
            condition1 = temp[['0.5k', '1k']].max() +5 <= temp[['3k', '4k']].max()  # 2k, 6k는 애매한 경우가 있으므로 제외하고 비교
            condition2 = temp[['0.5k', '1k']].mean() <= temp[['3k', '4k']].mean()  # 2k, 6k는 애매한 경우가 있으므로 제외하고 비교
            condition3 = (temp[['2k', '3k', '4k']] >= 25).any()
        else:
            temp = df_side['AC']
            condition1 =  temp[['0.5k', '1k']].max() +5 <= temp[['3k', '4k', '6k']].max()
            condition2 =  temp[['0.5k', '1k']].mean() <= temp[['3k', '4k']].mean()
            condition3 = (temp[['2k', '3k', '4k', '6k']] >= 25).any()

        if condition1 and condition2 and condition3:
            side.noise_induced = True
        else: side.noise_induced = False

    def __declare_D1__(self, df_side, side):
        condition1 = (df_side.loc[['0.5k', '1k', '2k'], 'AC'].mean() >= 30)
        condition2 = (df_side.loc[['3k', '4k', '6k'], 'AC'] >= 50).any()
        if condition1 & condition2:
            side.D1 = True
        else: side.D1 = False

    def __declare_AC25__(self, df_side, side):
        if df_side.loc[['0.5k', '1k', '2k'], 'AC'].mean() >= 25:
            side.AC25 = True
        else: side.AC25 = False

    def __declare_AC40__(self, df_side, side):
        if df_side.loc[['0.5k', '1k', '2k'], 'AC'].mean() >= 40:
            side.AC40 = True
        else: side.AC40 = False

    def __declare_BC25__(self, df_side, side):
        if df_side.loc[['0.5k', '1k', '2k'], 'BC'].mean() >= 25:
            side.BC25 = True
        else: side.BC25 = False
        
    def __declare_deafness__(self, df_side, side):
        # 한측 기준인 6분법 80dB이상
        a, b, c, d = df_side.loc[['0.5k', '1k', '2k', '4k'], 'AC'].tolist()
        hexameter = (a+(2*b)+(2*c)+d)/6
        if hexameter >= 80:
            side.deafness = True
        else: side.deafness = False

    # 필요한 골도 시행 여부
    def __which_side_should_be_done_BC_test__(self):
        BC_should_be_done = []
        if (self.Lt.second_exam == True) or (self.Rt.second_exam == True):
            BC_should_be_done.append('Lt')
            BC_should_be_done.append('Rt')
        else:
            # 나머지는 정상인데, 기도 6k만 40이상인 경우는 골도를 안함
            # 따라서, 2차 대상이 아니라면, 골도는 A 모두 안하고, 6k 때문에 C1 되는 경우도 안해
            if self.Lt.AC25 == True:
                BC_should_be_done.append('Lt')
            if self.Rt.AC25 == True:
                BC_should_be_done.append('Rt')
        return BC_should_be_done

    def __declare_adequate_BC_test__(self, df_side_BC_Hz, side):
        df_side_BC_missed = df_side_BC_Hz.loc[df_side_BC_Hz['AC'] >= 20, 'BC'].isna()
        if df_side_BC_missed.any():
            print(df_side_BC_missed.index.name, ': 골도 누락')
            side.adquate_BC_test = False
        else: side.adquate_BC_test = True