import pyautogui as pya
from JW_modules.activate_window import activate_window
from B4_general_judge_once import general_judge_once
from B3_special_select_next_module import special_select_next, NoNextPersonError
import time

JUDGE_DATE = '20251031'
DOCTOR = '박정우'

def general_judge_loop(judge_date, doctor, overwrite=False, use_pya_alert=False):
    while True:
        screenshot = pya.screenshot()
        general_judge_once(judge_date, doctor, screenshot=screenshot, overwrite=overwrite)
        try:
            special_select_next(screenshot, use_pya_alert=use_pya_alert)
            time.sleep(0.05)

        except NoNextPersonError:
            return
        
        except Exception as err:
            return
        

if __name__ == '__main__':
    WINDOW_TITLE ='FormDp7Master_S_SV2_한강수병원_11207124_박정우 - [특수결과입력]'
    activate_window(WINDOW_TITLE)

    general_judge_loop(JUDGE_DATE, DOCTOR, use_pya_alert=True)