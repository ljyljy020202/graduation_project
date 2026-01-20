import os

def load_prompt(prompt_path: str) -> str:
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"프롬프트 파일이 존재하지 않습니다: {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()
