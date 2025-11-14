# fireDetector

이 문서에는 이 폴더에서 `main.py`를 실행하기 위해 가상환경을 만들고 활성화하는 방법을 OS별로 정리해두었습니다.

### 1) 공통 절차 (프로젝트 폴더 기준)

- 프로젝트 폴더로 이동 (이 README는 `fireDetector` 폴더 안에 있습니다):

```powershell
cd C:\Users\kim\Desktop\fireDetector\fireDetector
```

- 가상환경 생성 (권장: 프로젝트 내부에 `.venv`):

```bash
python -m venv .venv
# 또는 (시스템에 python3만 있을 경우)
python3 -m venv .venv
```

- 가상환경 활성화 후 의존성 설치 및 실행:

```bash
# 활성화 후 (아래 OS별 명령 참고)
pip install -r requirements.txt   # 파일이 없으면 필요한 패키지를 개별 설치
python main.py
```

> 참고: 레포트 루트에 이미 `fire_env/` 같은 가상환경 폴더가 있는 경우, 새로 만들지 않고 기존 환경을 활성화해서 사용할 수 있습니다. 경로는 위치에 따라 다릅니다.

---

### 2) Ubuntu (bash / zsh)

```bash
cd /path/to/fireDetector/fireDetector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 3) macOS (bash / zsh)

```bash
cd /path/to/fireDetector/fireDetector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 4) Windows — PowerShell (권장)

```powershell
cd C:\Users\kim\Desktop\fireDetector\fireDetector
python -m venv .venv
# PowerShell에서 활성화
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

> 만약 스크립트 실행이 제한되어 `Activate.ps1` 실행이 차단된다면, 다음 중 하나를 선택하세요:

```powershell
# 1) 현재 세션에서만 제한 해제 (관리자 권한 불필요)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# 그런 다음 활성화 실행
.\.venv\Scripts\Activate.ps1

# 2) CMD에서 활성화 (명령 프롬프트)
.\.venv\Scripts\activate.bat
```

### 5) Windows — CMD (명령 프롬프트)

```cmd
cd C:\Users\kim\Desktop\fireDetector\fireDetector
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

### 6) Conda 대체 방법 (모든 OS 공통)

```bash
conda create -n fireenv python=3.10
conda activate fireenv
pip install -r requirements.txt
python main.py
```

---

### 추가 팁
- VS Code에서: Python 확장을 설치하면 터미널이 자동으로 활성화해주거나 인터프리터 선택을 쉽게 해줍니다.
- `requirements.txt`가 없다면, 필요한 패키지(PyTorch, OpenCV 등)를 직접 설치하거나 `pip freeze > requirements.txt`로 환경을 내보내기 할 수 있습니다.
- 프로젝트 루트에 이미 존재하는 `fire_env/` 같은 가상환경을 사용하려면 해당 폴더의 `Scripts`(Windows) 또는 `bin`(Unix) 경로를 활성화 명령에 맞게 지정하세요.

문서 업데이트가 필요하면 어떤 형식(영문/한글, 더 자세한 예시 등)으로 더 보완할지 알려주세요.