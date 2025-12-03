# main.py
from gui import ScannerGUI
import constants
import os

def main():
    # Crear archivos de ejemplo si no existen
    if not os.path.exists(constants.DEFAULT_DICC):
        sample = "\n".join([
            "KW_SI si",
            "KW_SINO sino",
            "KW_MIENTRAS mientras",
            "KW_REPITE repite",
            "KW_HASTA hasta",
            "KW_INICIO inicio",
            "KW_FIN fin",
            "KW_IMPRIMIR imprimir",
        ])
        with open(constants.DEFAULT_DICC, "w", encoding="utf-8") as f:
            f.write(sample)
    if not os.path.exists(constants.DEFAULT_INPUT):
        sample_input = "si contador es_mayor Que diez inicio mientras repite imprimir saludo hasta contador fin"
        with open(constants.DEFAULT_INPUT, "w", encoding="utf-8") as f:
            f.write(sample_input)

    app = ScannerGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
