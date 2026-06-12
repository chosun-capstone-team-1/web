# app/services/cleanup.py
import os
import time

def clean_old_reports(directory: str = "./temp_uploads/output", expire_seconds: int = 1800):
    now = time.time()
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                last_modified = os.path.getmtime(file_path)
                if now - last_modified > expire_seconds:
                    try:
                        os.remove(file_path)
                        print(f"[정리됨] {file_path}")
                    except Exception as e:
                        print(f"[오류] {file_path} 삭제 실패 → {e}")
