import os
import json
from common.prompt_loader import load_prompt
from common.file_utils import load_json, save_json
from common.llm_client import GeminiClient
from common.response_parser import safe_parse_response_json

PROMPT_PATH = "./prompts/labeling.txt"
INPUT_DIR = "./input_data"
OUTPUT_DIR = "./results/gemini"

system_prompt = load_prompt(PROMPT_PATH)
llm = GeminiClient()

# INPUT_DIR 내의 파일 목록 순회
for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".json"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    # 출력 폴더 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 이미 존재하면 스킵
    if os.path.exists(output_path):
        print(f"⏩ Skipping (already exists): {output_path}")
        continue

    print(f"🔍 Processing: {filename}")

    input_json = load_json(input_path)

    result_text = llm.generate(
        system_prompt=system_prompt,
        user_content=json.dumps(input_json, ensure_ascii=False)
    )

    # ✅ 안전한 JSON 파싱 적용
    result_json = safe_parse_response_json(result_text, filename)

    save_json(output_path, result_json)
    print(f"✅ Gemini Saved: {output_path}")
