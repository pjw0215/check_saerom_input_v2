import pyautogui as pya
try:
    from pya_module import delete_cell_info, write_through_clipboard
except:
    from .pya_module import delete_cell_info, write_through_clipboard

# 날짜 입력
def __input_date(date_):
    pya.click(72, 54)
    delete_cell_info()
    write_through_clipboard(date_)

    pya.click(174, 54)
    delete_cell_info()
    write_through_clipboard(date_)

# 검진번호 입력
def __input_number(start_number, end_number):
    pya.click(125, 213)
    delete_cell_info()
    write_through_clipboard(start_number)

    pya.click(158, 213)
    delete_cell_info()
    write_through_clipboard(end_number)

# 날짜와 검진번호로 찾기 (previous_date를 통해 검색날짜가 이전날짜와 일치하는 경우, 날짜는 새로 입력하지 않게 함)
def search_individual(date_, start_number, end_number, SECTION1_POSITION, delete_name_birth=True, previous_date=None):
    if delete_name_birth:
        pya.click(59, 113); delete_cell_info()  # 이름 삭제
        pya.click(59, 131); delete_cell_info()  # 생년월일 앞자리 삭제

    if pya.pixelMatchesColor(SECTION1_POSITION + 10, 61, (76, 97, 152), tolerance=10) == True: pya.click(SECTION1_POSITION + 10, 61)  # 전체기간 해제
    if date_ != previous_date: __input_date(date_)  # 날짜 입력
    __input_number(start_number, end_number)  # 번호 입력
    pya.click(SECTION1_POSITION + 46, 85)  # 조회 클릭
    pya.sleep(1)  # 대기


if __name__ == '__main__':
    date_ = '20240604'
    number = '496'
    SECTION1_POSITION = 334
    search_individual(date_, number, SECTION1_POSITION)