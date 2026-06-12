""
" 이미지 변환때문에 초반에 사용하였으나 나중에 확장할때 쓸 수 있어 남겨놓음 "
""
# from PIL import Image
# import numpy as np

# def convert_exe_to_image(file_path: str) -> Image.Image:
#     with open(file_path, "rb") as f:
#         byte_data = f.read()

#     arr = np.frombuffer(byte_data, dtype=np.uint8)

#     # 최소 1바이트 이상이어야 함
#     if len(arr) == 0:
#         raise ValueError("빈 파일입니다.")

#     # 2차원 정사각형 이미지로 reshape (예: 256x256)
#     size = int(np.ceil(np.sqrt(len(arr))))
#     padded = np.pad(arr, (0, size * size - len(arr)), mode="constant")
#     reshaped = padded.reshape((size, size))

#     return Image.fromarray(reshaped.astype(np.uint8), mode="L")
