# utils_io.py
from pathlib import Path
from typing import Optional

def read_text_file(path: str) -> Optional[str]:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

def write_text_file(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
