## app/utils/file_processing.py
""
" 전처리 : 확장자 추가 시 유연하게 확장하기 위한 파일"
""
from PIL import Image
import numpy as np
import os
import pandas as pd
import subprocess
from pathlib import Path


def convert_exe_to_image(file_path):
    with open(file_path, 'rb') as f:
        byte_data = f.read()

    max_size = 256 * 256
    byte_data = byte_data[:max_size] + b'\x00' * max(0, max_size - len(byte_data))
    byte_arr = np.frombuffer(byte_data, dtype=np.uint8)
    image_arr = byte_arr.reshape((256, 256))
    return Image.fromarray(image_arr, mode='L')

def convert_hwp_to_image(file_path):
    with open(file_path, 'rb') as f:
        byte_data = f.read()
    max_size = 256 * 256
    byte_data = byte_data[:max_size] + b'\x00' * max(0, max_size - len(byte_data))
    byte_arr = np.frombuffer(byte_data, dtype=np.uint8)
    image_arr = byte_arr.reshape((256, 256))
    return Image.fromarray(image_arr, mode='L')

def convert_docx_to_image(file_path):
    with open(file_path, 'rb') as f:
        byte_data = f.read()
    max_size = 256 * 256
    byte_data = byte_data[:max_size] + b'\x00' * max(0, max_size - len(byte_data))
    byte_arr = np.frombuffer(byte_data, dtype=np.uint8)
    image_arr = byte_arr.reshape((256, 256))
    return Image.fromarray(image_arr, mode='L')

def convert_xlsx_to_image(file_path):
    with open(file_path, 'rb') as f:
        byte_data = f.read()
    max_size = 256 * 256
    byte_data = byte_data[:max_size] + b'\x00' * max(0, max_size - len(byte_data))
    byte_arr = np.frombuffer(byte_data, dtype=np.uint8)
    image_arr = byte_arr.reshape((256, 256))
    return Image.fromarray(image_arr, mode='L')


def extract_pdf_features(file_path):
    # 현재 파일 기준으로 pdfid.py 경로 지정
    BASE_DIR = Path(__file__).resolve().parent
    pdfid_path = os.path.join(BASE_DIR, "pdfid.py")

    # 분석에 사용할 키워드
    keywords = [
        '/JavaScript', '/JS', '/Launch', '/OpenAction', '/AA',
        '/AcroForm', '/XFA', '/URI', '/EmbeddedFile', '/RichMedia'
    ]
    features = dict.fromkeys(keywords, 0)

    # subprocess 실행
    result = subprocess.run(
        ['python3', pdfid_path, file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 분석 실패 로그 출력 (디버깅용)
    if result.returncode != 0:
        print("[PDFID ERROR]")
        print(result.stderr)

    # 결과 파싱
    for line in result.stdout.splitlines():
        for kw in keywords:
            if kw in line:
                try:
                    count = int(line.strip().split()[-1].split('(')[0])
                    features[kw] = count
                except:
                    features[kw] = 0

    return features



# 확장자별로 (변환 함수, resize 크기) 관리
CONVERTER_MAP = {
    "exe": (convert_exe_to_image, (256, 256)),
    "pdf": (extract_pdf_features, None),
    "hwp": (convert_hwp_to_image, (256, 256)),  
    "xlsx": (convert_hwp_to_image, (256, 256)),  
    "docx": (convert_hwp_to_image, (256, 256))
}

