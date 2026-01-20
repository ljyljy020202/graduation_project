import os
import json
from common.prompt_loader import load_prompt
from common.file_utils import load_json, save_json
from common.llm_client import GeminiClient
from common.response_parser import safe_parse_response_json

PROMPT_PATH = "./prompts/labeling_prompt.txt"
INPUT_ROOT = "./Simple_DataSet"
OUTPUT_ROOT = "./results/gemini"

system_prompt = load_prompt(PROMPT_PATH)
llm = GeminiClient()

# ✅ 모든 하위 폴더 순회 (계층 구조 대응)
for root, dirs, files in os.walk(INPUT_ROOT):
    for filename in files:
        if not filename.endswith(".json"):
            continue

        input_path = os.path.join(root, filename)

        # 입력 구조 그대로 출력에 반영
        relative_path = os.path.relpath(input_path, INPUT_ROOT)
        output_path = os.path.join(OUTPUT_ROOT, relative_path)

        # 출력 폴더 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 이미 존재하면 스킵
        if os.path.exists(output_path):
            print(f"⏩ Skipping (already exists): {output_path}")
            continue

        print(f"🔍 Processing: {relative_path}")

        input_json = load_json(input_path)

        result_text = llm.generate(
            system_prompt=system_prompt,
            user_content=json.dumps(input_json, ensure_ascii=False)
        )

        # ✅ 안전한 JSON 파싱
        result_json = safe_parse_response_json(result_text, relative_path)

        save_json(output_path, result_json)
        print(f"✅ Gemini Saved: {output_path}")