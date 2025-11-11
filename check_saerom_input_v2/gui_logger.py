# gui_logger.py
from tkinter import TclError
import io, sys, threading, queue, subprocess
from contextlib import contextmanager, redirect_stdout, redirect_stderr

class _TkLogStream(io.TextIOBase):
    """print()/tabulate() 출력을 Tk Text에 흘리기 위한 내부 스트림"""
    def __init__(self, q: queue.Queue, logfile: str | None = None, encoding: str = "utf-8"):
        self.q = q
        self._fh = open(logfile, "a", encoding=encoding) if logfile else None
    def write(self, s: str):
        if not s:
            return 0
        self.q.put(s)
        if self._fh:
            self._fh.write(s)
        return len(s)
    def flush(self):
        if self._fh:
            self._fh.flush()
    def close(self):
        try:
            if self._fh:
                self._fh.close()
        finally:
            super().close()


def _pump_pipe(stream, put_fn):
    """subprocess stdout/stderr를 라인단위로 읽어 큐에 투입"""
    for line in iter(stream.readline, ''):
        put_fn(line)
    stream.close()


class LogPane:
    """
    Tkinter Text 위젯에 안전하게 로그를 흘리는 헬퍼.
    - print()/tabulate() 캡처: with log.capture_prints():
    - 외부 스크립트 로그: log.run_subprocess(cmd, env)
    - 임의 메시지: log.write("text")
    - 화면 지우기: log.clear()
    - 종료: log.close()
    """

    def __init__(self, text_widget, logfile: str | None = None, poll_ms: int = 50):
        self.text = text_widget
        self.root = text_widget.winfo_toplevel() # 최상위 Tk 윈도우 객체 저장
        self.q = queue.Queue()
        self.stream = _TkLogStream(self.q, logfile=logfile)
        self.poll_ms = poll_ms
        self._alive = True
        self._after_id = None
        self._is_running = False # 작업 실행 상태 플래그 추가

        # --noconsole 빌드 대비(없어도 무방)
        if not getattr(sys, "stdout", None):
            sys.stdout = io.StringIO()
        if not getattr(sys, "stderr", None):
            sys.stderr = io.StringIO()

        # after 루프 시작
        self._pump()


    def _pump(self):
        if not self._alive:
            return
        
        try:
            if not self.text.winfo_exists():
                return
        except TclError:
            return

        try:
            while True:
                chunk = self.q.get_nowait()
                # 위젯 존재 보장 하에서만 접근
                self.text.insert("end", chunk)
                self.text.see("end")
        except queue.Empty:
            pass
        except TclError:
            # 파괴 타이밍 경쟁 방지
            return

        # ⬅️ after 아이디 보관
        try:
            self._after_id = self.text.after(self.poll_ms, self._pump)
        except TclError:
            # 파괴 직전 경쟁 방지
            self._after_id = None
            return


    def write(self, msg: str):
        """바로 로그창에 쓰기(줄바꿈 자동 처리)"""
        if not msg.endswith("\n"):
            msg += "\n"
        self.q.put(msg)


    def clear(self):
        self.text.delete("1.0", "end")


    @contextmanager
    def capture_prints(self):
        """
        with log.capture_prints():
            # 여기서 나오는 print()/tabulate()가 Text로 들어옴
            your_job()
        """
        with redirect_stdout(self.stream), redirect_stderr(self.stream):
            yield


    def run_subprocess(self, cmd, env=None, text=True):
        """
        외부 스크립트 실행 후 stdout/stderr를 로그창으로 스트리밍.
        반환값: subprocess.Popen
        """
        # (생략: 이 부분은 Tkinter 에러와 직접 관련 없으므로 그대로 둡니다.)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text, env=env)
        if p.stdout:
            threading.Thread(target=_pump_pipe, args=(p.stdout, self.q.put), daemon=True).start()
        if p.stderr:
            threading.Thread(target=_pump_pipe, args=(p.stderr, self.q.put), daemon=True).start()
        self.write(f"[proc] started: {' '.join(map(str, cmd))}")
        return p
    

    def threaded_job(self, func, on_start=None, on_end=None):
        """
        백그라운드 스레드에서 func를 실행하고 print()를 캡처.
        on_start/on_end는 메인 스레드에서 실행됩니다.
        """
        def wrapper(*args, **kwargs):
            if self._is_running:
                self.write("[경고] 작업이 이미 실행 중입니다. 대기합니다.")
                return # 이미 실행 중이면 중복 실행 방지
            
            # 1. 메인 스레드: 시작 전 처리
            self._is_running = True
            if on_start and self.root.winfo_exists():
                self.root.after_idle(on_start) # 메인 스레드에서 즉시 실행

            # 2. 백그라운드 스레드: 작업 실행
            def worker():
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pythoncom = None
                
                job_result = None
                job_error = None

                try:
                    with self.capture_prints():
                        job_result = func(*args, **kwargs)
                except Exception as e:
                    job_error = e
                    self.write(f"[오류 발생] {e}")
                finally:
                    try:
                        if pythoncom:
                            pythoncom.CoUninitialize()
                    except Exception:
                        pass
                
                # 3. 메인 스레드: 작업 완료 후 처리 (안전한 정리)
                if self.root.winfo_exists():
                    # self.root.after()를 사용하여 메인 스레드에서 정리 코드를 실행
                    self.root.after(0, lambda: self._handle_end(on_end, job_result, job_error))

            t = threading.Thread(target=worker, daemon=True)
            t.start()
            return t
        return wrapper
    
    def _handle_end(self, on_end, result, error):
        """작업 완료 후 메인 스레드에서 실행되는 콜백"""
        self._is_running = False
        if on_end:
            try:
                on_end(result, error)
            except Exception as e:
                self.write(f"[정리 오류 발생] {e}")


    def close(self):
        """파일 핸들/after 정리"""
        self._alive = False
        # ⬅️ 예약된 after가 있으면 취소
        try:
            if self._after_id is not None and self.text.winfo_exists():
                self.text.after_cancel(self._after_id)
        except TclError:
            pass
        self._after_id = None
        try:
            self.stream.close()
        except Exception:
            pass