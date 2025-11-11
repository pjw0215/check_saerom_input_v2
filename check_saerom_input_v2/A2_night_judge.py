import pandas as pd
import pyautogui as pya
from check_saerom_input_v2.saerom_check_module.read_excel_file import read_excel_file
from check_saerom_input_v2.saerom_check_module.make_night_judge import make_night_judge, make_opinion_and_action
from check_saerom_input_v2.saerom_check_module.search_night_cardiovascular_loc import search_night_cardiovascular_loc
from check_saerom_input_v2.B3_special_select_next_module import get_individual_screenshot, wait_and_check_through_individual_screenshot
from JW_modules.activate_window import activate_window
from JW_modules.JW_pya import check_rgb_at_location, input_text
from B5_align_seperators import align_seperators_of_list, align_seperators_of_special

EXCEL_PATH = r"C:\Users\MyCom\Documents\통합 문서1.xlsx"

# 야간 클릭 예시
# 8/12
# 이준영 610820 (야간만)
# 이준영 031117 (야간 위장)
# 주재석 010804 (야간 심혈)

def clear_whole_date_check():
    # 전체 날짜 해제
    ALL_DATE_SELECTED_LOC = (321,57)
    if check_rgb_at_location(location=ALL_DATE_SELECTED_LOC, rgb=(4,34,113), threshold=80):
        pya.click(ALL_DATE_SELECTED_LOC)



def search_individual(date, number, previous_date=None):
    screenshot = pya.screenshot()
    prev_individual_screenshot = get_individual_screenshot(screenshot)

    get_individual_screenshot, wait_and_check_through_individual_screenshot
    
    if date != previous_date:
        input_text((73, 54), date)  # 시작날짜
        input_text((175, 54), date)  # 날짜

    input_text((126, 213), number)  # 시작번호
    input_text((157, 213), number)  # 끝번호

    pya.click(312, 84)  # 조회
    wait_and_check_through_individual_screenshot(prev_individual_screenshot)  # 기다리기


def check_closing(screenshot, unlock=True):
    if check_rgb_at_location(location=(801, 266), rgb=(252, 174, 188), threshold=25, screenshot=screenshot):
        if unlock:
            pya.click(920, 270)
            return False
        else:
            return True
    else:
        return False


def night_judge(excel_path, use_pya_alert=True):
    screenshot = pya.screenshot()
    align_seperators_of_special(first_only=False, screenshot=None)
    align_seperators_of_list(screenshot=screenshot)  # 대상자 리스트 정렬

    df_raw = read_excel_file(excel_path)

    df = df_raw[df_raw['특수검진물질'].str.contains('야간')].copy()  # 야간대상 데이터만 추려진 df 생성
    if len(df.index) == 0:
        pya.alert(text='야간작업 대상이 없습니다.', title='안내', button='확인')
        return
    
    df_night_judge = make_night_judge(df)  # df에 대응되는 인덱스를 가진 df_night_judge 생성
    df_night_judge_opinion = make_opinion_and_action(df_night_judge)  # df_night_judge에 소견과 조치를 추가한 df_night_judge_opinion 생성
    final = pd.concat([df, df_night_judge_opinion], axis=1, join='inner')

    previous_date = None
    pya.click(238, 256)  # 검색 초기화
    clear_whole_date_check()


    for i, idx in enumerate(final.index):

        date = final.loc[idx, '검진일자']
        number = final.loc[idx, '검진번호']

        opinion = final.loc[idx, '소견']
        action = final.loc[idx, '조치']
        code = final.loc[idx, '입력코드']

        # 검색
        search_individual(date, number, previous_date)

        # 판정수정
        screenshot = pya.screenshot()
        is_closing = check_closing(screenshot, unlock=False)
        if is_closing: continue

        opinion_loc = search_night_cardiovascular_loc(screenshot); pya.click(opinion_loc)  # 야간 심혈관 찾기
        input_text((1122, 660), code, delete=True); pya.press('enter')  # 코드
        input_text((1200, 660), opinion, delete=True)  # 소견
        input_text((1200, 695), action, delete=True)  # 조치
        pya.mouseDown(675, 270); pya.mouseUp(675, 270); pya.sleep(1)  # 저장

        previous_date = date

    
    if use_pya_alert:
        pya.alert(text='야간판정 작업을 완료했습니다.', title='안내', button='확인')


if __name__ == '__main__':
    WINDOW_TITLE ='FormDp7Master_S_SV2_한강수병원_11207124_박정우 - [특수결과입력]'
    activate_window(WINDOW_TITLE)
    
    night_judge(EXCEL_PATH)