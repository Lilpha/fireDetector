# fireDetector

실시간 YOLO 기반 화재 감지 시스템입니다. 백엔드(main.py)에서 YOLO 모델을 실행하고, 프론트엔드(Streamlit)에서 실시간 모니터링 대시보드를 제공합니다.

## 📋 주요 기능

### 🔥 화재 감지
- **YOLO v8 기반 실시간 화재 감지**: `fireModel/best.pt` 모델을 사용한 정확한 화재 인식
- **소켓 기반 스트리밍**: TCP 소켓 (localhost:5005)을 통해 처리된 영상을 실시간 전송
- **JSON 기반 이벤트 로깅**: 감지 이벤트를 `fire_events.json`에 기록

### 📊 대시보드 기능

#### 1. **듀얼 타이머 시스템** ✨
- **큰 시계 (화재 지속 시간)**: 화재가 감지되면 지속 시간을 초 단위로 계산
  - 예: `00:00:15` (15초 지속)
  - 화재 이벤트가 10초 이상 감지되지 않으면 자동 리셋

- **작은 시계 (마지막 감지)**: T- 형식으로 마지막 감지 시각과 경과 시간 표시
  - 예: `🕒 마지막 감지: 14:23:45 (T - 5s)`
  - 화재 종료 후에도 영구 보존

#### 2. **카운다운 상태 (화재 감소)** ✨ NEW
- 화재 이벤트가 사라진 후 **10초 동안 '화재 감소됨' 상태 유지**
- `T - 10s` → `T - 9s` → ... → `T - 0s` 형식으로 카운트다운 표시
- 상태: 🟡 **화재 감소됨** (황색)
- 10초 경과 후 자동으로 "정상 (Safe)" 상태로 전환

#### 3. **이벤트 카운터**
- **상태 머신 기반 정확한 이벤트 카운팅**
  - Rising Edge (화재 시작): 카운트 +1
  - Falling Edge (화재 종료): 상태 전환, 카운다운 시작
- 누적 감지 횟수를 실시간으로 표시

#### 4. **상태 표시기**
- 🚨 **화재 발생 (DANGER)** - 빨강
- 🟡 **화재 감소됨** - 황색 (카운다운 중)
- ✅ **정상 (Safe)** - 초록

### 📹 실시간 모니터링
- 카메라 피드를 JPEG 압축(80%)하여 실시간 표시
- 30 FPS로 스트리밍 처리
- YOLO 감지 결과(경계박스)를 포함한 처리 영상 표시

---

## 🚀 설치 및 실행

### 시스템 요구사항
- Python 3.9+
- Windows / macOS / Linux
- GPU 권장 (YOLO 추론 속도 향상)

### 1️⃣ 가상환경 활성화

이 프로젝트는 `fire_env/` 가상환경이 이미 포함되어 있습니다.

**레포지토리 루트(`main.py`가 있는 폴더)에서 실행:**

#### Windows PowerShell:
```powershell
..\fire_env\Scripts\Activate.ps1
```

PowerShell 보안 정책 오류 시:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
..\fire_env\Scripts\Activate.ps1
```

#### Windows CMD:
```cmd
..\fire_env\Scripts\activate.bat
```

#### macOS / Linux:
```bash
source fire_env/bin/activate
```

### 2️⃣ 백엔드 실행 (YOLO 화재 감지)

```powershell
python main.py
```

**출력 예시:**
```
🔥 YOLO 모델 로드됨: fireModel/best.pt
📡 소켓 서버 시작: localhost:5005
📹 카메라 스트림 처리 중...
```

### 3️⃣ 프론트엔드 실행 (Streamlit 대시보드)

**새 터미널에서 (가상환경 활성화 후):**

```powershell
streamlit run app.py
```

**브라우저 자동 실행:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

---

## 📁 파일 구조

```
fireDetector/
├── main.py                    # YOLO 화재 감지 + 소켓 스트리밍 백엔드
├── app.py                     # Streamlit 메인 앱
├── pages/
│   ├── 0_📊_Dashboard.py      # 실시간 모니터링 대시보드 (핵심 UI)
│   ├── 1_📷_Camera.py         # 카메라 피드 페이지
│   └── 2_⚙️_Settings.py       # 설정 페이지
├── utils/
│   └── helpers.py             # 소켓 통신, 이벤트 처리 헬퍼 함수
├── fireModel/
│   └── best.pt                # YOLO v8 화재 감지 모델
├── fire_env/                  # Python 가상환경
├── fire_events.json           # 감지 이벤트 로그 (자동 생성)
└── README.md                  # 이 파일
```

---

## ⚙️ 주요 설정 값

### main.py (백엔드 설정)
```python
ALERT_COOLDOWN = 30              # 콘솔 로깅 쿨다운 (초)
CONFIDENCE_THRESHOLD = 0.5       # YOLO 신뢰도 임계값
```

### pages/0_📊_Dashboard.py (프론트엔드 설정)
```python
FIRE_ACTIVE_THRESHOLD = 10       # 화재 활성 판단 임계값 (초)
FALLBACK_DURATION = 10           # 카운다운 지속 시간 (초)
```

---

## 🔄 동작 플로우

### 1. 화재 감지 시작 (Rising Edge)
```
14:23:45 - 화재 감지
↓
main.py: fire_events.json 갱신 (timestamp, confidence)
↓
Dashboard: 
  - fire_start_time 기록
  - daily_fire_count += 1
  - 큰 시계 시작 (00:00:00)
  - 상태: 🚨 화재 발생 (DANGER)
```

### 2. 화재 지속 중 (Stable High)
```
매 루프마다:
- 큰 시계 증가 (0:00:01, 0:00:02, ...)
- 작은 시계 갱신 (T - 초 계속 변함)
- 영상 스트림 실시간 처리
```

### 3. 화재 종료 감지 (Falling Edge)
```
14:24:00 - 감지 10초 이상 없음
↓
is_fire_active() = False
↓
Dashboard:
  - fire_end_time 기록
  - fire_start_time = None (큰 시계 리셋)
  - fire_end_time으로 카운다운 시작
  - 상태: 🟡 화재 감소됨 (T - 10s)
```

### 4. 카운다운 완료 (정상 상태)
```
10초 경과
↓
Dashboard:
  - fire_end_time = None
  - 상태: ✅ 정상 (Safe)
  - 마지막 감지 시간 영구 보존
```

---

## 📊 이벤트 데이터 형식

`fire_events.json`:
```json
{
  "event_type": "fire_detected",
  "timestamp": "2025-11-28T14:23:45.123456",
  "unix_timestamp": 1732804425.123456,
  "confidence": 0.92,
  "message": "화재 감지됨"
}
```

---

## 🔧 문제 해결

### 1. "모듈을 찾을 수 없음" 오류
```powershell
# 가상환경이 활성화되어 있는지 확인
(fire_env) C:\...> python -c "import torch; print('OK')"
```

### 2. 소켓 연결 오류 (localhost:5005)
```powershell
# main.py와 streamlit이 동시에 실행 중인지 확인
# 터미널 1: main.py
# 터미널 2: streamlit run app.py
```

### 3. 카메라 인식 안 됨
```powershell
# 다른 앱에서 카메라를 사용 중일 수 있음
# 또는 카메라 권한 확인
```

### 4. YOLO 모델 로드 오류
```
fireModel/best.pt가 올바른 위치에 있는지 확인
파일 크기 정상 여부: 약 40-50MB
```

---

## 📦 패키지 요구사항

가상환경에 미리 설치된 주요 패키지:
- `torch` / `torchvision` - PyTorch 딥러닝 프레임워크
- `ultralytics` - YOLO v8 모델
- `opencv-python (cv2)` - 영상 처리
- `streamlit` - 웹 대시보드 프레임워크
- `numpy` / `scipy` - 수치 연산
- `pillow (PIL)` - 이미지 처리

전체 패키지 목록:
```powershell
pip list
```

---

## 🌳 브랜치 정보

**현재 브랜치**: `develop` (새로운 기능 개발 중)

### ✨ 최신 업데이트 (develop 브랜치)

#### 📊 듀얼 타이머 시스템
- **큰 시계**: 화재 지속 시간 (00:00:00 ~ 계속 증가)
- **작은 시계**: 마지막 감지 시각 T- 형식 (예: T - 5s)

#### 🔄 카운다운 기능 (NEW!)
- 화재 이벤트 사라진 후 **10초 카운다운** (T - 10s ~ T - 0s)
- 상태 표시: 🟡 **화재 감소됨** (황색)
- 자동 상태 전환: 카운다운 완료 후 ✅ **정상 (Safe)**

#### 🎯 정확한 이벤트 카운팅
- **State Machine 패턴** 적용
- Rising Edge: 화재 감지 시작 (+1)
- Falling Edge: 화재 종료 감지 (카운다운 시작)
- 중복 계산 방지, 정확한 이벤트 카운트

#### 🚀 성능 개선
- threshold 10초로 단축: 빠른 상태 반응
- main.py에서 **매 프레임 JSON 갱신** (지속적 타이머 유지)
- 소켓 기반 실시간 스트리밍 안정화

---

## 💡 사용 팁

1. **카메라 선택**: `main.py`에서 `cv2.VideoCapture(0)`을 편집하여 다른 카메라 사용 가능
2. **감지 임계값 조정**: YOLO 신뢰도 임계값 `CONFIDENCE_THRESHOLD` 수정
3. **카운다운 시간 변경**: `FALLBACK_DURATION` 값 수정 (단위: 초)
4. **마지막 감지 저장**: JSON 파일을 외부 DB로 연동 가능

---

## 📝 라이선스

이 프로젝트는 개인 연구/개발용입니다.

---

## 👨‍💻 개발자

**최종 수정**: 2025-11-28  
**상태**: 활발한 개발 중 (develop 브랜치)  
**주요 기능 완성도**: 95%
