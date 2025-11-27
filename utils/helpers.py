"""
공용 헬퍼 함수 및 상수
"""
import queue
import threading
import socket
import cv2
import numpy as np
import time
import sys

# 전역 설정
HOST = 'localhost'
PORT = 5005
QUEUE_SIZE = 2

# 전역 프레임 큐
frame_queue = queue.Queue(maxsize=QUEUE_SIZE)
connection_status = {"status": "연결 중..."}
receiver_thread_ref = {"thread": None}

def debug_log(msg):
    """디버그 로그 출력 (타임스탬프 포함)"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG {timestamp}] {msg}", file=sys.stderr, flush=True)

def receive_frames():
    """프레임 수신 함수 (백그라운드 스레드에서 실행)"""
    debug_log("receive_frames 함수 시작")
    
    while True:
        try:
            debug_log(f"소켓 연결 시도: {HOST}:{PORT}")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))
            connection_status["status"] = "✓ 연결됨"
            debug_log("소켓 연결 성공")
            
            while True:
                try:
                    # 프레임 크기 수신 (4 바이트)
                    frame_size_data = client_socket.recv(4)
                    if not frame_size_data:
                        connection_status["status"] = "⚠️ 연결 끊김"
                        debug_log("연결 끊어짐")
                        break
                    
                    frame_size = int.from_bytes(frame_size_data, byteorder='big')
                    debug_log(f"프레임 크기: {frame_size} bytes")
                    
                    # 프레임 데이터 수신
                    frame_data = b''
                    while len(frame_data) < frame_size:
                        chunk = client_socket.recv(min(4096, frame_size - len(frame_data)))
                        if not chunk:
                            break
                        frame_data += chunk
                    
                    # JPEG 디코딩
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        # BGR을 RGB로 변환
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # 큐에 프레임 추가
                        try:
                            frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                        frame_queue.put(frame_rgb)
                        connection_status["status"] = "✓ 연결됨"
                    
                except Exception as e:
                    error_msg = str(e)[:30]
                    connection_status["status"] = f"⚠️ 오류: {error_msg}"
                    debug_log(f"프레임 수신 오류: {error_msg}")
                    break
        
        except ConnectionRefusedError:
            connection_status["status"] = "❌ 서버 연결 불가"
            debug_log("서버 연결 거부됨, 2초 후 재시도")
            time.sleep(2)
        except Exception as e:
            error_msg = str(e)[:30]
            connection_status["status"] = f"❌ 오류: {error_msg}"
            debug_log(f"예외 발생: {error_msg}")
            time.sleep(2)

def start_receiver_thread():
    """백그라운드 스레드 시작"""
    if receiver_thread_ref["thread"] is None or not receiver_thread_ref["thread"].is_alive():
        debug_log("백그라운드 스레드 시작")
        receiver_thread = threading.Thread(target=receive_frames, daemon=True)
        receiver_thread.start()
        receiver_thread_ref["thread"] = receiver_thread
        debug_log("백그라운드 스레드 실행 중")
