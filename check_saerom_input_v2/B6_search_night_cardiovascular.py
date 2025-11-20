import pyautogui as pya
from JW_modules.JW_pya import check_rgb_at_location, locate_image, locate_images
import os

def search_night_cardiovascular_loc(screenshot):

    try: module_folder = os.path.abspath(os.path.dirname(__file__))  # .py
    except NameError: module_folder = os.getcwd()  # .ipynb

    night_image_path = './image/night.png'
    cardiovascular_image_path = './image/cardiovascular.png'

    def __check_loc_is_cardiovascular(loc):
        try:
            locate_image(cardiovascular_image_path, screenshot=screenshot, region=(1270, loc.y-15, 1368, 30), grayscale=True)
            return True
        except pya.ImageNotFoundException:
            # print('해당 야간판정은 심혈관계 판정이 아닙니다.')
            return False

    def _search_cardiovascular_in_night(night_loc_list):
        for night_loc in night_loc_list:
            loc = pya.center(night_loc)
            if __check_loc_is_cardiovascular(loc):
                return loc  # 찾아진 야간작업 리스트 중 심혈관계에 해당하는게 있으면 첫번째것을 리턴 (하나밖에 없을테니)
            else: continue
        raise Exception('야간을 찾았으나 심혈관계가 없습니다.')

    def _check_is_more_opinion_page(screenshot):
        if not check_rgb_at_location(location=(1670, 553), rgb=(96, 96, 96), threshold=10, screenshot=screenshot):
            return False  # 유해인자 개수가 적어 휠 버튼도 없는 경우
        
        if not check_rgb_at_location(location=(1233, 559), rgb=(128, 128, 128), threshold=10, screenshot=screenshot):
            return False  # 마지막 유해인자 드러끝나서 표 테두리가 끊긴 경우
        
        return True


    while True:
        try:
            night_loc_list = list(locate_images(night_image_path, screenshot=screenshot, region=(1050, 350, 1250-1050, 580-350), grayscale=True))
            loc = _search_cardiovascular_in_night(night_loc_list)
            return loc

        except Exception as err:  # 야간을 찾지못해 night_loc_list를 정의하지 못하거나 / 야간을 찾았으나 심혈관계를 찾지못해 에러가 나는 경우
            if _check_is_more_opinion_page(screenshot):
                # print('페이지가 더 있어 내립니다.\n')
                pya.click(1670, 542)  # 페이지를 아래로 내리기  # 적당만큼만 내려지는지 확인 필요
                screenshot = pya.screenshot()
                continue
            else:
                raise Exception(f'페이지가 더 없어 종료합니다. : {err}')
            

if __name__ == '__main__':
    print(search_night_cardiovascular_loc())