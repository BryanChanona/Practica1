#!/usr/bin/env python3
"""
scanner_gui.py

Interfaz gráfica para tu analizador léxico.
- Usa el diccionario y la regex que compartiste.
- Muestra resultados en una tabla.
- Puede guardar tokens_salida.txt y generar dfa_trie.dot (Graphviz).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os

# -------------------------
# Config / Regex (tu versión)
# -------------------------
REGEX_IDENT = re.compile(r'^[a-z][a-z0-9]*$') # la que ya usabas

DEFAULT_DICC = "diccionario.txt"
DEFAULT_INPUT = "texto_entrada.txt"
DEFAULT_OUTPUT = "tokens_salida.txt"
DEFAULT_DFA_DOT = "dfa_trie.dot"

# -------------------------
# Lógica del analizador (basada en tu código)
# -------------------------
def cargar_diccionario(ruta):
    dicc = {}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                s = linea.strip()
                if not s or s.startswith("#"):
                    continue
                parts = s.split()
                if len(parts) >= 2:
                    tipo, lexema = parts[0], parts[1]
                else:
                    # si hay una sola columna asumimos "lexema TOKEN" no dado -> TOKEN inferido
                    lexema = parts[0]
                    tipo = f"KW_{lexema.upper()}"
                dicc[lexema] = tipo
    except FileNotFoundError:
        raise
    return dicc

def analizar_palabra(palabra, dicc):
    if palabra in dicc:
        return dicc[palabra], palabra
    if REGEX_IDENT.match(palabra):
        return "IDENTIFICADOR", palabra
    return "ERROR_LEXICO", palabra

def tokenizar_con_split(texto):
    # Comportamiento original: split por whitespace
    return texto.split()

def tokenizar_por_regex(texto):
    # Extrae secuencias de letras/dígitos/underscore (más robusto en presencia de puntuación)
    return re.findall(r"[A-Za-z0-9_]+", texto)

def procesar_texto(texto, dicc, metodo="split"):
    if metodo == "split":
        palabras = tokenizar_con_split(texto)
    else:
        palabras = tokenizar_por_regex(texto)
    resultados = []
    for p in palabras:
        token, lex = analizar_palabra(p, dicc)
        resultados.append((token, lex))
    return resultados

# -------------------------
# Generar DFA (trie) en DOT (Graphviz)
# -------------------------
def build_trie_dot(keywords, out_path=DEFAULT_DFA_DOT):
    """
    Construye un trie a partir de las palabras clave y lo escribe en formato .dot
    Cada nodo es un estado; los estados finales (palabras completas) se marcan doblecercado.
    """
    # construimos trie como diccionario de nodos
    trie = {}
    end_states = set()
    next_id = 0
    root = 0
    trie[root] = {}  # node_id -> {char: child_id}

    def new_node():
        nonlocal next_id, trie
        next_id += 1
        trie[next_id] = {}
        return next_id

    # construir trie
    for word in sorted(keywords):
        cur = root
        for ch in word:
            if ch not in trie[cur]:
                nid = new_node()
                trie[cur][ch] = nid
            cur = trie[cur][ch]
        end_states.add(cur)

    # escribir dot
    lines = []
    lines.append('digraph Trie {')
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=circle];')
    # marcar estados
    for nid in trie:
        attrs = []
        if nid == root:
            attrs.append('label="q0"')
        else:
            attrs.append(f'label="{nid}"')
        if nid in end_states:
            attrs.append('peripheries=2')  # doble círculo para finales
        lines.append(f'  n{nid} [{", ".join(attrs)}];')
    # aristas con etiqueta de caracter
    for nid, edges in trie.items():
        for ch, child in edges.items():
            # escapar comillas si es necesario
            label = ch.replace('"', '\\"')
            lines.append(f'  n{nid} -> n{child} [label="{label}"];')
    lines.append('}')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out_path

# -------------------------
# GUI
# -------------------------
class ScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador Léxico - WarmHeart (GUI)")
        self.geometry("980x640")
        self.minsize(900, 560)

        # variables
        self.dic_path = tk.StringVar(value=DEFAULT_DICC)
        self.input_path = tk.StringVar(value=DEFAULT_INPUT)
        self.tokenizar_metodo = tk.StringVar(value="split")  # 'split' o 'regex'

        # UI layout
        self._build_topframe()
        self._build_editors()
        self._build_results()
        self._build_statusbar()

    def _build_topframe(self):
        frame = ttk.Frame(self, padding=(6,6))
        frame.pack(side="top", fill="x")

        ttk.Label(frame, text="Diccionario:").pack(side="left")
        ttk.Entry(frame, textvariable=self.dic_path, width=40).pack(side="left", padx=6)
        ttk.Button(frame, text="Abrir", command=self._open_dic_file).pack(side="left")
        ttk.Button(frame, text="Guardar dicc (save as)", command=self._save_dic_file).pack(side="left", padx=(6,0))

        ttk.Label(frame, text="   Archivo entrada:").pack(side="left", padx=(12,0))
        ttk.Entry(frame, textvariable=self.input_path, width=40).pack(side="left", padx=6)
        ttk.Button(frame, text="Abrir", command=self._open_input_file).pack(side="left")

        # método tokenización
        ttk.Label(frame, text="   Tokenizar:").pack(side="left", padx=(12,0))
        r1 = ttk.Radiobutton(frame, text="split()", variable=self.tokenizar_metodo, value="split")
        r2 = ttk.Radiobutton(frame, text="regex (alnum/_)", variable=self.tokenizar_metodo, value="regex")
        r1.pack(side="left"); r2.pack(side="left")

        ttk.Button(frame, text="Analizar", command=self._action_analizar).pack(side="right", padx=8)
        ttk.Button(frame, text="Guardar tokens", command=self._action_guardar_tokens).pack(side="right")

    def _build_editors(self):
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(side="top", fill="both", expand=True, padx=6, pady=6)

        # Diccionario editor
        left = ttk.Labelframe(paned, text="Diccionario (lexema token)")
        paned.add(left, weight=1)
        self.txt_dic = tk.Text(left, wrap="none", height=15)
        self.txt_dic.pack(fill="both", expand=True)
        btn_load = ttk.Button(left, text="Cargar desde archivo", command=self._open_dic_file)
        btn_load.pack(anchor="e", padx=6, pady=6)

        # Input editor
        right = ttk.Labelframe(paned, text="Texto de entrada")
        paned.add(right, weight=2)
        self.txt_input = tk.Text(right, wrap="word")
        self.txt_input.pack(fill="both", expand=True)
        btn_load_in = ttk.Button(right, text="Cargar desde archivo", command=self._open_input_file)
        btn_load_in.pack(anchor="e", padx=6, pady=6)

    def _build_results(self):
        frame = ttk.Labelframe(self, text="Resultados / Tokens")
        frame.pack(side="top", fill="both", expand=False, padx=6, pady=(0,6))

        columns = ("token", "lexema")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        self.tree.heading("token", text="Token")
        self.tree.heading("lexema", text="Lexema")
        self.tree.column("token", width=160, anchor="w")
        self.tree.column("lexema", width=640, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # acciones debajo
        subframe = ttk.Frame(self)
        subframe.pack(side="top", fill="x", padx=6)
        ttk.Button(subframe, text="Generar DFA (.dot)", command=self._action_generar_dfa).pack(side="left")
        ttk.Button(subframe, text="Limpiar tabla", command=lambda: self._llenar_tabla([])).pack(side="left", padx=6)
        ttk.Button(subframe, text="Refrescar editores (archivo -> editor)", command=self._refresh_editors_from_files).pack(side="right")

    def _build_statusbar(self):
        self.status = tk.StringVar(value="Listo")
        bar = ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w")
        bar.pack(side="bottom", fill="x")

    # ---------- acciones ----------
    def _open_dic_file(self):
        path = filedialog.askopenfilename(title="Abrir diccionario", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            self.dic_path.set(path)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.txt_dic.delete("1.0", tk.END)
                self.txt_dic.insert("1.0", content)
                self.status.set(f"Diccionario cargado: {path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer diccionario:\n{e}")

    def _save_dic_file(self):
        path = filedialog.asksaveasfilename(title="Guardar diccionario", defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.txt_dic.get("1.0", tk.END))
                self.status.set(f"Diccionario guardado: {path}")
                self.dic_path.set(path)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _open_input_file(self):
        path = filedialog.askopenfilename(title="Abrir texto entrada", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            self.input_path.set(path)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.txt_input.delete("1.0", tk.END)
                self.txt_input.insert("1.0", content)
                self.status.set(f"Entrada cargada: {path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer archivo:\n{e}")

    def _refresh_editors_from_files(self):
        # recarga los contenidos actuales de los rutas (si existen)
        dpath = self.dic_path.get()
        ipath = self.input_path.get()
        if os.path.isfile(dpath):
            with open(dpath, "r", encoding="utf-8") as f:
                self.txt_dic.delete("1.0", tk.END)
                self.txt_dic.insert("1.0", f.read())
        if os.path.isfile(ipath):
            with open(ipath, "r", encoding="utf-8") as f:
                self.txt_input.delete("1.0", tk.END)
                self.txt_input.insert("1.0", f.read())
        self.status.set("Editores actualizados desde archivos (si existían)")

    def _action_analizar(self):
        # leer diccionario del editor (no solo del archivo)
        dic_text = self.txt_dic.get("1.0", tk.END).strip()
        # si el editor está vacío, intentamos cargar desde la ruta
        if not dic_text and os.path.isfile(self.dic_path.get()):
            try:
                with open(self.dic_path.get(), "r", encoding="utf-8") as f:
                    dic_text = f.read()
            except:
                dic_text = ""
        # guardamos temporalmente a un archivo para usar cargar_diccionario u parseamos directamente
        # parseamos directamente para que se acepte formato "lexema token" por línea
        dicc = {}
        for line in dic_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) >= 2:
                tipo, lexema = parts[0], parts[1]
            else:
                lexema = parts[0]
                tipo = f"KW_{lexema.upper()}"
            dicc[lexema] = tipo

        input_text = self.txt_input.get("1.0", tk.END)
        metodo = self.tokenizar_metodo.get()
        resultados = procesar_texto(input_text, dicc, metodo=metodo)
        self._llenar_tabla(resultados)
        self.last_resultados = resultados
        self.status.set(f"Análisis completado — {len(resultados)} tokens procesados")

    def _llenar_tabla(self, rows):
        # limpiar
        for i in self.tree.get_children():
            self.tree.delete(i)
        # llenar
        for tok, lex in rows:
            self.tree.insert("", tk.END, values=(tok, lex))

    def _action_guardar_tokens(self):
        # guardar a archivo (preguntar ruta)
        path = filedialog.asksaveasfilename(title="Guardar tokens_salida", initialfile=DEFAULT_OUTPUT, defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not path:
            return
        rows = getattr(self, "last_resultados", None)
        if rows is None:
            messagebox.showinfo("Info", "Primero ejecuta el análisis para generar tokens.")
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Token,Lexema\n")
                for tok, lex in rows:
                    f.write(f"{tok},{lex}\n")
            self.status.set(f"Tokens guardados en: {path}")
            messagebox.showinfo("Guardado", f"Tokens guardados correctamente en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar tokens:\n{e}")

    def _action_generar_dfa(self):
        # intenta generar DFA a partir del diccionario actual en editor
        dic_text = self.txt_dic.get("1.0", tk.END).strip()
        if not dic_text:
            messagebox.showinfo("Info", "El editor de diccionario está vacío. Añade palabras reservadas y token names.")
            return
        keywords = []
        for line in dic_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) >= 2:
                # asumimos formato "TOKEN LEXEMA" o "lexema token"? El tuyo usaba tipo lexema order (tipo,lexema)
                # En tu ejemplo original hiciste: tipo, lexema = linea.split(); dicc[lexema] = tipo
                # Por consistencia usaremos la segunda columna como lexema si hay 2 columnas.
                lexema = parts[1]
            else:
                lexema = parts[0]
            keywords.append(lexema)
        if not keywords:
            messagebox.showinfo("Info", "No se encontraron lexemas válidos en el diccionario.")
            return
        # generar .dot
        try:
            out = build_trie_dot(keywords, out_path=DEFAULT_DFA_DOT)
            self.status.set(f"DFA (.dot) generado: {out}")
            messagebox.showinfo("DFA generado", f"Archivo DOT creado:\n{out}\n\nConvierte con Graphviz: dot -Tpng {out} -o dfa.png")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar DFA:\n{e}")

# -------------------------
# Main
# -------------------------
def main():
    app = ScannerGUI()
    # si existen archivos por defecto, cargarlos en editores
    if os.path.isfile(DEFAULT_DICC):
        with open(DEFAULT_DICC, "r", encoding="utf-8") as f:
            app.txt_dic.insert("1.0", f.read())
    if os.path.isfile(DEFAULT_INPUT):
        with open(DEFAULT_INPUT, "r", encoding="utf-8") as f:
            app.txt_input.insert("1.0", f.read())
    app.mainloop()

if __name__ == "__main__":
    main()
