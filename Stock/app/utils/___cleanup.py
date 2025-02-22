import os
import signal
import psutil

def cleanup_python_processes():
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 현재 프로세스는 제외
            if proc.pid == current_pid:
                continue
                
            # Python 프로세스 찾기
            if 'python' in proc.name().lower():
                cmdline = proc.cmdline()
                # Stock 앱 관련 프로세스만 처리
                if any('Stock' in cmd for cmd in cmdline):
                    os.kill(proc.pid, signal.SIGTERM)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue