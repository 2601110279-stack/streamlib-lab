# 📋 app.py
import base64
import io
import os
import requests
import streamlit as st
from PIL import Image
from pathlib import Path

# 페이지 기본 설정
st.set_page_config(
    page_title="방구석 진품명품",
    page_icon="🧐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 파일 적용
style_path = Path(__file__).with_name("style.css")

if style_path.is_file():
    st.markdown(
        f"<style>{style_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )


MAX_SIDE = 1024
SAMPLE_IMAGE = "sample.jpg"  # ★ GitHub/Colab에 올린 내 예시 사진 파일명

API_URL = st.secrets.get("API_URL", "http://localhost:8000").rstrip("/")
ACCESS_CODE = st.secrets.get("APP_ACCESS_CODE", "")

try:
    info = requests.get(f"{API_URL}/", timeout=30).json()
except Exception:
    st.error("❌ API 서버에 닿지 못함 — Secrets의 API_URL 주소를 확인하세요.")
    st.stop()

fields = info.get("fields", {})
field_names = " · ".join(fields.keys())

st.title(f"{info.get('icon', '🧐')} {info.get('name', '방구석 진품명품')}")
st.caption(
    f"{info.get('description', '')} · 결과 칸 : {field_names} · "
    "얼굴 · 신분증 · 카드 번호가 보이는 사진은 올리지 마세요"
)

use_camera = st.toggle("카메라 켜기")
camera_file = st.camera_input("소장품 촬영하기") if use_camera else None
uploaded_file = st.file_uploader("또는 사진 파일 올리기", type=["png", "jpg", "jpeg", "webp"])

active_file = camera_file or uploaded_file
run_btn = st.button("정리하기", disabled=(active_file is None))
sample_btn = st.button("예시 사진으로 해 보기") if os.path.exists(SAMPLE_IMAGE) else False

raw_bytes = None
if run_btn and active_file is not None:
    raw_bytes = active_file.getvalue()
elif sample_btn and os.path.exists(SAMPLE_IMAGE):
    with open(SAMPLE_IMAGE, "rb") as f:
        raw_bytes = f.read()


def to_jpeg_b64(raw: bytes) -> str:
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    image.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


if raw_bytes is not None:
    st.image(raw_bytes, width=320)
    with st.spinner("감정사가 돋보기로 살펴보는 중..."):
        b64_str = to_jpeg_b64(raw_bytes)
        try:
            res = requests.post(
                f"{API_URL}/analyze",
                json={"image_b64": b64_str, "mime_type": "image/jpeg"},
                headers={"X-Access-Code": ACCESS_CODE},
                timeout=120,
            )
        except Exception:
            st.error("❌ API 서버 연결 중 오류가 발생했습니다.")
            st.stop()

    if res.status_code == 200:
        body = res.json()
        result_data = body.get("result", {})
        tokens = body.get("tokens", 0)
        rows = [{"칸": key, "내용": result_data.get(key, "확인 불가")} for key in fields]
        st.table(rows)
        st.caption(f"상태 번호 200 · 토큰 {tokens}")
    else:
        try:
            detail = res.json().get("detail", res.text)
        except Exception:
            detail = res.text
        st.error(f"❌ 상태 번호 {res.status_code} : {detail}")
