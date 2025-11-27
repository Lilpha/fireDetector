import cv2
from ultralytics import YOLO
import time
import math # 바운딩 박스 좌표 계산용
import os
from pathlib import Path

# --- 설정 ---
# 1. 모델 로드 (2단계에서 다운로드한 .pt 파일 경로)
model = YOLO("best.pt")

# 2. 카메라 설정 (0번 카메라 = 기본 연결된 카메라)
cap = cv2.VideoCapture(0)

# 3. 프레임 저장 설정
FRAME_OUTPUT_PATH = "latest_frame.jpg"
FIRE_DETECTED_PATH = "fire_detected.txt"

# 3. 알림 쿨다운 설정 (초)
ALERT_COOLDOWN = 30 # 30초에 한 번만 알림
last_alert_time = 0

# 4. 감지할 클래스 이름 (모델마다 다를 수 있음)
#    일반적으로 'fire', 'flame' 등입니다. 
#    모델을 로드한 후 model.names를 출력하여 정확한 이름을 확인하는 것이 좋습니다.
print(f"사용 가능한 클래스: {model.names}")
TARGET_CLASS = 'fire' # 예시, 실제 모델의 클래스 이름으로 변경 필요

print("--- 실시간 화재 감지를 시작합니다 (종료: 'q' 키) ---")
print(f"사용 중인 모델 클래스: {model.names}")

while True:
    # 1. 카메라에서 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        print("카메라를 읽을 수 없습니다.")
        break

    # 2. YOLO 모델로 현재 프레임 추론(감지)
    results = model(frame, stream=True, verbose=False) # verbose=False로 로그 최소화

    fire_detected_in_frame = False

    # 3. 감지 결과(results) 분석
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # 3-1. 클래스 ID 확인 및 이름 변환
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            # 3-2. 우리가 찾는 '불' 클래스인지 확인
            if class_name.lower() == TARGET_CLASS.lower():
                fire_detected_in_frame = True
                
                # 3-3. (시각화) 감지된 객체에 사각형 그리기
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # 바운딩 박스 그리기 (파란색)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # 3-4. (시각화) 라벨 및 신뢰도 표시
                confidence = math.ceil(box.conf[0] * 100) / 100
                label = f"{class_name} {confidence}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # 4. (시각화) 결과 프레임 저장
    #    Streamlit에서 읽을 수 있도록 파일로 저장
    try:
        cv2.imwrite(FRAME_OUTPUT_PATH, frame)
    except Exception as e:
        print(f"프레임 저장 오류: {e}")

    # 5. 화재 감지 상태 파일로 저장
    current_time = time.time()
    if fire_detected_in_frame:
        print(f"[{time.ctime()}] !!! 화재 감지 !!!")
        # 화재 감지 상태 저장
        try:
            with open(FIRE_DETECTED_PATH, 'w') as f:
                f.write("True")
        except:
            pass
        
        # 5-1. 쿨다운 시간이 지났는지 확인
        if (current_time - last_alert_time) > ALERT_COOLDOWN:
            print(">>> 알림 조건 충족! (알림 전송 로직 호출)")
            
            # ************************************************
            # ** 다음 단계:
            # ** 여기에 send_fcm_notification() 함수를 호출합니다. **
            # send_fcm_notification() 
            # ************************************************
            
            last_alert_time = current_time # 마지막 알림 시간 갱신
        else:
            print(">>> (알림 쿨다운 시간...)")
    else:
        # 화재 미감지 상태 저장
        try:
            with open(FIRE_DETECTED_PATH, 'w') as f:
                f.write("False")
        except:
            pass


    # 6. 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 종료 처리 ---
cap.release()
cv2.destroyAllWindows()
print("--- 감지 시스템을 종료합니다. ---")