import pyautogui as pya
from JW_modules.activate_window import activate_window
from B1_change_special_question_module import ChangeSpecialQuestion
from B3_special_select_next_module import special_select_next, NoNextPersonError
import time

def check_special_question(use_pya_alert=True):
    while True:
        screenshot = pya.screenshot()
        ChangeSpecialQuestion(screenshot)
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
    
    check_special_question()