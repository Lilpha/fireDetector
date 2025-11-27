"""
대시보드 페이지 (우측 카드)
"""
import streamlit as st
from utils.helpers import start_receiver_thread, debug_log

debug_log("dashboard.py 페이지 로드")

st.header("📊 실시간 대시보드")

# 백그라운드 스레드 시작
start_receiver_thread()

debug_log("dashboard.py - 카드 생성")

# 3개의 카드 (컬럼 사용)
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("⏱ 화재 지속 시간")
        st.write("불이 지속된 시간을 나타내는 타이머")
        st.metric(label="Duration", value="00:12:34", delta="지속 중")

with col2:
    with st.container(border=True):
        st.subheader("📈 이벤트 발생 빈도")
        st.write("불이라는 이벤트 발생 빈도를 나타내는 창")
        st.metric(label="Frequency", value="5 회", delta="1시간 기준")

with col3:
    with st.container(border=True):
        st.subheader("✅ 현재 상태")
        st.write("현재 카메라가 보는 상태")
        st.success("정상 (Normal)")

debug_log("dashboard.py - 카드 생성 완료")
