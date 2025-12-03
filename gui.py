# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import scanner_core
import dfa_trie
import constants
from pathlib import Path

class ScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador Léxico - Práctica1 (GUI)")
        self.geometry("980x640")
        self.minsize(900, 560)

        self.dic_path = tk.StringVar(value=constants.DEFAULT_DICC)
        self.input_path = tk.StringVar(value=constants.DEFAULT_INPUT)
        self.tokenizar_metodo = tk.StringVar(value="split")

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

        ttk.Label(frame, text="   Tokenizar:").pack(side="left", padx=(12,0))
        r1 = ttk.Radiobutton(frame, text="split()", variable=self.tokenizar_metodo, value="split")
        r2 = ttk.Radiobutton(frame, text="regex (alnum/_)", variable=self.tokenizar_metodo, value="regex")
        r1.pack(side="left"); r2.pack(side="left")

        ttk.Button(frame, text="Analizar", command=self._action_analizar).pack(side="right", padx=8)
        ttk.Button(frame, text="Guardar tokens", command=self._action_guardar_tokens).pack(side="right")

    def _build_editors(self):
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(side="top", fill="both", expand=True, padx=6, pady=6)

        left = ttk.Labelframe(paned, text="Diccionario (lexema token)")
        paned.add(left, weight=1)
        self.txt_dic = tk.Text(left, wrap="none", height=15)
        self.txt_dic.pack(fill="both", expand=True)
        ttk.Button(left, text="Cargar desde archivo", command=self._open_dic_file).pack(anchor="e", padx=6, pady=6)

        right = ttk.Labelframe(paned, text="Texto de entrada")
        paned.add(right, weight=2)
        self.txt_input = tk.Text(right, wrap="word")
        self.txt_input.pack(fill="both", expand=True)
        ttk.Button(right, text="Cargar desde archivo", command=self._open_input_file).pack(anchor="e", padx=6, pady=6)

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

        subframe = ttk.Frame(self)
        subframe.pack(side="top", fill="x", padx=6)
        ttk.Button(subframe, text="Generar DFA (.dot)", command=self._action_generar_dfa).pack(side="left")
        ttk.Button(subframe, text="Limpiar tabla", command=lambda: self._llenar_tabla([])).pack(side="left", padx=6)
        ttk.Button(subframe, text="Refrescar editores (archivo -> editor)", command=self._refresh_editors_from_files).pack(side="right")

    def _build_statusbar(self):
        self.status = tk.StringVar(value="Listo")
        bar = ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w")
        bar.pack(side="bottom", fill="x")

    def _open_dic_file(self):
        path = filedialog.askopenfilename(title="Abrir diccionario", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            self.dic_path.set(path)
            with open(path, "r", encoding="utf-8") as f:
                self.txt_dic.delete("1.0", "end")
                self.txt_dic.insert("1.0", f.read())
            self.status.set(f"Diccionario cargado: {path}")

    def _save_dic_file(self):
        path = filedialog.asksaveasfilename(title="Guardar diccionario", defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.txt_dic.get("1.0", "end"))
            self.dic_path.set(path)
            self.status.set(f"Diccionario guardado: {path}")

    def _open_input_file(self):
        path = filedialog.askopenfilename(title="Abrir texto entrada", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            self.input_path.set(path)
            with open(path, "r", encoding="utf-8") as f:
                self.txt_input.delete("1.0", "end")
                self.txt_input.insert("1.0", f.read())
            self.status.set(f"Entrada cargada: {path}")

    def _refresh_editors_from_files(self):
        dpath = self.dic_path.get()
        ipath = self.input_path.get()
        if os.path.isfile(dpath):
            with open(dpath, "r", encoding="utf-8") as f:
                self.txt_dic.delete("1.0", "end")
                self.txt_dic.insert("1.0", f.read())
        if os.path.isfile(ipath):
            with open(ipath, "r", encoding="utf-8") as f:
                self.txt_input.delete("1.0", "end")
                self.txt_input.insert("1.0", f.read())
        self.status.set("Editores actualizados desde archivos (si existían)")

    def _action_analizar(self):
        dic_text = self.txt_dic.get("1.0", "end").strip()
        if not dic_text and os.path.isfile(self.dic_path.get()):
            with open(self.dic_path.get(), "r", encoding="utf-8") as f:
                dic_text = f.read()

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

        input_text = self.txt_input.get("1.0", "end")
        metodo = self.tokenizar_metodo.get()
        resultados = scanner_core.procesar_texto(input_text, dicc, metodo=metodo)
        self._llenar_tabla(resultados)
        self.last_resultados = resultados
        self.status.set(f"Análisis completado — {len(resultados)} tokens procesados")

    def _llenar_tabla(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for tok, lex in rows:
            self.tree.insert("", "end", values=(tok, lex))

    def _action_guardar_tokens(self):
        path = filedialog.asksaveasfilename(title="Guardar tokens_salida", initialfile=Path(constants.DEFAULT_OUTPUT).name, defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not path:
            return
        rows = getattr(self, "last_resultados", None)
        if rows is None:
            messagebox.showinfo("Info", "Primero ejecuta el análisis para generar tokens.")
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("Token,Lexema\n")
            for tok, lex in rows:
                f.write(f"{tok},{lex}\n")
        self.status.set(f"Tokens guardados en: {path}")
        messagebox.showinfo("Guardado", f"Tokens guardados correctamente en:\n{path}")

    def _action_generar_dfa(self):
        dic_text = self.txt_dic.get("1.0", "end").strip()
        if not dic_text:
            messagebox.showinfo("Info", "El editor de diccionario está vacío. Añade palabras reservadas y token names.")
            return
        keywords = []
        for line in dic_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            lexema = parts[1] if len(parts) >= 2 else parts[0]
            keywords.append(lexema)
        out = dfa_trie.build_trie_dot(keywords, constants.DEFAULT_DFA_DOT)
        self.status.set(f"DFA (.dot) generado: {out}")
        messagebox.showinfo("DFA generado", f"Archivo DOT creado:\n{out}\n\nConvierte con Graphviz: dot -Tpng {out} -o dfa.png")
