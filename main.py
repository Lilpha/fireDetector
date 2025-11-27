import cv2
from ultralytics import YOLO
import time
import math
import socket
import json
from datetime import datetime

# --- 설정 ---
model = YOLO("fireModel/best.pt")
cap = cv2.VideoCapture(0)

ALERT_COOLDOWN = 30
last_alert_time = 0
fire_detected_state = False

TARGET_CLASS = 'fire'

# 이벤트 로그 파일
EVENT_LOG_FILE = "fire_events.json"

print(f"사용 가능한 클래스: {model.names}")
print("--- 실시간 화재 감지를 시작합니다 ---")
print(f"사용 중인 모델 클래스: {model.names}")

# 로컬호스트에서 프레임을 송신할 소켓 서버 설정
HOST = 'localhost'
PORT = 5005

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
server_socket.settimeout(1)

client_socket = None
print(f"✓ 소켓 서버 대기 중: {HOST}:{PORT}")

try:
    while True:
        # 클라이언트 연결 시도
        try:
            if client_socket is None:
                client_socket, addr = server_socket.accept()
                print(f"✓ 클라이언트 연결됨: {addr}")
        except socket.timeout:
            pass

        # 1. 카메라에서 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("카메라를 읽을 수 없습니다.")
            break

        # 2. YOLO 모델로 현재 프레임 추론
        results = model(frame, stream=True, verbose=False)

        fire_detected_in_frame = False

        # 3. 감지 결과 분석
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]

                if class_name.lower() == TARGET_CLASS.lower():
                    fire_detected_in_frame = True
                    
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                    confidence = math.ceil(box.conf[0] * 100) / 100
                    label = f"{class_name} {confidence}"
                    cv2.putText(frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        fire_detected_state = fire_detected_in_frame

        # 4. 프레임을 연결된 클라이언트로 송신
        if client_socket:
            try:
                # JPEG로 압축
                ret_encode, frame_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                data = frame_encoded.tobytes()
                
                # 프레임 크기와 데이터 전송
                frame_size = len(data)
                client_socket.sendall(frame_size.to_bytes(4, byteorder='big'))
                client_socket.sendall(data)
            except (BrokenPipeError, ConnectionResetError):
                print("클라이언트 연결 해제됨")
                client_socket = None
            except Exception as e:
                print(f"송신 오류: {e}")
                client_socket = None

        # 5. 화재 감지 여부 및 알림 로직
        current_time = time.time()
        if fire_detected_in_frame:
            print(f"[{time.ctime()}] !!! 화재 감지 !!!")
            
            # 화재 감지 시 항상 JSON 갱신 (타임스탬프 업데이트)
            # 이렇게 하면 streamlit의 threshold가 리셋되어 지속 시간이 계속 유지됨
            confidence_val = float(confidence) if 'confidence' in locals() else 0.0
            event_data = {
                "event_type": "fire_detected",
                "timestamp": datetime.now().isoformat(),
                "unix_timestamp": current_time,
                "confidence": confidence_val,
                "message": "🔥 화재가 감지되었습니다!"
            }
            
            try:
                with open(EVENT_LOG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(event_data, f, indent=2, ensure_ascii=False)
                debug_log_flag = True
            except Exception as e:
                print(f"이벤트 저장 오류: {e}")
            
            # 알림 쿨다운 관리 (첫 감지 시에만 콘솔 출력)
            if (current_time - last_alert_time) > ALERT_COOLDOWN:
                print(">>> 알림 조건 충족! (첫 감지 또는 쿨다운 만료)")
                last_alert_time = current_time
            else:
                pass  # 쿨다운 중이지만 JSON은 계속 갱신됨
        else:
            # 화재 미감지 - JSON 파일 존재하면 삭제 (선택사항)
            pass

        time.sleep(0.03)  # 약 30 FPS 유지

except KeyboardInterrupt:
    print("\n시스템 종료 중...")

finally:
    if client_socket:
        client_socket.close()
    server_socket.close()
    cap.release()
    print("--- 감지 시스템을 종료합니다. ---")