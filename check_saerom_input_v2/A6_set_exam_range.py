import re
import pyautogui as pya
from datetime import datetime
from JW_modules.JW_pya import input_text, check_rgb_at_location, locate_image
from JW_modules.activate_window import activate_window, WindowActivationError

LOC_INFO = {
    '특수결과입력': {
        'start_date':  (72, 53),
        'end_date':    (174, 53),
        'start_number':(125, 212),
        'end_number':  (158, 212),
    },

    '데이터 엑셀다운': {
        'start_date':  (402, 118),
        'end_date':    (512, 118),
        'start_number':(1026, 118),
        'end_number':  (1073, 118),
    },

    '특수검진 마감 및 전송관리': {
        'start_date':  (70, 118),
        'end_date':    (184, 118),
        'start_number':(537, 139),
        'end_number':  (586, 139),
    },

    '공단검진 마감 및 청구관리': {
        'start_date':  (70, 118),
        'end_date':    (184, 118),
        'start_number':(709, 118),
        'end_number':  (759, 118),
    },
}

# 특수검진결과 관련 정보
SPECIAL_WHOLE_DATE_SELECT_LOC = (320, 57)
SELECTED_RGB = (75, 96, 151)
EXAM_OPEN_CHECK_LOC = (171, 149)
CHECKED_RGB = (96, 96, 96)
RESET_LOC = (238, 256)
EXAM_OPEN_LOC = (191, 152)
SPECIAL_LOC = (66, 344)
GENERAL_LOC = (66, 151)

# 데이터 다운로드 관련 정보
DOWN_WHOLE_DATE_SELECT_LOC = (1131, 153)
DOWN_SPECIAL_OPTION_LOC = (1131, 172)


def parse_exam_range(text: str):
    """
    '10/25 7001-7025' → ('20251025', '7001', '7025')
    단, 오늘보다 미래 날짜면 연도를 1년 전으로 보정.
    """
    today = datetime.today()

    # 정규식으로 분리 (10/25, 7001, 7025)
    m = re.match(r'(\d{1,2})/(\d{1,2})\s+(\d+)[-~](\d+)', text.strip())
    if not m:
        raise ValueError(f"형식이 올바르지 않습니다: {text}")

    month, day, start_no, end_no = map(int, m.groups())

    # 올해 기준 날짜 생성
    candidate = datetime(year=today.year, month=month, day=day)

    # 미래면 1년 전으로 보정
    if candidate > today:
        candidate = candidate.replace(year=today.year - 1)

    date_str = candidate.strftime("%Y%m%d")
    return date_str, str(start_no), str(end_no)


def set_exam_range(exam_range:str, choice:str):
    activated_title = None
    for title in LOC_INFO.keys():
        try:
            activate_window(title, regex=True)
            activated_title = title
            break
        except WindowActivationError:
            continue

    if activated_title is None:
        raise WindowActivationError('창을 찾을 수 없습니다!')
    
    if title == '특수결과입력':
        screenshot = pya.screenshot()

        # 전체 검색 해제
        if check_rgb_at_location(SPECIAL_WHOLE_DATE_SELECT_LOC, rgb=SELECTED_RGB, threshold=15, screenshot=screenshot):
            print('전체선택을 해제합니다.')
            pya.click(SPECIAL_WHOLE_DATE_SELECT_LOC)

        # 검진 종류 열려있으면 닫기
        if not check_rgb_at_location(EXAM_OPEN_CHECK_LOC, rgb=CHECKED_RGB, threshold=15, screenshot=screenshot):
            print('검진종류 선택창을 닫습니다.')
            pya.click(EXAM_OPEN_LOC)

        if choice == '특수':
            pya.click(RESET_LOC)
            pya.click(EXAM_OPEN_LOC)
            pya.click(SPECIAL_LOC)
            pya.click(EXAM_OPEN_LOC)
        else:
            pya.click(RESET_LOC)
            pya.click(EXAM_OPEN_LOC)
            pya.click(GENERAL_LOC)
            pya.click(EXAM_OPEN_LOC)

    elif title == '데이터 엑셀다운':
        screenshot = pya.screenshot()
        
        option_select_error = False
        try:
            locate_image('./image/down_option_select.png', screenshot=screenshot)
            locate_image('./image/down_option_select2.png', screenshot=screenshot)
        except pya.ImageNotFoundException:
            option_select_error = True
            pass

        whole_data_checked = check_rgb_at_location(DOWN_WHOLE_DATE_SELECT_LOC, rgb=SELECTED_RGB, threshold=15, screenshot=screenshot)
        down_special_checked = check_rgb_at_location(DOWN_SPECIAL_OPTION_LOC, rgb=SELECTED_RGB, threshold=15, screenshot=screenshot)
        if not (whole_data_checked and down_special_checked):
            option_select_error = True

        if option_select_error:
            raise Exception('데이터 엑셀다운 옵션선택을 확인하세요')


    exam_date, start_number, end_number = parse_exam_range(exam_range)
    input_text(LOC_INFO[title]['start_date'], exam_date, delete=True)
    input_text(LOC_INFO[title]['end_date'], exam_date, delete=True)
    input_text(LOC_INFO[title]['start_number'], start_number, delete=True)
    input_text(LOC_INFO[title]['end_number'], end_number, delete=True)

    pya.press('F2')
    return


if __name__ == '__main__':
    exam_range = '01/25 7001-7025'
    set_exam_range(exam_range)