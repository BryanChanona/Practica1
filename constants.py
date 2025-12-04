import re
from pathlib import Path

# 
REGEX_IDENT_PATTERN = r'^HOLA[a-z]+$'
REGEX_IDENT = re.compile(REGEX_IDENT_PATTERN)

# Paths por defecto 
BASE_DIR = Path(__file__).parent
DEFAULT_DICC = str(BASE_DIR / "diccionario.txt")
DEFAULT_INPUT = str(BASE_DIR / "texto_entrada.txt")
DEFAULT_OUTPUT = str(BASE_DIR / "tokens_salida.txt")
DEFAULT_DFA_DOT = str(BASE_DIR / "dfa_trie.dot")
