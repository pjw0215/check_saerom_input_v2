import os, re
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox as msgbox
from gui_logger import LogPane
from A1_check_special_question import check_special_question
from A2_night_judge import night_judge
from A3_check_list import check_list
from A4_fill_special_judge_date_loop import fill_special_judge_date_loop
from A5_general_judge_loop import general_judge_loop
from A6_set_exam_range import set_exam_range
from B3_special_select_next_module import NoNextPersonError
from JW_modules.activate_window import activate_window
from JW_modules.folder_config import cd_here
from JW_modules.JW_json import read_json, to_json

module_folder = cd_here()
OPTION_PATH = os.path.join(module_folder, 'option.json')

def make_window_pattern(window_name: str, hospital: str = "한강수병원") -> str:
    h = re.escape(hospital)
    m = re.escape(window_name)
    return rf"(?=.*{h})(?=.*{m})"

def activate_window_for_addon(window_name):
    window_pattern = make_window_pattern(window_name)
    activate_window(window_pattern, regex=True)


class SooSaeromAddon():

    def __init__(self):
        self.root = Tk()
        self.root.geometry("800x770+50+100")
        self.root.title('한강수 새롬 애드온')

        self.option = read_json(OPTION_PATH) or dict()

        # 현재 실행 중인 스레드 객체 저장용
        self.current_job_thread = None
        
        # 작업 종료 후 알림창 억제 여부 (억제가 필요한 경우 각 메소드에서 True로 입력)
        self._suppress_end_alert = False


        # 파일 선택 프레임 (self.top)
        self.top = LabelFrame(self.root, text='엑셀파일 경로 (2, 3번 기능에서 사용)')
        self.top.pack(fill=BOTH, padx=20, pady=10)
        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=0)

        self.listbox1 = Listbox(self.top, selectmode='single', height=1)
        self.listbox1\
            .grid(row=0, column=0, sticky="we", padx=20, pady=10)
        Button(self.top, text='선택', command=self.select_excel_file)\
            .grid(row=0, column=1, padx=20, pady=10)
        
        self.excel_path = self.option.get('excel_path')
        self.listbox1.insert(END, self.excel_path)
        
        # 기능 선택 프레임 (self.mid)
        PADY = 5
                       
        self.mid = LabelFrame(self.root, text='기능')
        self.mid.pack(fill=BOTH, padx=20, pady=PADY)
        for c in range(3):  # grid: [0]라벨 | [1]시작 | [2]중지
            self.mid.grid_columnconfigure(c, weight=0)

        mid_row = 0

        Label(self.mid, text=f'{mid_row}. 검진일 및 번호 조회')\
            .grid(row=mid_row, column=0, sticky=W, padx=10, pady=PADY)
        Button(self.mid, text="시작", width=6, command=self.start_set_exam_range)\
            .grid(row=mid_row, column=1, sticky=W, padx=10, pady=PADY)
        Label(self.mid, text='ex) 12/5 1001-1123')\
            .grid(row=mid_row, column=2, sticky=W, padx=10, pady=PADY)
        self.exam_range_var = StringVar()
        Entry(self.mid, width=20, textvariable=self.exam_range_var)\
            .grid(row=mid_row, column=3, sticky=W, padx=10, pady=PADY, columnspan=2)
        self.choice_var = StringVar(value="특수")
        ttk.Radiobutton(self.mid, text="특수", value="특수", variable=self.choice_var)\
            .grid(row=mid_row, column=5, sticky=W, padx=10, pady=PADY)
        ttk.Radiobutton(self.mid, text="일반", value="일반", variable=self.choice_var)\
            .grid(row=mid_row, column=6, sticky=W, padx=10, pady=PADY)
        mid_row += 1

        Label(self.mid, text=f'{mid_row}. 특수문진 체크')\
            .grid(row=mid_row, column=0, sticky=W, padx=10, pady=PADY)
        Button(self.mid, text="시작", width=6, command=self.start_check_special_question)\
            .grid(row=mid_row, column=1, sticky=W, padx=10, pady=PADY)
        mid_row += 1
        

        Label(self.mid, text=f'{mid_row}. 야간 판정')\
            .grid(row=mid_row, column=0, sticky=W, padx=10, pady=PADY)
        Button(self.mid, text="시작", width=6, command=self.start_night_judge)\
            .grid(row=mid_row, column=1, sticky=W, padx=10, pady=PADY)
        mid_row += 1
        

        Label(self.mid, text=f'{mid_row}. 특수판정 체크리스트')\
            .grid(row=mid_row, column=0, sticky=W, padx=10, pady=PADY)
        Button(self.mid, text="시작", width=6, command=self.start_check_list)\
            .grid(row=mid_row, column=1, sticky=W, padx=10, pady=PADY)
        mid_row += 1
        

        Label(self.mid, text=f'{mid_row}. 특수판정일 입력')\
            .grid(row=mid_row, column=0, sticky=W, padx=10, pady=PADY)
        Button(self.mid, text="시작", width=6, command=self.start_fill_special_judge_date_loop)\
            .grid(row=mid_row, column=1, sticky=W, padx=10, pady=PADY)
        Label(self.mid, text='⚬ 날짜 (YYYYMMDD)')\
            .grid(row=mid_row, column=2, sticky=W, padx=10, pady=PADY)
        self.special_judge_date_var = StringVar()
        Entry(self.mid, width=10, textvariable=self.special_judge_date_var)\
            .grid(row=mid_row, column=3, sticky=W, padx=10, pady=PADY)
        self.special_overwrite_var = BooleanVar(value=False)
        Checkbutton(self.mid, text='덮어쓰기', variable=self.special_overwrite_var)\
            .grid(row=mid_row, column=4, sticky=W, padx=10, pady=PADY)
        mid_row += 1
        

        Label(self.mid, text=f'{mid_row}. 일반건강검진 판정')\
            .grid(row=mid_row, column=0, sticky=W, padx=10, pady=PADY)
        Button(self.mid, text="시작", width=6, command=self.start_general_judge_loop)\
            .grid(row=mid_row, column=1, sticky=W, padx=10, pady=PADY)
        Label(self.mid, text='⚬ 날짜 (YYYYMMDD)')\
            .grid(row=mid_row, column=2, sticky=W, padx=10, pady=PADY)
        self.general_judge_date_var = StringVar()
        Entry(self.mid, width=10, textvariable=self.general_judge_date_var)\
            .grid(row=mid_row, column=3, sticky=W, padx=10, pady=PADY)
        self.general_overwrite_var = BooleanVar(value=False)
        Checkbutton(self.mid, text='덮어쓰기', variable=self.general_overwrite_var)\
            .grid(row=mid_row, column=4, sticky=W, padx=10, pady=PADY)
        Label(self.mid, text='⚬ 면허번호')\
            .grid(row=mid_row, column=5, sticky=W, padx=10, pady=PADY)
        self.doctor_number = self.option.get('doctor_number')
        self.doctor_number_var = StringVar(value=self.doctor_number)
        Entry(self.mid, width=10, textvariable=self.doctor_number_var)\
            .grid(row=mid_row, column=6, sticky=W, padx=10, pady=PADY)
        mid_row += 1

        
        # 로그 프레임 (self.bottom)
        self.bottom = Frame(self.root)
        self.bottom.pack(fill=BOTH, padx=10, pady=10)
        
        self.text = Text(self.bottom, wrap="none", font=("Consolas", 10))
        # self.logger = LogPane(self.text, logfile="test_log.txt")
        self.logger = LogPane(self.text)
        self.text.pack(fill="both", expand=True, padx=10, pady=(10,0))

        Button(self.bottom, text="지우기", width=10, command=self.clear_log)\
            .pack(side="right", padx=10)


        # 루프
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    
    def select_excel_file(self):
        if self.excel_path:
            initial_dir = os.path.dirname(self.excel_path)
        else:
            initial_dir = None

        get_excel_path = filedialog.askopenfilenames(
            title='파일을 선택하세요', 
            filetypes=[('엑셀 파일', '*.xlsx')], 
            initialdir=initial_dir
        )

        if get_excel_path:
            self.excel_path = get_excel_path[0]
            self.listbox1.delete(0, END) 
            self.listbox1.insert(END, self.excel_path)


    def clear_log(self):
        self.text.delete("1.0", "end")
    

    def _on_start(self):
        start_msg = getattr(self, '_current_start_message', "▶ 작업을 시작합니다...")
        self.logger.write(start_msg)


    def _on_end(self, result, error):
        try:
            if error:
                # ⬇️ NoNextPersonError인지 확인
                if isinstance(error, NoNextPersonError):
                    # ⬇️ 다음 대상이 없어 '정상적으로' 종료된 경우
                    self.logger.write("✔ 작업이 완료되었습니다.")
                    self.logger.write("")
                    if not self._suppress_end_alert:
                        msgbox.showinfo('완료', '작업이 완료되었습니다.')
                else:
                    # ⬇️ 그 외, 예기치 않은 오류로 종료된 경우
                    # 오류 메시지는 이미 threaded_job 내에서 로그에 기록됨
                    self.logger.write(f"✖ 오류가 발생하여 종료되었습니다. : {type(error).__name__}")
                    self.logger.write("")
                    msgbox.showerror('오류', '오류가 발생해 중단되었습니다.')
            else:
                # error가 None인 경우 (함수가 예외 없이 return 했을 경우)
                self.logger.write("✔ 작업이 완료되었습니다.")
                self.logger.write("")
                if not self._suppress_end_alert:
                    msgbox.showinfo('완료', '작업이 완료되었습니다.')
        
        finally:
            # 다음 작업에 영향 없게 항상 원복
            self._suppress_end_alert = False


    def start_set_exam_range(self):
        """검진일 및 검진번호 입력"""
        self._current_start_message = "▶ 검진일 및 번호를 입력 후 조회합니다..."
        activate_window_for_addon('')  # 한강수병원을 검증하기 위함

        exam_range = self.exam_range_var.get().strip()
        if not exam_range:
            msgbox.showwarning('입력 오류', '검진일 및 번호를 입력해주세요.')
            return
        
        choice = self.choice_var.get()

        self._suppress_end_alert = True  # 이 기능의 경우 예외적으로 알람 발생 억제, _on_end 메소드 내에서 다시 False로 원복됨
        
        self.current_job_thread = self.logger.threaded_job(
            set_exam_range, on_start=self._on_start, on_end=self._on_end)\
                (exam_range=exam_range, choice=choice)

    
    def start_check_special_question(self):
        """특수문진 체크 시작 및 버튼 상태 업데이트"""
        self._current_start_message = "▶ 특수문진 체크 작업을 시작합니다..."
        activate_window_for_addon('특수결과입력')
        self.current_job_thread = self.logger.threaded_job(
            check_special_question, on_start=self._on_start, on_end=self._on_end)\
                (use_pya_alert=False)
    
    
    def start_night_judge(self):
        """특수검진 야간판정 입력"""
        self._current_start_message = "▶ 특수검진 야간판정 입력을 시작합니다..."
        activate_window_for_addon('특수결과입력')
        self.current_job_thread = self.logger.threaded_job(
            night_judge, on_start=self._on_start, on_end=self._on_end)\
                (excel_path=self.excel_path, use_pya_alert=False)
        

    def start_check_list(self):
        """판정 체크리스트"""
        self._current_start_message = "▶ 특수검진 체크리스트를 검토합니다..."
        self.current_job_thread = self.logger.threaded_job(
            check_list, on_start=self._on_start)\
                (excel_path=self.excel_path)


    def start_fill_special_judge_date_loop(self):
        """특수검진 판정일 입력"""
        self._current_start_message = "▶ 특수문진 판정일 입력을 시작합니다..."
        activate_window_for_addon('특수결과입력')
        
        special_judge_date = self.special_judge_date_var.get().strip()
        if not special_judge_date:
            msgbox.showwarning('입력 오류', '판정일을 입력해주세요.')
            return
        
        special_overwrite = self.special_overwrite_var.get()
        
        self.current_job_thread = self.logger.threaded_job(
            fill_special_judge_date_loop, on_start=self._on_start, on_end=self._on_end)\
                (judge_date=special_judge_date, overwrite=special_overwrite, use_pya_alert=False)
        

    def start_general_judge_loop(self):
        """일반검진 자동판정"""
        self._current_start_message = "▶ 일반검진 자동판정을 시작합니다..."
        activate_window_for_addon('특수결과입력')

        general_judge_date = self.general_judge_date_var.get().strip()
        if not general_judge_date:
            msgbox.showwarning('입력 오류', '판정일을 입력해주세요.')
            return
        
        self.doctor_number = self.doctor_number_var.get().strip()
        if not self.doctor_number:
            msgbox.showwarning('입력 오류', '면허번호를 입력해주세요.')
            return

        general_overwrite = self.general_overwrite_var.get()
        
        self.current_job_thread = self.logger.threaded_job(
            general_judge_loop, on_start=self._on_start, on_end=self._on_end)\
                (judge_date=general_judge_date, doctor=self.doctor_number, overwrite=general_overwrite, use_pya_alert=False)


    def update_option(self):
        option_changed = False
        
        if bool(self.doctor_number) and (self.doctor_number != self.option.get('doctor_number')):
            self.option['doctor_number'] = self.doctor_number
            option_changed = True

        if bool(self.excel_path) and self.option.get('excel_path') != self.excel_path:
            self.option['excel_path'] = self.excel_path
            option_changed = True
        
        if option_changed:
            to_json(self.option, OPTION_PATH)


    def on_closing(self):
        if msgbox.askokcancel("종료", "종료하시겠습니까?"):
            self.update_option()    
            try:
                self.logger.close()   # ⬅️ 먼저 after 취소
            except Exception:
                pass
            # 한 틱 뒤에 파괴하면 더 안전
            self.root.after(0, self.root.destroy)


if __name__ == '__main__':
    SooSaeromAddon()