import re

# -------------------------------
# Cargar diccionario
# -------------------------------
def cargar_diccionario(ruta):
    dicc = {}
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            tipo, lexema = linea.strip().split()
            dicc[lexema] = tipo
    return dicc


# -------------------------------
# Analizador Léxico
# -------------------------------

# Regex de identificadores
REGEX_IDENT = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

def analizar_palabra(palabra, dicc):
    # Paso A: es palabra clave?
    if palabra in dicc:
        return dicc[palabra], palabra

    # Paso B: es identificador válido?
    if REGEX_IDENT.match(palabra):
        return "IDENTIFICADOR", palabra

    # Paso C: error lexicográfico
    return "ERROR_LEXICO", palabra


# -------------------------------
# Programa Principal
# -------------------------------
def main():
    diccionario = cargar_diccionario("diccionario.txt")

    with open("texto_entrada.txt", "r", encoding="utf-8") as f:
        contenido = f.read()

    palabras = contenido.split()

    with open("tokens_salida.txt", "w", encoding="utf-8") as out:
        out.write("Token,Lexema\n")
        for palabra in palabras:
            token, lex = analizar_palabra(palabra, diccionario)
            out.write(f"{token},{lex}\n")


if _name_ == "_main_":
    main()