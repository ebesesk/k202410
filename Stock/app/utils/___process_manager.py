import multiprocessing
import atexit
from contextlib import contextmanager
from typing import List
import logging

logger = logging.getLogger(__name__)

class ProcessManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.processes: List[multiprocessing.Process] = []
            cls._instance.pool = None
        return cls._instance
    
    def init_pool(self, processes=None):
        if self.pool is None:
            self.pool = multiprocessing.Pool(processes=processes)
    
    def cleanup_pool(self):
        if self.pool:
            logger.info("Cleaning up process pool...")
            self.pool.close()
            self.pool.join()
            self.pool = None
    
    def cleanup_processes(self):
        logger.info(f"Cleaning up {len(self.processes)} processes...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()
            p.join()
        self.processes.clear()
    
    def cleanup_all(self):
        self.cleanup_pool()
        self.cleanup_processes()

    @contextmanager
    def get_pool(self):
        if self.pool is None:
            self.init_pool()
        try:
            yield self.pool
        finally:
            pass  # 풀은 앱 종료 시에만 정리

    def run_process(self, target, args=()):
        p = multiprocessing.Process(target=target, args=args)
        self.processes.append(p)
        p.start()
        return p

process_manager = ProcessManager()
atexit.register(process_manager.cleanup_all)