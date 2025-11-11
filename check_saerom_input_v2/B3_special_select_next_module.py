from JW_modules.JW_pya import check_rgb_at_location
import pyautogui as pya
import time

'''
특수결과입력 메뉴에서 다음 사람을 찾고,
다음 사람이 있는 경우 다음으로 넘어가도록하는 모듈
'''

# --- 리스트 좌표 관련 상수 ---
LIST_START = (143, 419)  # 이름이 시작하는 셀의 좌상단 꼭지점 (화면 전체 좌표 기준)
LIST_END = (207, 951)    # 이름 리스트가 보여지는 최하단 (우측 x좌표, 하단 y좌표)
BACKGROUND_GAP = 2       # 표 선(x=0)에서 파란 배경(선택 셀)까지의 x 오프셋
LIST_GAP = 20            # 각 행(사람 이름 셀) 간격(px 단위)
TOTAL_VISIBLE_NAME_COUNT = 26  # 한 화면에 보이는 최대 인원 수

# --- 인적정보 좌표 관련 상수 ---
INDIVIDUAL_START = (441, 46)
INDIVIDUAL_END = (735, 135)

# --- 색상 기준 ---
RGB_SELECTED = (182, 202, 234)  # 선택된 셀의 파란 배경색 RGB
RGB_BORDER = (128, 128, 128)    # 각 셀 경계선(회색)의 RGB

# --- 예외 정의 ---
class NoSelectedPersonError(Exception): pass  # 선택된 사람이 없을 때 발생
class NoNextPersonError(Exception): pass      # 다음 사람이 없을 때 발생


def get_selected_person_index(list_screenshot):
    """
    현재 선택된 사람이 몇 번째 행에 위치하는지 찾아서 반환.
    - list_screenshot: 전체 스크린샷에서 리스트 영역만 crop 한 이미지
    - 반환: 선택된 사람의 인덱스 (1-based)
    - 실패 시: NoSelectedPersonError 발생
    """
    y0 = (LIST_GAP // 2)  # 각 행의 중앙쯤 되는 y좌표 기준
    for n in range(1, TOTAL_VISIBLE_NAME_COUNT+1):
        # n번째 행의 중앙 좌표에 선택 배경색이 있는지 검사
        if check_rgb_at_location(location=(BACKGROUND_GAP, y0+((n-1)*LIST_GAP)),
                                 rgb=RGB_SELECTED, threshold=15, screenshot=list_screenshot):
            # print(f'{n}번째 사람이 선택되어있습니다.')
            return n
    # 반복문 끝날 때까지 못 찾으면 예외 발생
    raise NoSelectedPersonError
        

def check_is_next_person(list_screenshot):
    """
    현재 선택된 사람의 아래에 '다음 사람'이 있는지 확인.
    - 선택된 행의 index를 찾고
    - 그 아래쪽 경계선 위치에 회색(RGB_BORDER)이 있는지 검사
    - True: 다음 사람 있음 / False: 마지막 사람
    """
    index_number = get_selected_person_index(list_screenshot)
    expected_next_border_loc = (0, index_number*LIST_GAP+1)  # 다음 행 시작 경계선 예상 좌표

    if check_rgb_at_location(location=expected_next_border_loc,
                             rgb=RGB_BORDER, threshold=15, screenshot=list_screenshot):
        # print('다음 사람이 있습니다.')
        return True
    else:
        # print('현재가 마지막 사람입니다.')
        return False


def get_list_screenshot(screenshot):
    list_screenshot = screenshot.crop((LIST_START[0], LIST_START[1],
                                       LIST_START[0] + 20, LIST_END[1]))
    return list_screenshot


def get_individual_screenshot(screenshot):
    individual_screenshot = screenshot.crop((INDIVIDUAL_START[0], INDIVIDUAL_START[1],
                                             INDIVIDUAL_END[0], INDIVIDUAL_END[1]))
    return individual_screenshot


def is_selection_blue_contiguous(list_screenshot) -> bool:
    """
    리스트 스크린샷에서 '선택 파란색'이 세로로 한 덩어리(연속)인지 확인.
    - 파란 영역이 둘 이상으로 끊어지면(분할) 아직 로딩 중으로 간주.
    - 검사 x좌표: 파란 배경이 나오는 열 (BACKGROUND_GAP ~ list_img.width-1 중간값 사용)
    """
    
    x = BACKGROUND_GAP  # 파란 배경이 분명히 잡히도록 가운데 쪽 x 사용
    _, height = list_screenshot.size

    block_count = 0
    prev_blue = False
    for y in range(height):
        is_blue_now = check_rgb_at_location(location=(x, y), rgb=RGB_SELECTED, threshold=15, screenshot=list_screenshot)
        if is_blue_now and not prev_blue:
            block_count += 1
        prev_blue = is_blue_now

        if block_count > 1:
            # 파란 블록이 두 덩어리 이상 → 분할됨
            return False
    # block_count == 0 도 허용 (스크롤 중 등) → 이 경우도 안정된 상태로 보되,
    # 선택영역 없음은 상위 로직에서 잡힘. 여기서는 "분할 아님"만 판단.
    return True


def wait_and_check_through_individual_screenshot(prev_individual_screenshot, max_wait_time=5):
    start_time = time.time()
    
    while True:
        new_screenshot = pya.screenshot()
        new_individual_screenshot = get_individual_screenshot(new_screenshot)
        changed = (prev_individual_screenshot.tobytes() != new_individual_screenshot.tobytes())
        
        if changed:
            pya.sleep(0.1)
            return True
        
        # 최대 대기 시간 초과 시 종료
        elif time.time() - start_time > max_wait_time:
            return False
        
        else:
            pya.sleep(0.1)
            continue


def wait_and_check_through_list_screenshot(list_screenshot):
    while True:
        new_screenshot = pya.screenshot()
        new_list_screenshot = get_list_screenshot(new_screenshot)
        changed = (list_screenshot.tobytes() != new_list_screenshot.tobytes())
        if changed and is_selection_blue_contiguous(new_list_screenshot):
            pya.sleep(0.1)
            return True
        else:
            pya.sleep(0.1)
            continue


def special_select_next(screenshot, use_pya_alert=True):
    """
    전체 스크린샷에서 리스트 영역만 잘라 검사하고,
    다음 사람이 있으면 F9 키 입력으로 선택 이동.
    - 다음 사람 없음: NoNextPersonError 발생
    """
    # 리스트 영역만 crop (좌상단, 우상단, 좌하단, 우하단 좌표로 지정)
    list_screenshot = get_list_screenshot(screenshot)
    if check_is_next_person(list_screenshot):
        # print('다음 사람을 선택합니다.')
        pya.press('F9')   # F9 키 입력 → 다음 사람 선택
    else:
        if use_pya_alert:
            pya.alert(text='다음 대상이 없습니다.', title='안내', button='확인')
        raise NoNextPersonError
    
    # 인적정보 변경으로 확인
    prev_individual_screenshot = get_individual_screenshot(screenshot)
    wait_and_check_through_individual_screenshot(prev_individual_screenshot)

    # 리스트영역 변경으로 확인
    # wait_and_check_through_list_screenshot(list_screenshot)
    

if __name__ == '__main__':
    from JW_modules.activate_window import activate_window
    WINDOW_TITLE ='FormDp7Master_S_SV2_한강수병원_11207124_박정우 - [특수결과입력]'
    activate_window(WINDOW_TITLE)

    # 테스트: 최대 3번 다음 사람 이동 시도
    for i in range(30):
        screenshot = pya.screenshot()
        special_select_next(screenshot)
