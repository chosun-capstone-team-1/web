# app/utils/performance_timer.py
import time
from datetime import datetime
from zoneinfo import ZoneInfo

class InferenceTimer:
    def __init__(self):
        self.log = {}
        self._start = time.time()
        self.log["start_time"] = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y/%m/%d %H:%M:%S")


    def mark(self, key: str):
        now = time.time()
        self.log[key] = round(now - self._start, 2)
        self._start = now

    def get_log(self):
        return {
            "start_time": self.log.get("start_time", "-"),
            "model_load": self.log.get("model_load", "-"),
            "preprocess": self.log.get("preprocess", "-"),
            "inference": self.log.get("inference", "-"),
        }
