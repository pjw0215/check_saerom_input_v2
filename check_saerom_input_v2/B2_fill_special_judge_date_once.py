import pyautogui as pya
from JW_modules.JW_pya import input_text, locate_image
from JW_modules.folder_config import cd_here

def fill_special_judge_date_once(date:str, screenshot=None, overwrite=False):
    cd_here()
    IMAGE_PATH = './image/blank_date.png'

    if overwrite:
        input_text(location=(1118, 930), input_str=date, delete=True)
        pya.click(674, 270)  # 저장
        pya.sleep(0.7)
        return
    
    else:
        try:
            locate_image(image=IMAGE_PATH, screenshot=screenshot, region=(1115, 920, 1195-1115, 945-920))
            input_text(location=(1118, 930), input_str=date, delete=False)
            pya.click(674, 270)  # 저장
            pya.sleep(0.7)
            return

        except pya.ImageNotFoundException:
            return
    

if __name__ == '__main__':
    from JW_modules.activate_window import activate_window
    from B3_special_select_next_module import special_select_next
    
    WINDOW_TITLE ='FormDp7Master_S_SV2_한강수병원_11207124_박정우 - [특수결과입력]'
    activate_window(WINDOW_TITLE)
    
    date = '20251117'
    screenshot = pya.screenshot()
    fill_special_judge_date_once(date, screenshot=screenshot)
    special_select_next(screenshot)