import streamlit as st
import time
import os
from PIL import Image

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Fire Detection")

st.title("🔥 화재 감지 모니터링")

# 2. 레이아웃 분할 (5:5)
col_left, col_right = st.columns(2)

# --- 왼쪽 컬럼 (카메라 화면) ---
with col_left:
    # border=True 옵션이 '카드'처럼 테두리를 만들어줍니다.
    with st.container(border=True):
        st.subheader("📷 실시간 카메라 화면")
        
        # 실시간 스트리밍을 위한 placeholder
        camera_placeholder = st.empty()
        
        # 프레임이 업데이트될 때까지 기다리는 로직
        while True:
            try:
                # main.py에서 저장한 최신 프레임 읽기
                if os.path.exists("latest_frame.jpg"):
                    image = Image.open("latest_frame.jpg")
                    camera_placeholder.image(image, use_container_width=True)
                    time.sleep(0.05)  # 약 20 FPS
                else:
                    camera_placeholder.warning("⏳ 카메라 초기화 중...")
                    time.sleep(1)
            except Exception as e:
                camera_placeholder.warning(f"⚠️ 카메라 읽기 오류: {e}")
                time.sleep(1)

# --- 오른쪽 컬럼 (정보 창 3개) ---
with col_right:
    # 첫 번째 카드: 타이머
    with st.container(border=True):
        st.subheader("⏱ 화재 지속 시간")
        st.write("불이 지속된 시간을 나타내는 타이머")
        # st.metric은 숫자 데이터를 아주 예쁘게 보여주는 내장 함수입니다.
        st.metric(label="Duration", value="00:12:34", delta="지속 중")

    # 두 번째 카드: 빈도
    with st.container(border=True):
        st.subheader("📊 이벤트 발생 빈도")
        st.write("불이라는 이벤트 발생 빈도를 나타내는 창")
        st.metric(label="Frequency", value="5 회", delta="1시간 기준")

    # 세 번째 카드: 상태
    with st.container(border=True):
        st.subheader("✅ 현재 상태")
        st.write("현재 카메라가 보는 상태")
        
        # 화재 감지 상태를 실시간으로 읽기
        fire_status = "정상 (Normal)"
        status_type = "success"
        
        try:
            if os.path.exists("fire_detected.txt"):
                with open("fire_detected.txt", 'r') as f:
                    status = f.read().strip()
                    if status == "True":
                        fire_status = "🚨 화재 감지! (Fire Detected)"
                        status_type = "error"
                    else:
                        fire_status = "정상 (Normal)"
                        status_type = "success"
        except:
            pass
        
        # 상태에 따라 색상을 다르게 보여줌
        if status_type == "success":
            st.success(fire_status)
        else:
            st.error(fire_status)