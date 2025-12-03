# scanner_core.py
"""
Lógica del analizador léxico:
- cargar_diccionario
- tokenizadores
- analizar_palabra
- procesar_texto
"""

import re
from typing import Dict, List, Tuple
import constants

def cargar_diccionario(ruta: str) -> Dict[str, str]:
    dicc = {}
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            s = linea.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) >= 2:
                tipo, lexema = parts[0], parts[1]
            else:
                lexema = parts[0]
                tipo = f"KW_{lexema.upper()}"
            dicc[lexema] = tipo
    return dicc

def analizar_palabra(palabra: str, dicc: Dict[str, str]) -> Tuple[str, str]:
    if palabra in dicc:
        return dicc[palabra], palabra
    if constants.REGEX_IDENT.match(palabra):
        return "IDENTIFICADOR", palabra
    return "ERROR_LEXICO", palabra

def tokenizar_con_split(texto: str) -> List[str]:
    return texto.split()

def tokenizar_por_regex(texto: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_]+", texto)

def procesar_texto(texto: str, dicc: Dict[str, str], metodo: str = "split") -> List[Tuple[str, str]]:
    if metodo == "split":
        palabras = tokenizar_con_split(texto)
    else:
        palabras = tokenizar_por_regex(texto)
    resultados = [analizar_palabra(p, dicc) for p in palabras]
    return resultados
