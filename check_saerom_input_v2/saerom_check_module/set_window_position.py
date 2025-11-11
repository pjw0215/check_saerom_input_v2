import pyautogui as pya

def set_window_position(SECTION1_POSITION, SECTION2_POSITION):

    previous_position = pya.position()

    # 첫번째 구분점 이동
    section1_image = pya.locateOnScreen('./image/judge_section_drag_point.png', region=(0, 510, 700-0, 565-510), grayscale=True, confidence=0.95)
    if pya.center(section1_image)[0] != SECTION1_POSITION: pya.mouseDown(section1_image); pya.moveTo(SECTION1_POSITION); pya.mouseUp(); pya.sleep(2.5)

    # 특1판정 미선택시 클릭
    try:
        first = pya.locateOnScreen('./image/first.png', region=(pya.center(section1_image)[0]+500, 185, 80, 225), grayscale=True, confidence=0.95)
        if not first: pya.click(543+SECTION1_POSITION, 205); pya.sleep(2)
    except pya.ImageNotFoundException:
        pya.click(543+SECTION1_POSITION, 205); pya.sleep(2)

    # 두번째 구분점 이동
    section2_image = pya.locateOnScreen('./image/judge_section_drag_point.png', region=(section1_image.left, 610, pya.size()[0], 665-610), grayscale=True, confidence=0.95)
    if pya.center(section2_image)[0] != SECTION2_POSITION: pya.mouseDown(section2_image); pya.moveTo(SECTION2_POSITION); pya.mouseUp(); pya.sleep(1.5)

    pya.moveTo(previous_position)


if __name__ == '__main__':
    SECTION1_POSITION = 334
    SECTION2_POSITION = 1130
    set_window_position(SECTION1_POSITION, SECTION2_POSITION)