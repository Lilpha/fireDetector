"""
🔥 화재 감지 시스템 - 메인 진입점
Multi-Page Streamlit 앱
"""
import streamlit as st
from utils.helpers import start_receiver_thread, debug_log

# 페이지 설정
st.set_page_config(
    page_title="Fire Detection System",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

debug_log("========== 앱 시작 ==========")

st.title("🔥 화재 감지 모니터링 시스템")

# 백그라운드 스레드 시작
start_receiver_thread()

st.markdown("""
---
### 📌 메뉴 안내
좌측 사이드바에서 원하는 페이지를 선택하세요:
- **📷 Camera**: 실시간 카메라 영상 스트리밍
- **📊 Dashboard**: 실시간 통계 및 상태 모니터링
- **⚙️ Settings**: 시스템 설정 및 정보

---
""")

# 현재 상태 표시
st.info("✅ 시스템 준비 완료. 왼쪽 메뉴에서 페이지를 선택하세요.")

debug_log("메인 앱 페이지 로드 완료")
