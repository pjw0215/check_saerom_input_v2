from JW_modules.activate_window import activate_window
from JW_modules.JW_pya import locate_images, locate_image
import pyautogui as pya


def align_seperators_of_list(screenshot=None):  # 특수결과입력의 리스트를 초기화
    SEPERATOR2_IMAGE_PATH = './image/seperator2.png'

    if screenshot is None:
        screenshot = pya.screenshot()

    ref_sep_x_list = [30, 110, 144, 208]  # 원래 실선은 하나씩 -1되어야 하나, 니들이미지 width가 2이여서, pya.center는 +1씩 해야하고, 그러면 이렇게 된다.
    now_sep_loc_list = locate_images(SEPERATOR2_IMAGE_PATH, region=(0, 399, 273-0, 422-399), screenshot=screenshot, confidence=0.98)

    acc_dx = 0
    for i, loc in enumerate(now_sep_loc_list):
        if i > 3: break

        now_center = pya.center(loc)
        now_center_x = now_center.x + acc_dx  # 여태까지 조정중 이동된 거리도 보정
        needed_x = ref_sep_x_list[i]

        if now_center_x != needed_x:
            dx = needed_x - now_center_x  # 이동하게 되는 거리
            if i == 0:  # 첫 선은 약간 왼쪽을 클릭해야 움직여진다
                pya.mouseDown(now_center_x-1, now_center.y)
            else:
                pya.mouseDown(now_center_x, now_center.y)
            pya.move(dx, 0)
            pya.mouseUp()
            pya.sleep(1)
            acc_dx += dx
        else:
            continue


def align_seperators_of_special(first_only=False, screenshot=None):
    SEPERATOR_IMAGE_PATH = './image/seperator.png'
    SPECIAL_FIRST_IMAGE_PATH = './image/special_first.png'

    if screenshot is None:
        screenshot = pya.screenshot()

    # 첫번째 구분선 조정
    loc = locate_image(SEPERATOR_IMAGE_PATH, region=(0, 495, 1680, 535-495), screenshot=screenshot, confidence=0.95)
    now_center = pya.center(loc)
    needed_x = 273
    if now_center.x != needed_x:
        dx = needed_x - now_center.x
        pya.mouseDown(now_center.x, now_center.y)
        pya.move(dx, 0)
        pya.mouseUp()
        pya.sleep(3.5)
    
    if first_only:
        return

    # '특1판정' 클릭
    try:
        locate_image(SPECIAL_FIRST_IMAGE_PATH, screenshot=screenshot)
    except pya.ImageNotFoundException:
        pya.click(808, 244)
        pya.sleep(2)
        screenshot = pya.screenshot()

    # 두번째 구분선 조정
    loc = locate_image(SEPERATOR_IMAGE_PATH, region=(0, 620, 1680, 660-620), screenshot=screenshot, confidence=0.95)
    now_center = pya.center(loc)
    needed_x = 1050
    if now_center.x != needed_x:
        dx = needed_x - now_center.x
        pya.mouseDown(now_center.x, now_center.y)
        pya.move(dx, 0)
        pya.mouseUp()
        pya.sleep(2)
    

if __name__ == '__main__':
    activate_window('특수결과입력', regex=True)
    screenshot = pya.screenshot()

    # align_seperators_of_special(first_only=True, screenshot=screenshot)  # "특수결과입력" 대상자 옆 구분선만
    align_seperators_of_special(first_only=False, screenshot=screenshot)  # "특1판정"의 소견쪽 구분선도
    align_seperators_of_list(screenshot=screenshot)