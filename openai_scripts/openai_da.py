import os
import json
from openai import OpenAI

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key="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")

# ✅ 라벨링용 프롬프트 (system 메시지)
SYSTEM_PROMPT = """
# Role
당신은 한국어 구어체 데이터 증강 전문가입니다. 주어진 보이스피싱 대화 데이터를 기반으로, 내용은 동일하지만 표현이 다른 새로운 대화 데이터를 생성하는 것이 임무입니다.

# Task
제공된 [Original Data]의 대화 흐름, 사기 수법, 핵심 내용은 **그대로 유지**하세요.
대신, 화자의 말투, 어휘, 문장 구조, 감정 상태를 변경하여 **새로운 버전의 대화(Variation)**를 생성하세요.

# Input Data Format (Example)
{
  "conversation_id": 177,
  "conversation_label": 1,
  "utterances": [
    { "idx": 0, "speaker": "A", "text": "네 여보세요?" },
    ... (중략) ...
    { "idx": 19, "speaker": "B", "text": "네" }
  ]
}

# Variation Guide (이 지침에 맞춰 변형하세요)
1. **화자 A (사기꾼):**
   - 원본과 다른 어휘를 사용하되, 목적(계좌 요구, 협박 등)은 유지하세요.
   - 예: "선지급 해드리고" -> "미리 입금 처리 도와드리고", "사장님" -> "고객님"
2. **화자 B (피해자):**
   - 반응의 뉘앙스를 바꾸세요. (예: 원본이 단순 대답이라면 -> 조금 더 의심하거나, 혹은 더 순진하게 반응하도록 변경)
   - 예: "네 가입한 적 없는데요" -> "아니요, 저는 그런 거 가입 안 했는데요?"
3. **내용 변형:**
   - 원본 대화의 의도와 핵심 흐름은 반드시 유지하십시오.
   - 단, 문장 표현, 단어 선택, 어조는 새롭게 창작하십시오.
4. **구조적 유연성:**
   - **반드시 원본과 발화(Utterance) 개수를 똑같이 맞출 필요는 없습니다.**
   - 대화가 더 자연스럽다면, 짧은 두 문장을 하나로 합치거나 긴 문장을 두 개로 나누어도 됩니다.
   - 예:
     [원본] A: "여보세요?" / A: "김철수님 맞으세요?" (2줄)
     [생성] A: "네, 여보세요. 혹시 김철수 고객님 본인 맞으십니까?" (1줄)
5. **형식 준수:**
   - 결과는 반드시 지정된 JSON 형식을 따라야 합니다.
   - `idx`는 0부터 다시 순차적으로 매기십시오.

# Request
위 가이드라인에 따라 서로 다른 시나리오의 데이터 3개를 생성해 주세요. 응답은 다른 문자열이나 기호 없이 3개의 JSON 객체로 구성된 JSON 리스트만 반환해주세요.

"""

# 입력/출력 폴더 설정
input_root = "./Test_DataSet/Abnormal"
output_root = "./LLM_DA_result/results_gpt_5_nano/Abnormal"

# test_data 폴더 내의 파일 목록 순회
for filename in os.listdir(input_root):
    if not filename.endswith(".json"):
        continue

    # 입력 파일 경로
    input_path = os.path.join(input_root, filename)

    # 출력 파일명 (같은 이름으로 저장)
    output_path = os.path.join(output_root, filename)

    # 출력 폴더 생성
    os.makedirs(output_root, exist_ok=True)

    # 이미 존재하면 스킵
    if os.path.exists(output_path):
        print(f"⏩ Skipping (already exists): {output_path}")
        continue

    print(f"🔍 Processing: {filename}")

    # 파일 읽기
    with open(input_path, "r", encoding="utf-8") as f:
      try:
           input_json = json.load(f)
      except json.JSONDecodeError:
          print(f"❌ JSON 파싱 실패 (입력): {filename}")
          continue

    try:
        # ✅ API 호출
        response = client.chat.completions.create(
        model="gpt-5-nano",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(input_json, ensure_ascii=False)}
            ]
        )

        content = response.choices[0].message.content.strip()

        # ✅ JSON 파싱 시도
        try:
            result_json = json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️ JSON 파싱 실패: {filename}")
            result_json = {"raw_response": content}

        # ✅ 결과 저장
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved: {output_path}")

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
