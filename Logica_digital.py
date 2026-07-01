import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


class _ScriptConsole(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                                     QTextEdit, QFileDialog, QComboBox, QLabel)
        self.setWindowTitle("Consola de scripts (Python)")
        self.resize(700, 500)

        main_layout = QVBoxLayout(self)

        toolbar_layout = QHBoxLayout()

        self.example_combo = QComboBox(self)
        self.example_combo.addItem("Seleccionar ejemplo…")
        for name in SCRIPT_EXAMPLES.keys():
            self.example_combo.addItem(name)
        self.example_combo.currentIndexChanged.connect(self._cargar_ejemplo)
        toolbar_layout.addWidget(QLabel("Ejemplos:", self))
        toolbar_layout.addWidget(self.example_combo)

        load_btn = QPushButton("Cargar", self)
        load_btn.setToolTip("Cargar un script desde un archivo .py")
        load_btn.clicked.connect(self._cargar_script)
        toolbar_layout.addWidget(load_btn)

        save_btn = QPushButton("Guardar", self)
        save_btn.setToolTip("Guardar el script actual a un archivo .py")
        save_btn.clicked.connect(self._guardar_script)
        toolbar_layout.addWidget(save_btn)

        run_btn = QPushButton("Ejecutar", self)
        run_btn.setToolTip("Ejecutar el código Python en el contexto actual")
        run_btn.clicked.connect(self._ejecutar_codigo)
        toolbar_layout.addWidget(run_btn)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        self.code_edit = QTextEdit(self)
        self.code_edit.setPlaceholderText(
            "Escribe tu código Python aquí\nPor ejemplo:\n"
            "for c in componentes:\n    print(c.nombre, c.tipo)"
        )
        main_layout.addWidget(self.code_edit, stretch=3)

        self.output_edit = QTextEdit(self)
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Salida del script…")
        main_layout.addWidget(self.output_edit, stretch=2)

    def _cargar_ejemplo(self, index: int) -> None:
        if index <= 0:
            return
        example_name = list(SCRIPT_EXAMPLES.keys())[index - 1]
        script_code = SCRIPT_EXAMPLES.get(example_name, "")
        self.code_edit.setPlainText(script_code)

    def _guardar_script(self) -> None:
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar script",
            str(Path.cwd() / "script.py"),
            "Archivos Python (*.py);;Todos los archivos (*)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.code_edit.toPlainText())
            except Exception as exc:
                mostrar_error_detallado(self, "Guardar script", exc)

    def _cargar_script(self) -> None:
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar script",
            str(Path.cwd()),
            "Archivos Python (*.py);;Todos los archivos (*)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.code_edit.setPlainText(f.read())
            except Exception as exc:
                mostrar_error_detallado(self, "Cargar script", exc)

    def _ejecutar_codigo(self) -> None:
        import io
        import contextlib
        codigo = self.code_edit.toPlainText()
        salida_buff = io.StringIO()
        sim_ref = self.parent()
        env = {
            'sim': sim_ref,
            'componentes': getattr(sim_ref, 'componentes', []),
            'conexiones': getattr(sim_ref, 'conexiones', []),
            'preferences': preferences,
            'interpretar_valor_prefijo': interpretar_valor_prefijo,
            'formatear_valor_con_prefijo': formatear_valor_con_prefijo,
            'simulation_core': simulation_core,
            'llamar_hooks': llamar_hooks,
        }
        try:
            with contextlib.redirect_stdout(salida_buff), contextlib.redirect_stderr(salida_buff):
                exec(codigo, env)
        except Exception as exc:
            print(exc)
        self.output_edit.setPlainText(salida_buff.getvalue())


def abrir_consola_scripts(self) -> None:
    dlg = _ScriptConsole(self)
    dlg.exec_()


def simular_logica(self) -> None:
    from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
    try:
        api = SimulationAPI(self.componentes)
        rows, columns = api.tabla_verdad_digital_extendida()
        if not rows or not columns:
            QMessageBox.information(
                self, "Tabla de verdad", "No se encontraron compuertas lógicas en el circuito.")
            return
        net_name_map = getattr(api, 'last_net_name_map', {})
        if net_name_map:
            try:
                model = ModelBuilder.desde_escena(self.componentes)
                comp_by_name = {comp.name: comp for comp in model.components}
            except Exception:
                comp_by_name = {}
            for comp in self.componentes:
                if not hasattr(comp, 'logic_inputs'):
                    continue
                mcomp = comp_by_name.get(getattr(comp, 'nombre', None))
                if mcomp is None or not mcomp.pins:
                    continue
                try:
                    num_inputs = len(comp.logic_inputs)
                    output_pin = mcomp.pins[-1] if mcomp.pins else None
                    output_net = output_pin.net_id if output_pin else None
                    input_names: List[str] = []
                    for idx in range(num_inputs):
                        if idx < len(mcomp.pins):
                            pin_net = mcomp.pins[idx].net_id
                            name = net_name_map.get(pin_net)
                            if name is None:
                                name = chr(ord('A') + idx)
                            input_names.append(name)
                    out_name = net_name_map.get(output_net, None)
                    if out_name is None:
                        out_name = 'Y'
                    comp.establecer_nombres_logicos(input_names, out_name)
                except Exception:
                    continue
        dlg = DigitalTruthTableDialog(rows, columns, parent=self)
        dlg.exec_()
        try:
            functions_info = api.expresiones_booleanas_digitales()
        except Exception:
            functions_info = {}
        if functions_info:
            expr_lines: list[str] = []
            lang = CURRENT_LANGUAGE if 'CURRENT_LANGUAGE' in globals() else 'es'
            if lang == 'en':
                canonical_label = 'Canonical'
                simplified_label = 'Simplified'
            else:
                canonical_label = 'Canónica'
                simplified_label = 'Simplificada'
            for out_name, exprs in functions_info.items():
                canonical_expr = exprs.get('canonical', '')
                simplified_expr = exprs.get('simplified', '')
                line = f"{out_name}:\n  {canonical_label}: {canonical_expr}\n  {simplified_label}: {simplified_expr}"
                expr_lines.append(line)
            expr_text = "\n\n".join(expr_lines)
            try:
                QMessageBox.information(self, "Funciones booleanas", expr_text)
            except Exception:
                print(expr_text)
    except Exception as exc:
        try:
            QMessageBox.critical(
                self, "Error", f"No se pudo generar la tabla de verdad: {exc}")
        except Exception:
            pass


def aplicar_a(clase=None):
    clase = clase or _base.CircuitSimulator
    if 'abrir_consola_scripts' in globals():
        setattr(clase, 'abrir_consola_scripts', abrir_consola_scripts)
    if 'simular_logica' in globals():
        setattr(clase, 'simular_logica', simular_logica)
    if '_ScriptConsole' in globals():
        _base._ScriptConsole = _ScriptConsole
    return clase
