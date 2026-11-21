"""방구석 진품명품 - 레트로 TV 감정쇼 프론트엔드.

필요한 Streamlit Secrets:
    API_URL = "https://my-ai-api-2u2c.vercel.app"
    APP_ACCESS_CODE = "(Vercel과 동일한 접근 코드)"

백엔드(main.py) 수정 없이 GET / 와 POST /analyze 를 이용합니다.
"""

import base64
import html
import io
from pathlib import Path

import requests
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

# Streamlit 명령 중 가장 먼저 페이지를 설정합니다.
st.set_page_config(
    page_title="방구석 진품명품 | 보물 감정쇼",
    page_icon="🧐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

HERE = Path(__file__).resolve().parent
STYLE_FILE = HERE / "style.css"
MAX_SIDE = 1024

if STYLE_FILE.exists():
    st.markdown(
        f"<style>{STYLE_FILE.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

API_URL = st.secrets.get("API_URL", "http://localhost:8000").rstrip("/")
ACCESS_CODE = st.secrets.get("APP_ACCESS_CODE", "")


def escape(value: object) -> str:
    """AI 출력 문자열이 HTML 구조에 영향을 주지 않도록 처리."""
    return html.escape(str(value if value is not None else ""))


def to_jpeg_b64(raw: bytes) -> str:
    """PNG/JPEG/WEBP 이미지를 크기 제한에 맞게 JPEG로 변환."""
    with Image.open(io.BytesIO(raw)) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((MAX_SIDE, MAX_SIDE))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=83, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def analyze(raw: bytes) -> dict | None:
    """기존 FastAPI의 /analyze 엔드포인트만 호출."""
    try:
        encoded = to_jpeg_b64(raw)
    except (OSError, ValueError, UnidentifiedImageError):
        st.error("이미지 파일을 읽지 못했어요. JPG·PNG·WEBP 파일인지 확인해 주세요.")
        return None

    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={"image_b64": encoded, "mime_type": "image/jpeg"},
            headers={"X-Access-Code": ACCESS_CODE},
            timeout=120,
        )
    except requests.RequestException:
        st.error("감정 서버와 연결되지 않았어요. 잠시 후 다시 시도해 주세요.")
        return None

    if response.status_code != 200:
        try:
            error_detail = response.json().get("detail", response.text)
        except (ValueError, AttributeError):
            error_detail = response.text
        st.error(f"감정 요청 실패 ({response.status_code}): {error_detail}")
        return None

    try:
        payload = response.json()
    except ValueError:
        st.error("서버가 올바른 분석 결과를 반환하지 않았어요.")
        return None

    if not isinstance(payload.get("result"), dict):
        st.error("감정 결과 형식이 올바르지 않아요.")
        return None

    return payload


def render_result(payload: dict, field_names: list[str]) -> None:
    """AI가 반환한 값 그대로 감정서에 표시(가격 조작/고정값 없음)."""
    result = payload["result"]
    price = escape(result.get("감정가", "가격 추정 어려움"))
    other_fields = [name for name in field_names if name != "감정가"]

    rows = "".join(
        f'<div class="result-item"><dt>{escape(name)}</dt>'
        f'<dd>{escape(result.get(name, "확인 불가"))}</dd></div>'
        for name in other_fields
    )

    st.markdown(
        f"""
        <section class="result-ticket" aria-label="AI 감정 결과">
          <div class="result-ribbon"><span>🎉 감정 결과 공개!</span><span class="result-edition">AI APPRAISAL REPORT</span></div>
          <div class="result-inner">
            <p class="price-kicker">두구두구... 오늘의 예상 감정가는?</p>
            <div class="result-price">{price}</div>
            <p class="price-notice">※ 사진만으로 추정한 재미용 참고 가격이며 실제 거래 시세가 아닙니다.</p>
            <dl class="result-items">{rows}</dl>
            <div class="stamp" aria-hidden="true">감정<br>완료!</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"✅ 감정 완료 · 상태 번호 200 · 사용 토큰 {escape(payload.get('tokens', 0))}")


# 앱 정보: 백엔드와 통신하는 기능은 기존과 같습니다.
try:
    response = requests.get(f"{API_URL}/", timeout=30)
    response.raise_for_status()
    info = response.json()
    fields = info.get("fields", {})
    if not isinstance(fields, dict) or not fields:
        raise ValueError("API fields 형식 오류")
except (requests.RequestException, ValueError):
    st.error("API 서버에 닿지 못했어요. Streamlit Secrets의 API_URL을 확인해 주세요.")
    st.stop()

st.markdown(
    """
    <div class="show-meta">
      <span class="on-air"><span class="live-dot"></span> ON AIR</span>
      <span class="show-channel">방구석 방송국 · 제1회 소장품 감정쇼</span>
      <span class="season">EP. 001 / SPECIAL</span>
    </div>
    <section class="show-hero">
      <div class="hero-copy">
        <div class="hero-eyebrow">✨ 이 물건... 혹시 대박인가요?! ✨</div>
        <h1>방구석 <span>진품명품!</span></h1>
        <p>서랍 속 피규어부터 오래된 전자기기까지!<br>
           사진 한 장으로 열어보는 <strong>나만의 소장품 감정쇼</strong></p>
        <div class="hero-tags"><span>🔍 AI 돋보기 ON</span><span>💎 숨은 보물 찾기</span><span>🎁 재미로 감정하기</span></div>
      </div>
      <div class="mascot-side" aria-hidden="true">
        <div class="mascot-speech">얼마일까?!</div>
        <div class="mascot-emoji">🧐</div>
        <div class="mascot-base">💥 두구두구 💥</div>
      </div>
    </section>
    <div class="marquee"><span>★ 감정쇼 시작 ★</span><span>사진 한 장이면 OK!</span><span>★ 오늘의 보물은? ★</span></div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="steps">
      <div><b>01</b><span>사진 올리기</span></div>
      <span class="step-arrow">➜</span>
      <div><b>02</b><span>AI 감정하기</span></div>
      <span class="step-arrow">➜</span>
      <div><b>03</b><span>감정가 공개!</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.1, 0.9], gap="large")

with left:
    with st.container(border=True, key="upload_panel"):
        st.markdown(
            '<div class="panel-header"><span class="panel-number">MISSION 01</span>'
            '<h2>🎁 오늘의 보물을 올려주세요!</h2>'
            '<p>내 물건의 가치를 알아볼 준비가 됐나요?</p></div>',
            unsafe_allow_html=True,
        )
        use_camera = st.toggle("📸 카메라로 바로 찍기", key="use_camera")
        camera_file = st.camera_input("소장품 촬영하기") if use_camera else None
        uploaded_file = st.file_uploader(
            "🗂️ 사진 고르기 (JPG · PNG · WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False,
            key="treasure_file",
        )
        st.markdown(
            '<p class="upload-hint">🔒 얼굴 · 신분증 · 카드 번호가 보이는 사진은 올리지 마세요.</p>',
            unsafe_allow_html=True,
        )

with right:
    with st.container(border=True, key="preview_panel"):
        st.markdown(
            '<div class="panel-header"><span class="panel-number alt">ON STAGE</span>'
            '<h2>🎬 오늘의 감정 주인공</h2>'
            '<p>무대에 올릴 소장품을 확인하세요!</p></div>',
            unsafe_allow_html=True,
        )
        active_file = camera_file or uploaded_file
        if active_file is None:
            st.markdown(
                '<div class="empty-stage"><div class="stage-spark">✦ &nbsp; ★ &nbsp; ✦</div>'
                '<div class="stage-emoji">🧸</div><strong>오늘의 보물을 기다리는 중!</strong>'
                '<small>왼쪽에서 사진을 선택해 주세요.</small></div>',
                unsafe_allow_html=True,
            )
        else:
            st.image(active_file.getvalue(), width="stretch", caption="✨ 무대 위에 올라온 소장품")

st.markdown(
    '<div class="action-title"><span class="action-number">MISSION 02</span>'
    '<h2>🥁 운명의 감정 버튼을 눌러주세요!</h2></div>',
    unsafe_allow_html=True,
)

sample_paths = [HERE / "sample.jpg", HERE / "receipt.png"]
sample_path = next((p for p in sample_paths if p.is_file()), None)

btn_col, sample_col = st.columns([2.5, 1], gap="medium")
with btn_col:
    run_btn = st.button("🎤 감정 결과 공개!", key="go", disabled=active_file is None, width="stretch")
with sample_col:
    sample_btn = (
        st.button("🎲 예시로 체험", key="sample", width="stretch")
        if sample_path else False
    )

raw_bytes = None
if run_btn and active_file is not None:
    raw_bytes = active_file.getvalue()
elif sample_btn and sample_path is not None:
    raw_bytes = sample_path.read_bytes()
    st.info("🎲 예시 사진으로 감정쇼를 시작했어요!")
    st.image(raw_bytes, width=240)

if raw_bytes is not None:
    with st.spinner("🧐 감정사가 돋보기로 꼼꼼히 살펴보는 중... 두구두구!"):
        payload = analyze(raw_bytes)
    if payload is not None:
        st.markdown('<div class="results-heading">🏆 <span>MISSION CLEAR!</span> 오늘의 감정서가 도착했어요</div>', unsafe_allow_html=True)
        render_result(payload, list(fields.keys()))

st.markdown(
    '<div class="show-footer">🎟️ 방구석 감정쇼 · 100% AI의 사진 기반 추정 / 실제 거래 가격은 별도 확인해 주세요. <span>THANKS FOR WATCHING!</span></div>',
    unsafe_allow_html=True,
)
