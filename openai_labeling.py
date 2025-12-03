import os
import json
from openai import OpenAI

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key="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")  # 🔒 실제 API 키로 교체하세요

# ✅ 라벨링용 프롬프트 (system 메시지)
SYSTEM_PROMPT = """
[SYSTEM ROLE]
당신은 금융 보안 전문가이자 AI 데이터 라벨러입니다.
당신의 임무는 주어진 전화 통화 내역을 분석하여, 보이스피싱 의도가 담긴 발화를 식별하고 지정된 JSON 포맷으로 완성하는 것입니다.

[TASK DESCRIPTION]
입력된 통화 대화문의 각 문장(utterances)에 대해 보이스피싱 위험도를 판별하여 0 또는 1로 라벨링하십시오.
- 1 (Suspicious/Phishing): 보이스피싱의 핵심 범죄 행위(금전 요구, 개인정보 탈취, 악성 앱 설치 유도 등)가 포함된 문장.
- 0 (Normal): 일상적인 대화, 단순 질문, 인사, 혹은 범죄 행위가 포함되지 않은 피싱범의 단순 응대.

[DECISION RULES]
각 문장을 판정할 때는 아래의 4대 핵심 트리거를 기준으로 삼으십시오.
1. 금전 요구: 이체, 송금, 현금 전달, 대출 상환, 상품권 구매 등을 지시하거나 유도하는 내용.
2. 매체 설치 및 접속: 원격 제어 앱, 악성 앱 설치, 특정 URL 클릭, 가짜 사이트 접속을 유도하는 내용.
3. 민감 정보 요구: 비밀번호, OTP, 보안카드, 주민등록번호 전체, 계좌번호 등을 직접적으로 요구하는 내용.
4. 심리적 압박: 검찰, 경찰, 금감원 사칭, 구속 및 수사 언급, 지금 당장, 비밀 유지 등을 강요하며 피해자를 고립시키는 내용.

[CONTEXT AND BIAS GUIDELINES]
1. 맥락 활용: 현재 문장의 의도를 파악하기 위해 이전까지의 대화 흐름을 참고하십시오.
2. 독립적 판정: 입력으로 주어진 conversation_label(대화 전체 라벨)이 1이라 하더라도, 모든 문장이 1인 것은 아닙니다. 반드시 문장 그 자체에 범죄 의도가 포함되어 있는지 개별적으로 판단하십시오.
3. 화자 표기 무시: 입력 데이터의 speaker 필드에 사기범 표기가 있더라도 이를 판단의 절대적 근거로 삼지 마십시오.

[INPUT FORMAT]
입력은 아래 필드를 포함한 단일 JSON 객체입니다.
- conversation_id: 대화 고유 ID (정수 또는 문자열)
- conversation_label: 대화 전체의 라벨 (0: 정상, 1: 피싱)
- utterances: 대화 내용이 담긴 객체들의 리스트 (idx, speaker, text 포함)

[OUTPUT FORMAT]
입력된 JSON 구조를 유지하되, utterances 내부의 각 객체에 label 필드를 추가하여 반환하십시오. 반환되는 JSON은 반드시 아래 형식을 따라야 합니다.

{
  "conversation_id": (입력값 유지),
  "conversation_label": (입력값 유지),
  "utterances": [
    {
      "idx": (입력된 인덱스를 문자열 "0", "1" 형태로 변환),
      "label": (판정 결과: 정수 0 또는 1),
      "speaker": (입력값 유지),
      "text": (입력값 유지)
    },
    ...
  ]
}

[FEW-SHOT EXAMPLES]

User Input:
{
  "conversation_id": 1024,
  "conversation_label": 1,
  "utterances": [
    {"idx": 0, "speaker": "A", "text": "서울지검 첨단범죄수사팀 김민수 수사관입니다."},
    {"idx": 1, "speaker": "B", "text": "네 무슨 일이시죠?"},
    {"idx": 2, "speaker": "A", "text": "지금 당장 계좌의 잔액을 안전계좌로 이체하셔야 합니다."}
  ]
}

Model Output:
{
  "conversation_id": 1024,
  "conversation_label": 1,
  "utterances": [
    {"idx": "0", "label": 1, "speaker": "A", "text": "서울지검 첨단범죄수사팀 김민수 수사관입니다."},
    {"idx": "1", "label": 0, "speaker": "B", "text": "네 무슨 일이시죠?"},
    {"idx": "2", "label": 1, "speaker": "A", "text": "지금 당장 계좌의 잔액을 안전계좌로 이체하셔야 합니다."}
  ]
}
"""

# ✅ 입력/출력 폴더 설정
input_root = "./Simple_DataSet"
output_root = "./results"

# ✅ 모든 하위 폴더 순회
for root, dirs, files in os.walk(input_root):
    for filename in files:
        if not filename.endswith(".txt"):
            continue

        # 입력 파일 경로
        input_path = os.path.join(root, filename)

        # 출력 경로 (입력 폴더 구조 그대로 반영)
        relative_path = os.path.relpath(input_path, input_root)
        output_path = os.path.join(output_root, relative_path)
        output_path = output_path.replace(".txt", ".json")

        # 출력 폴더가 없으면 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # ✅ 이미 결과 파일이 존재하면 스킵
        if os.path.exists(output_path):
            print(f"⏩ Skipping (already exists): {output_path}")
            continue
        
        print(f"🔍 Processing: {relative_path}")

        # 파일 읽기
        with open(input_path, "r", encoding="utf-8") as f:
            conversation = f.read().strip()

        try:
            # ✅ API 호출
            response = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": conversation}
                ]
            )

            content = response.choices[0].message.content.strip()

            # ✅ JSON 파싱 시도
            try:
                result_json = json.loads(content)
            except json.JSONDecodeError:
                print(f"⚠️ JSON 파싱 실패: {relative_path}")
                result_json = {"raw_response": content}

            # ✅ 결과 저장
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)

            print(f"✅ Saved: {output_path}")

        except Exception as e:
            print(f"❌ Error processing {relative_path}: {e}")
