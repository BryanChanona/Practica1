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

REGEX_IDENT = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

def analizar_palabra(palabra, dicc):
    # A: palabra reservada
    if palabra in dicc:
        return dicc[palabra], palabra

    # B: identificador válido
    if REGEX_IDENT.match(palabra):
        return "IDENTIFICADOR", palabra

    # C: error léxico
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


if __name__ == "__main__":
    main()
