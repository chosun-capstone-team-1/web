## app/services/ai_rf_reports.py
import matplotlib
matplotlib.use("Agg")  # <- GUI 백엔드 막기
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from fpdf import FPDF
from datetime import datetime
import hashlib
import textwrap
import platform
import os
import re
import pytz
from io import BytesIO
from matplotlib import rcParams
from app.utils.model_info import get_model_performance_score
from app.utils.model_info import extract_model_info 
from matplotlib.transforms import blended_transform_factory

from openai import OpenAI
from dotenv import load_dotenv
from fastapi import UploadFile


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system = platform.system()
if system == "Darwin":  # macOS
    matplotlib.rcParams["font.family"] = "AppleGothic"
elif system == "Windows": # windows
    matplotlib.rcParams["font.family"] = "Malgun Gothic"
else:
    nanum_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    if os.path.exists(nanum_path):
        fm.fontManager.addfont(nanum_path)
        font_name = fm.FontProperties(fname=nanum_path).get_name()
        matplotlib.rcParams["font.family"] = font_name
    else:
        matplotlib.rcParams["font.family"] = "DejaVu Sans"


matplotlib.rcParams["axes.unicode_minus"] = False

# 캐싱 저장소
_gpt_cache = {}


class CustomPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Noto", "", 10)
        self.set_text_color(100)
        page_num = f"- {self.page_no()} -"
        self.cell(0, 10, page_num, align='C')


def generate_rf_pdf_report(file: UploadFile, result: dict, model_name=None):
    return generate_final_pdf_report(file, result, model_name)


def ask_gpt_for_recommendations(summary_text: str) -> str:
    if summary_text in _gpt_cache:
        return _gpt_cache[summary_text]

    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
다음은 악성코드 탐지 요약입니다:

{summary_text}

위 내용을 참고하여 다음 항목을 간단히 정리해주세요:
1. 보안 위협 여부 (한 줄로 요약)
2. 권장 보안 조치 (리스트 형식)
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    clean_text = response.choices[0].message.content.strip()

    replacements = [
        ("**", ""),
        ("##", ""),
        ("__", ""),
        ("--", "-"),
    ]
    for old, new in replacements:
        clean_text = clean_text.replace(old, new)

    _gpt_cache[summary_text] = clean_text.strip()
    return clean_text.strip()


# 모델 성능 점수 자동 추출 : F1/Recall/Precision, Benign/Malware 클래스 정확도 시각화 함수
def create_combined_model_performance_chart(perf):
    import matplotlib.pyplot as plt

    precision = perf["Precision"]
    recall = perf["Recall"]
    f1_score = perf["F1-Score"]
    benign = perf["Benign"]
    malware = perf["Malware"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3), gridspec_kw={'wspace': 0.8})

    metrics = ['Precision', 'Recall', 'F1-Score']
    scores = [precision, recall, f1_score]
    colors1 = ['#A5C9FF', '#9BDCFD', '#CBA4F5']
    ax1.barh(metrics, scores, color=colors1)
    ax1.set_xlim(0, 100)
    ax1.set_xlabel("%")
    ax1.set_title("F1 / Precision / Recall", fontsize=12, y=1.05)

    for i, v in enumerate(scores):
        ax1.text(102, i, f"{v:.2f}%", va='center', fontsize=9)

    labels = ['Benign', 'Malware']
    values = [benign, malware]
    colors2 = ['#72A7F9', '#B295F8']
    bars = ax2.bar(labels, values, color=colors2)
    ax2.set_ylim(0, 110)
    ax2.set_ylabel("정확도 (%)")
    ax2.set_title("Accuracy by Class", fontsize=12, y=1.05)

    for i, v in enumerate(values):
        ax2.text(i, 102, f"{v:.2f}%", ha='center', fontsize=9)

    chart_path = "combined_performance_chart.png"
    plt.subplots_adjust(bottom=0.2)
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# 간트 차트 스타일 로그 타임라인 시각화 함수
def create_log_gantt_chart(model_load, preprocess, inference):
    try:
        total = model_load + preprocess + inference
        segments = [model_load, preprocess, inference]
        labels = ['모델 로딩', '전처리', '추론']
        colors = ['#93C5FD', '#FDE68A', '#FCA5A5']

        fig, ax = plt.subplots(figsize=(6.5, 1.5))
        start = 0
        starts = []

        for i in range(len(segments)):
            duration = max(segments[i], 0.02)
            ax.broken_barh([(start, duration)], (0, 12), facecolors=colors[i])
            ax.text(start, -1.5, f"{start:.2f}s", ha='center', fontsize=7, color='gray')
            starts.append(start)
            start += duration

        ax.text(start, -1.5, f"{start:.2f}s", ha='center', fontsize=7, color='gray')

        for i in range(len(segments)):
            raw_duration = segments[i]
            duration = max(raw_duration, 0.02)
            start = starts[i]
            center_x = start + duration / 2
            label_text = f"{labels[i]} ({raw_duration:.2f}s)"

            y_text = 30 if labels[i] == "모델 로딩" else 23 if labels[i] == "전처리" else 17

            ax.annotate('', xy=(center_x, 6), xytext=(center_x, y_text - 1),
                        arrowprops=dict(arrowstyle="->", lw=1.2, color='black'))
            ax.text(center_x, y_text, label_text,
                    ha='left', va='bottom', fontsize=8, color='black')

        ax.set_xlim(0, max(total + 0.2, 1.0))
        ax.set_ylim(-2, 30)
        ax.set_yticks([])
        ax.set_xlabel("Time (sec)", fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        chart_path = "gantt_log_chart.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    except Exception as e:
        print(f"[Gantt Chart 생성 실패] {e}")
        return None



#def generate_final_pdf_report(file: UploadFile, result: dict, model_name=None):
def generate_final_pdf_report(file: UploadFile, result: dict, model_name=None, custom_filename: str = None):

    model_type = result.get("model_info", {}).get("type") or model_name or "Unknown"

    """
    출력 아래와 같이 나와야 함
    result = {
        "confidence": 0.87,
        "accuracy": 95.61,
        "result": "악성",
        "log": {
            "start_time": "2025/04/07 14:22:10",
            "model_load": 0.91,
            "preprocess": 0.72,
            "inference": 1.07
        },
        "model_info": {
            "type": "CNN",
            "input": "Grayscale, 256x256",
            "train_size": "20,000"
        }
    }
    """
    def create_pie_chart(malicious_percent):
        benign_percent = 100 - malicious_percent
        labels = ['악성 : {:.1f}%'.format(malicious_percent), '정상 : {:.1f}%'.format(benign_percent)]
        sizes = [malicious_percent, benign_percent]
        colors = ['#C084FC', '#93C5FD']

        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        ax.pie(sizes, labels=['Malicious', 'Benign'], colors=colors,
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        ax.axis('equal')
        plt.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)

        chart_path = "pie_chart.png"
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()
        return chart_path

    contents = file.file.read()
    file_stream = BytesIO(contents)
    file_hash = hashlib.sha256(contents).hexdigest()
    file_name = os.path.basename(file.filename).replace("/", "_").replace("\\", "_")
    extension = os.path.splitext(file_name)[1]
    file_size = f"{len(contents) / 1024 / 1024:.2f} MB"

    confidence = result["confidence"]
    test_acc = result["accuracy"]
    detection_result = result["result"]

    now = datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y/%m/%d %H:%M:%S")
    malicious_percent = round(confidence * 100, 1)
    chart_path = create_pie_chart(malicious_percent)

    pdf = CustomPDF()  
    pdf.alias_nb_pages() # 하단 페이지 개수
    pdf.add_page()

    font_dir = os.path.join(os.path.dirname(__file__), "../assets/fonts")
    pdf.add_font("Noto", "", os.path.join(font_dir, "NotoSansKR-Regular.ttf"), uni=True)
    pdf.add_font("Noto", "B", os.path.join(font_dir, "NotoSansKR-Bold.ttf"), uni=True)

    logo_path = os.path.join(os.path.dirname(__file__), "../assets/images/report_logo.png")
    pdf.image(logo_path, x=10, y=10, w=45)
    pdf.set_xy(150, 10)
    pdf.set_font("Noto", "", 9)
    pdf.multi_cell(0, 6, "65, Chosundae 5-gil, Dong-gu\nSouth Korea, Gwangju 61452\nhttps://ict.chosun.ac.kr", align='R')

    pdf.set_xy(10, 38)
    pdf.set_font("Noto", "B", 18)
    pdf.cell(0, 10, "Malicious File Analysis Report", align='L')
    pdf.ln(10)
    pdf.set_font("Noto", "", 12)
    pdf.cell(0, 10, now)
    pdf.ln(12)

    pdf.set_font("Noto", "B", 14)
    pdf.cell(0, 10, "1. 파일 분석 정보 (File Analysis Information)")
    pdf.ln(12)
    pdf.set_font("Noto", "", 12)
    pdf.set_x(15)
    table_data = [
        ["File name", file_name],
        ["File Size", file_size],
        ["Extension", extension],
        ["SHA-256 Hash", file_hash]
    ]
    for row in table_data:
        pdf.set_x(15)
        pdf.cell(40, 10, row[0], border=1)
        pdf.cell(150, 10, row[1], border=1)
        pdf.ln()
    pdf.ln(8)

    pdf.set_font("Noto", "B", 14)
    pdf.cell(0, 10, "2. 탐지 결과 요약 (Summary of Detection Results)")
    pdf.ln(10)
    pdf.set_font("Noto", "", 12)
    pdf.cell(0, 10, f"탐지 결과 : {detection_result}")
    pdf.ln(8)
    pdf.cell(0, 10, f"신뢰도 (Confidence) : {test_acc:.2f} %")
    pdf.ln(8)

    pdf.set_text_color(100)
    pdf.set_font("Noto", "", 10)
    pdf.multi_cell(0, 8, "※ 본 보고서에서의 신뢰도는 모델의 성능을 의미합니다.")
    pdf.set_text_color(0)
    pdf.set_font("Noto", "", 12)
    pdf.ln(10)

    image_width = 100
    x_centered = (pdf.w - image_width) / 2
    pdf.image(chart_path, x=x_centered, w=image_width)
    pdf.ln(10)

    pdf.cell(0, 10, f"해당 \"{file_name}\" 파일은 {detection_result}으로 탐지되었으며,", align='C')
    pdf.ln(8)
    pdf.cell(0, 10, f"{malicious_percent:.1f}%의 탐지 확률을 기반으로 판단됩니다.", align='C')
    pdf.ln(10)

    pdf.set_text_color(100)
    pdf.set_font("Noto", "", 10)
    lines = [
        "※ 본 보고서에서는 악성 및 정상 중 예측 확률이 더 높은 값을 기준으로 판별하며,",
        "악성 확률이 60% 이상일 경우 '악성'으로 판별합니다."
    ]
    for line in lines:
        pdf.cell(0, 6, line, align='C')
        pdf.ln(6)
    pdf.set_text_color(0)
    pdf.ln(8)

    model_info = extract_model_info(extension)
    model_type = model_info.get("type", "Unknown")
    input_info = model_info.get("input", "-")
    train_size = model_info.get("train_size", "-")

    pdf.set_font("Noto", "B", 14)
    pdf.cell(0, 10, "3. 분석 환경 (AI Models Used)")
    pdf.ln(10)
    pdf.set_font("Noto", "", 12)
    pdf.multi_cell(0, 8,
        f"{model_type} 기반의 머신러닝 모델을 사용하여 파일을 분석하였습니다.\n"
        f"해당 모델은 약 {train_size}개의 학습 데이터를 기반으로 학습되었으며,\n"
        f"{input_info} 형태로 전처리된 데이터를 사용합니다.\n"
        f"모델의 테스트 정확도는 {test_acc:.2f}%입니다."
    )
    pdf.ln(6)
    # 모델 성능 점수 자동 추출 : F1/Recall/Precision, Benign/Malware 클래스 정확도 시각화 함수
    perf = get_model_performance_score(extension)
    combined_chart_path = create_combined_model_performance_chart(perf)

    # 3. PDF에 삽입
    if os.path.exists(combined_chart_path):
        pdf.image(combined_chart_path, x=pdf.l_margin + 10, w=pdf.w - 2 * (pdf.l_margin + 10))
        pdf.ln(10)

    # 4. 이미지 파일 정리
    if os.path.exists(combined_chart_path):
        os.remove(combined_chart_path)


    log = result.get("log", {})
    pdf.set_font("Noto", "B", 14)
    pdf.cell(0, 10, "4. 분석 로그 요약 (Analysis Log Summary)")
    pdf.ln(10)
    pdf.set_font("Noto", "", 12)
    pdf.multi_cell(0, 8,
        f"- 분석 시작 시간: {log.get('start_time', '-')}\n"
        f"- 모델 로딩 시간: {log.get('model_load', '-')}초\n"
        f"- 파일 전처리 시간: {log.get('preprocess', '-')}초\n"
        f"- 추론 시간: {log.get('inference', '-')}초"
    )
    pdf.ln(8)
    gantt_chart_path = None
    try:
        model_load = float(log.get('model_load') or 0.0)
        preprocess = float(log.get('preprocess') or 0.0)
        inference = float(log.get('inference') or 0.0)

        gantt_chart_path = create_log_gantt_chart(model_load, preprocess, inference)

        if gantt_chart_path and os.path.exists(gantt_chart_path):
            pdf.image(gantt_chart_path, x=pdf.l_margin + 10, w=pdf.w - 2 * (pdf.l_margin + 10))
            pdf.ln(10)
    except Exception as e:
        print(f"[PDF] 로그 시각화 실패: 모델 로딩/전처리/추론 시각화 중 오류\n→ {e}")
    finally:
        if gantt_chart_path and os.path.exists(gantt_chart_path):
            os.remove(gantt_chart_path)




    pdf.set_font("Noto", "B", 14)
    pdf.cell(0, 10, "5. 대응 및 권장 조치 (Response and Recommended Actions)")
    pdf.ln(10)
    pdf.set_font("Noto", "", 12)
    # GPT API 호출을 위한 요약 구성
    summary_text = f"""
    탐지 결과: {detection_result}
    신뢰도: {test_acc:.2f}%
    악성 확률: {confidence * 100:.1f}%
    모델: {model_type}
    입력형태: {input_info}
    학습량: {train_size}
    시작시간: {log.get('start_time', '-')}
    모델 로딩: {log.get('model_load', '-')}초
    전처리: {log.get('preprocess', '-')}초
    추론: {log.get('inference', '-')}초
    """

    try:
        gpt_advice = ask_gpt_for_recommendations(summary_text)
        pdf.multi_cell(0, 8, gpt_advice)
        # 생성형 AI 안내 문구 삽입
        pdf.set_font("Noto", "", 9)
        pdf.set_text_color(120)
        pdf.ln(4)
        pdf.cell(0, 8, "※ 위 내용은 OpenAI GPT-4o 생성형 AI 모델의 자동 응답 결과입니다.", align="R")
        pdf.set_text_color(0)
    except Exception as e:
        print("[GPT 오류] 권장 조치 생성 실패:", e)
        pdf.multi_cell(0, 8,
            "open ai api 작동 안됨!\n"
        )


    except Exception as e:
        print("[GPT 오류] 권장 조치 생성 실패:", e)
        fallback_text = (
            "open ai api 작동 안됨!\n"
        )
        for line in fallback_text.split('\n'):
            if line.strip():
                pdf.multi_cell(0, 8, line.strip())



    output_dir = "./temp_uploads/output"
    os.makedirs(output_dir, exist_ok=True)

    output_filename = custom_filename if custom_filename else f"{file_name}_report.pdf"  
    output_path = os.path.join(output_dir, output_filename) 
    pdf.output(output_path)  

    if os.path.exists(chart_path):
        os.remove(chart_path)

    return output_path

