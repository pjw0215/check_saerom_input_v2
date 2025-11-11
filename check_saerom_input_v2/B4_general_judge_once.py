import pyautogui as pya
from JW_modules.JW_pya import input_text, locate_image
from JW_modules.folder_config import cd_here

def general_judge_once(date:str, doctor:str, screenshot=None, overwrite=False):
    cd_here()

    JUDGE_IMAGE_PATH = './image/blank_general_judge.png'
    DATE_IMAGE_PATH = './image/blank_date.png'
    DATE_IMAGE_PATH2 = './image/blank_date2.png'
    DOCTOR_IMAGE_PATH = './image/blank_doctor.png'

    general_judge = False
    fill_date = False
    fill_doctor = False
    
    if not screenshot:
        screenshot = pya.screenshot()

    # 자동판정
    try:
        locate_image(image=JUDGE_IMAGE_PATH, screenshot=screenshot, region=(419, 314, 495-419, 338-314))
        pya.click(652, 273)
        pya.sleep(1)
        general_judge = True
        screenshot = pya.screenshot()  # 자동판정 하면서 판정일, 판정의사가 채워질 수 있으므로, 자동판정 후 다시 스샷을 찍는다.
    except pya.ImageNotFoundException:
        pass

    # 판정일 입력
    if overwrite:
        input_text(location=(326, 272), input_str=date, delete=True)
        pya.press('ENTER')
        fill_date = True

    else:
        try:
            locate_image(image=DATE_IMAGE_PATH, screenshot=screenshot, region=(324, 264, 402-324, 282-264))
            input_text(location=(326, 272), input_str=date, delete=False)  # True로 해야 입력이 제대로 되나..??
            pya.press('ENTER')
            fill_date = True
        except pya.ImageNotFoundException:
            pass

        if fill_date == False:
            try:
                locate_image(image=DATE_IMAGE_PATH2, screenshot=screenshot, region=(324, 264, 402-324, 282-264))
                input_text(location=(326, 272), input_str=date, delete=False)  # True로 해야 입력이 제대로 되나..??
                pya.press('ENTER')
                fill_date = True
            except pya.ImageNotFoundException:
                pass


    # 판정의사 입력
    try:
        locate_image(image=DOCTOR_IMAGE_PATH, screenshot=None, region=(487, 287, 547-487, 307-287))
        input_text(location=(490, 297), input_str=doctor, delete=True)
        pya.press('ENTER')
        fill_doctor = True
    except pya.ImageNotFoundException:
        pass

    # 저장
    if general_judge or fill_date or fill_doctor:
        pya.click(708, 273)
        pya.sleep(0.7)
    

if __name__ == '__main__':
    from JW_modules.activate_window import activate_window
    from B3_special_select_next_module import special_select_next

    WINDOW_TITLE ='FormDp7Master_S_SV2_한강수병원_11207124_박정우 - [특수결과입력]'
    activate_window(WINDOW_TITLE)
    
    date = '20251031'
    doctor = '박정우'
    screenshot = pya.screenshot()
    general_judge_once(date, doctor, screenshot=screenshot, overwrite=False)
    # special_select_next(screenshot)