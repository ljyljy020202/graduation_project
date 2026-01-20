import json

def safe_parse_response_json(content: str, output_filename: str):
    """
    모델 응답(content)을 최대한 JSON으로 파싱하려고 시도.
    - 1차: 그대로 json.loads
    - 2차: ``` 코드블록 감싸진 경우 코드블록 제거 후 다시 시도
    - 다 안 되면 {"raw_response": content} 형태로 반환
    """
    # 1차 시도
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 2차 시도: 코드블록 제거
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        inner = "\n".join(lines).strip()
        try:
            return json.loads(inner)
        except json.JSONDecodeError:
            print(f"⚠️ JSON 파싱 실패 (코드블록 제거 후도 실패): {output_filename}")

    print(f"⚠️ JSON 파싱 실패: {output_filename} (raw_response로 저장)")
    return {"raw_response": content}
