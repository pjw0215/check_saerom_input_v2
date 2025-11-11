import clipboard
import pyautogui as pya

def write_through_clipboard(input_str):
    clipboard.copy(input_str)
    pya.hotkey('Ctrl', 'V')

def delete_cell_info():
    pya.press('Home'); pya.hotkey('shiftright','shiftleft','end','down'); pya.press('Delete')