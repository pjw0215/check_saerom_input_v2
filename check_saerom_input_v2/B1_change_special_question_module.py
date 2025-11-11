from JW_modules.JW_pya import check_rgb_at_location
import pyautogui as pya

SPECIAL_QUESTION_BACK_START1 = (569, 378)  # 가장 위에 있는 특수문진 배경 위치
SPECIAL_QUESTION_BACK_START2 = (928, 378)
LIST_GAP = 16
QUESTION_COUNT_IN_A_COL = 20

ETC_QUESTION_LOC1 = (793, 741)
ETC_QUESTION_LOC2 = (793, 762)

RGB_SEVERE = (241, 169, 190)
# RGB_MILD = (255, 215, 221)
# RGB_NONE = (255, 255, 255)

LOC_SAVE = (675, 270)


class ChangeSpecialQuestion():

    def __init__(self, screenshot):

        self.changed = False

        for x, y0 in (SPECIAL_QUESTION_BACK_START1, SPECIAL_QUESTION_BACK_START2):
            for n in range(QUESTION_COUNT_IN_A_COL+1):
                location = (x, y0+((n-1)*LIST_GAP))
                self.change_severe_to_mild(location, screenshot)


        for location in (ETC_QUESTION_LOC1, ETC_QUESTION_LOC2):
            self.change_severe_to_mild(location, screenshot, backspace=True)

        if self.changed:
            # print('변경 사항이 있어 저장합니다.')
            pya.click(LOC_SAVE)

    
    def change_severe_to_mild(self, location: tuple, screenshot, backspace=False):
        if check_rgb_at_location(location=location, rgb=RGB_SEVERE, threshold=15, screenshot=screenshot):
            pya.click(location)
            if backspace: pya.press('backspace')
            pya.press('2')

            if not self.changed:
                self.changed = True


if __name__ == '__main__':
    from JW_modules.activate_window import activate_window
    WINDOW_TITLE ='FormDp7Master_S_SV2_한강수병원_11207124_박정우 - [특수결과입력]'
    activate_window(WINDOW_TITLE)
    
    screenshot = pya.screenshot()
    ChangeSpecialQuestion(screenshot)