import pyautogui as pya

def check_closing_and_unlock(SECTION1_POSITION):
    if pya.pixelMatchesColor(920, 229, (252, 174, 188), tolerance=10):
        pya.click(SECTION1_POSITION+644, 236)
        pya.click(962, 693)


if __name__ == '__main__':
    SECTION1_POSITION = 330
    check_closing_and_unlock(SECTION1_POSITION)