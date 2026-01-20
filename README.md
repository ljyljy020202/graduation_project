# 📌 LLM 기반 자동 라벨링 & 데이터 처리 파이프라인

본 프로젝트는 OpenAI 및 Gemini API를 활용하여
텍스트 데이터에 대한 자동 라벨링 / 데이터 증강 / 구조화 처리를 수행하는 실험용 파이프라인입니다.
프롬프트 파일 분리, 공통 모듈화, 모델별 실행 스크립트 분리를 통해
확장성과 재사용성을 고려한 구조로 설계되었습니다.

## 📁 프로젝트 구조

```
project/ 
├── openai_main.py      # openai 요청 기본 스크립트
├── openai_v2.py        # 입력 폴더가 계층 구조인 경우 (예 - input 아래 /Normal, /Abnormal 등으로 나뉜 경우 이 구조를 반영하여 그대로 results 파일에 결과를 저장함)
├── gemini_main.py      # gemini 요청 기본 스크립트
├── gemini_v2.py        # 입력 폴더가 계층 구조인 경우
├── common/             # 파일 처리, llm 클라이언트 등 공통 유틸 함수들 모음
│   ├── __init__.py
│   ├── prompt_loader.py
│   ├── config.py
│   ├── file_utils.py
│   └── llm_client.py
├── prompts/            # 요청에 사용할 프롬프트 원문 txt
│   ├── labeling.txt
│   └── data_augment.txt
├── input_data/         # 입력 데이터 경로
├── results/            # 출력 데이터 경로
├── .env
└── README.md
```

## ⚙️ 실행 환경
### Python 버전
Python 3 이상 권장
### 필수 설치 패키지
pip install openai google-generativeai python-dotenv

## 🔐 .env 설정 방법
프로젝트 루트에 .env 파일을 생성하고 아래 내용을 작성하세요:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-5-mini
GEMINI_MODEL=gemini-2.5-pro
```
⚠️ .env 파일은 절대 GitHub에 커밋하지 마세요!

## 🚀 실행 방법
```
python openai_main.py    # OpenAI 기본 실행
python openai_v2.py      # OpenAI 계층 구조 입력 대응 실행
python gemini_main.py    # Gemini 기본 실행
python gemini_v2.py      # Gemini 계층 구조 입력 대응 실행
```

## 🧩 동작 방식 요약
1. input_data/ 내 텍스트/JSON 데이터 로딩
2. prompts/ 내 프롬프트 파일 적용
3. LLM(OpenAI/Gemini)에 요청
4. 응답을 안전하게 JSON으로 파싱
5. results/에 동일 구조로 저장
