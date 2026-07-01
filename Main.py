import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

try:
    from PyQt5.QtWidgets import QApplication
except Exception as exc:
    raise SystemExit(
    ) from exc

try:
    import Interfaz
except ModuleNotFoundError as exc:
    if exc.name == "Interfaz":
        raise SystemExit(
            "No se encontro Interfaz.py. Extrae primero la carpeta completa del ZIP "
            "y ejecuta Main.py desde esa carpeta; no lo abras directamente dentro del ZIP."
        ) from exc
    raise


def cargar_modulos_separados():
    modulos = [
        "Modelo_circuito",
        "Simulacion",
        "Bode",
        "LGR",
        "Calcuadora_de_resistencias",
        "Calculadora_VLSM",
        "Analisis_AC",
        "Laboratorio",
        "Exportaciones",
        "Logica_digital",
    ]
    for nombre in modulos:
        try:
            modulo = __import__(nombre)
            aplicar = getattr(modulo, "aplicar_a", None)
            if aplicar is not None:
                aplicar(Interfaz.CircuitSimulator)
        except Exception as exc:
            try:
                Interfaz.logger.warning(
                    "No se pudo cargar módulo %s: %s", nombre, exc)
            except Exception:
                print(f"No se pudo cargar módulo {nombre}: {exc}")


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    cargar_modulos_separados()

    if "--cli" in argv:
        cli_args = [arg for arg in argv[1:] if arg != "--cli"]
        return Interfaz.ejecutar_cli(cli_args)

    if "--run-tests" in argv:
        ok = Interfaz.ejecutar_pruebas_internas(verbose=True)
        return 0 if ok else 1

    app = QApplication(argv)
    ventana = Interfaz.MultiTabWindow()
    ventana.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
