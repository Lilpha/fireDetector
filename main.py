import cv2
from ultralytics import YOLO
import time
import math
import socket
import json
from datetime import datetime

# --- 설정 ---
fire_model = YOLO("fireModel/best.pt")  # 화재 감지 모델 (매 프레임)
animal_model = YOLO("yolov8n.pt")  # 동물 감지 모델 - nano 모델 사용 (더 빠름)

cap = cv2.VideoCapture(0)

ALERT_COOLDOWN = 30
last_alert_time = 0
fire_detected_state = False
animal_detected_state = False

TARGET_CLASS = 'fire'

# 동물 클래스 리스트 (YOLO coco 데이터셋의 동물 클래스)
ANIMAL_CLASSES = ['dog', 'cat', 'bird', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 
                  'person', 'monkey', 'deer', 'fox', 'rabbit', 'squirrel', 'penguin', 'panda']

# 이벤트 로그 파일
FIRE_EVENT_LOG_FILE = "fire_events.json"
ANIMAL_EVENT_LOG_FILE = "animal_events.json"

# 성능 최적화: 프레임 스킵 설정
ANIMAL_DETECTION_SKIP = 3  # 매 3프레임마다 동물 감지 (더 빠름)
frame_count = 0

print(f"화재 감지 모델 클래스: {fire_model.names}")
print(f"동물 감지 모델 클래스: {animal_model.names}")
print(f"성능 최적화: 매 {ANIMAL_DETECTION_SKIP}프레임마다 동물 감지")
print("--- 실시간 화재 + 동물 감지를 시작합니다 ---")

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

        # 2. YOLO 모델로 현재 프레임 추론 (화재 감지 - 매 프레임)
        fire_results = fire_model(frame, stream=True, verbose=False)
        
        # 동물 감지는 성능 최적화를 위해 프레임 스킵
        animal_results = None
        if frame_count % ANIMAL_DETECTION_SKIP == 0:
            animal_results = animal_model(frame, stream=True, verbose=False)
        
        frame_count += 1

        fire_detected_in_frame = False
        animal_detected_in_frame = False
        detected_animals = []

        # 3-1. 화재 감지 결과 분석 (매 프레임)
        for r in fire_results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = fire_model.names[cls_id]

                if class_name.lower() == TARGET_CLASS.lower():
                    # 화재 이벤트 트리거
                    fire_detected_in_frame = True
                    
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # 화재 감지: 파란색 박스
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                    confidence = math.ceil(box.conf[0] * 100) / 100
                    label = f"🔥 {class_name} {confidence}"
                    cv2.putText(frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 3-2. 동물 감지 결과 분석 (스킵된 프레임에서만)
        if animal_results is not None:
            for r in animal_results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    class_name = animal_model.names[cls_id]

                    # 동물 클래스 확인
                    if class_name.lower() in [c.lower() for c in ANIMAL_CLASSES]:
                        animal_detected_in_frame = True
                        detected_animals.append(class_name)
                        
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # 동물 감지: 초록색 박스
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        confidence = math.ceil(box.conf[0] * 100) / 100
                        label = f"🐾 {class_name} {confidence}"
                        cv2.putText(frame, label, (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        fire_detected_state = fire_detected_in_frame
        animal_detected_state = animal_detected_in_frame

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
        
        # === 화재 감지 처리 ===
        if fire_detected_in_frame:
            print(f"[{time.ctime()}] 🔥 화재 감지 !!!")
            
            confidence_val = float(confidence) if 'confidence' in locals() else 0.0
            fire_event_data = {
                "event_type": "fire_detected",
                "timestamp": datetime.now().isoformat(),
                "unix_timestamp": current_time,
                "confidence": confidence_val,
                "message": "🔥 화재가 감지되었습니다!"
            }
            
            try:
                with open(FIRE_EVENT_LOG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(fire_event_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"화재 이벤트 저장 오류: {e}")
            
            if (current_time - last_alert_time) > ALERT_COOLDOWN:
                print(">>> 화재 알림 조건 충족!")
                last_alert_time = current_time
        
        # === 동물 감지 처리 ===
        if animal_detected_in_frame:
            animal_list = ", ".join(set(detected_animals))  # 중복 제거
            print(f"[{time.ctime()}] 🐾 동물 감지: {animal_list}")
            
            animal_event_data = {
                "event_type": "animal_detected",
                "timestamp": datetime.now().isoformat(),
                "unix_timestamp": current_time,
                "detected_animals": detected_animals,
                "message": f"🐾 {animal_list}이(가) 감지되었습니다!"
            }
            
            try:
                with open(ANIMAL_EVENT_LOG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(animal_event_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"동물 이벤트 저장 오류: {e}")

        time.sleep(0.03)  # 약 30 FPS 유지

except KeyboardInterrupt:
    print("\n시스템 종료 중...")

finally:
    if client_socket:
        client_socket.close()
    server_socket.close()
    cap.release()
    print("--- 감지 시스템을 종료합니다. ---")