import re
from pathlib import Path

# Regex para identificador: solo minúsculas, sin guion bajo
REGEX_IDENT_PATTERN = r'^[a-z](?:[a-z0-9]{1,}|[a-z0-9]{0,})$'
REGEX_IDENT = re.compile(REGEX_IDENT_PATTERN)

# Paths por defecto (carpeta del proyecto Practica1)
BASE_DIR = Path(__file__).parent
DEFAULT_DICC = str(BASE_DIR / "diccionario.txt")
DEFAULT_INPUT = str(BASE_DIR / "texto_entrada.txt")
DEFAULT_OUTPUT = str(BASE_DIR / "tokens_salida.txt")
DEFAULT_DFA_DOT = str(BASE_DIR / "dfa_trie.dot")
