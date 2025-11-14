# fireDetector

이 프로젝트는 현재 가상환경이 이미 포함되어 있는 상태입니다. 최근 폴더 구조가 변경되어 이 README가 있는 위치와 가상환경 위치가 다를 수 있으니 아래 내용을 참고해 활성화 후 `main.py`를 실행하세요.

요약: 가상환경은 이미 설치되어 있으므로 패키지 설치(`pip install -r requirements.txt`)는 불필요합니다. 단, 가상환경의 위치가 바뀌었다면 경로만 맞춰 활성화하세요.

파일/폴더 예시 구조 (참고):

```
fireDetector/             <- 레포지토리 루트
	main.py
	fire_env/               <- 이미 생성된 가상환경 (예시)
	fireModel/
	fireDetector/           <- (이 README가 들어있는 하위 폴더일 수 있음)
		README.md
```

1) 이동: README가 있는 폴더에서 레포지토리 루트( `main.py`가 있는 위치)로 이동하세요.

```powershell
cd ..\..   # 또는 적절한 상대경로로 레포지토리 루트로 이동
```

2) 기존 가상환경 활성화 (이미 `fire_env`가 있는 경우)

- Ubuntu / macOS (bash / zsh):

```bash
source fire_env/bin/activate
python main.py
```

- Windows — PowerShell:

```powershell
..\fire_env\Scripts\Activate.ps1
python main.py
```

만약 PowerShell에서 스크립트 실행이 제한되어 활성화가 차단되면(한번만 세션 범위에서 해제 가능):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
..\fire_env\Scripts\Activate.ps1
```

- Windows — CMD (명령 프롬프트):

```cmd
..\fire_env\Scripts\activate.bat
python main.py
```

3) (선택) 가상환경이 다른 위치 또는 `.venv`로 존재할 때

- 저장소 내부에 `.venv`가 있는 경우(또는 새로 만들고 싶을 때):

```bash
# 새로 만들고 싶으면
python -m venv .venv
# 활성화 (Unix)
source .venv/bin/activate
# 또는 PowerShell
.\.venv\Scripts\Activate.ps1
python main.py
```

4) 상태 확인 / 패키지 확인

가상환경 활성화 후, 설치된 패키지를 확인하려면:

```bash
pip list
# 또는 현재 환경에 고정된 목록을 만들고 싶다면
pip freeze > current-requirements.txt
```

추가 안내
- `requirements.txt`에서 설치할 필요는 없습니다(이미 가상환경에 패키지가 설치되어 있음).
- 가상환경 위치를 README에 명확히 표기하길 원하시면, 정확한 상대경로(`../fire_env` 등)를 알려주시면 그에 맞춰 수정해 드리겠습니다.

원하시면 다음 작업을 도와드리겠습니다:
- 레포지토리 루트에 있는 실제 가상환경 경로로 README에 경로 고정하기
- 현재 가상환경에서 `pip freeze > requirements.txt` 실행해 `requirements.txt` 생성
- 실행용 스크립트 `run.sh` / `run.bat` 추가
