import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


class ModoLaboratorioDialog(QDialog):
    def __init__(self, parent=None, simulacion: Optional[Tuple[List[str], List[float]]] = None):
        super().__init__(parent)
        self.setWindowTitle("Modo Laboratorio")
        from PyQt5.QtWidgets import QVBoxLayout, QPushButton
        if simulacion is not None:
            self.sim_labels, self.sim_values = simulacion
        else:
            self.sim_labels, self.sim_values = [], []
        self.med_labels: List[str] = []
        self.med_values: List[float] = []
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.btn_cargar = QPushButton("Cargar medición")
        self.btn_cargar.clicked.connect(self.cargar_medicion)
        layout.addWidget(self.btn_cargar)
        self.graficar()

    def cargar_medicion(self) -> None:
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona archivo de medición",
            "",
            "CSV (*.csv);;Todos los archivos (*.*)"
        )
        if not fname:
            return
        labels: List[str] = []
        values: List[float] = []
        import csv
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    try:
                        label = row[0]
                        val = float(row[1]) if len(row) > 1 else 0.0
                        labels.append(label)
                        values.append(val)
                    except Exception:
                        continue
            self.med_labels = labels
            self.med_values = values
            self.graficar()
        except Exception as exc:
            try:
                QMessageBox.critical(
                    self, "Modo laboratorio", f"No se pudo cargar la medición:\n{exc}")
            except Exception:
                pass

    def graficar(self) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        sim_plotted = False
        med_plotted = False
        if self.sim_values:
            try:
                import numpy as _np
                sim_vals = list(self.sim_values)
                if self.med_values and len(self.med_values) != len(self.sim_values):
                    x_sim = _np.linspace(0, len(sim_vals) - 1, len(sim_vals))
                    x_target = _np.linspace(
                        0, len(sim_vals) - 1, len(self.med_values))
                    sim_vals_interp = _np.interp(x_target, x_sim, sim_vals)
                    x_sim_plot = list(range(len(self.med_values)))
                    ax.plot(x_sim_plot, sim_vals_interp, label="Simulación")
                else:
                    x_sim_plot = list(range(len(sim_vals)))
                    ax.plot(x_sim_plot, sim_vals, label="Simulación")
                sim_plotted = True
            except Exception:
                try:
                    x = list(range(len(self.sim_values)))
                    ax.plot(x, self.sim_values, label="Simulación")
                    sim_plotted = True
                except Exception:
                    pass
        if self.med_values:
            try:
                x_med = list(range(len(self.med_values)))
                ax.plot(x_med, self.med_values, label="Medición")
                med_plotted = True
            except Exception:
                pass
        try:
            if sim_plotted or med_plotted:
                ax.legend()
                ax.set_xlabel("Muestra")
                ax.set_ylabel("Magnitud")
                ax.set_title("Curva simulada vs medida")
                combined = []
                if sim_plotted:
                    combined.extend(self.sim_values)
                if med_plotted:
                    combined.extend(self.med_values)
                valid_vals = [
                    v for v in combined if isinstance(v, (int, float))]
                if valid_vals:
                    y_min = min(valid_vals)
                    y_max = max(valid_vals)
                    if y_min == y_max:
                        margin = 0.1 * abs(y_max) if y_max != 0 else 1.0
                        ax.set_ylim(y_min - margin, y_max + margin)
                    else:
                        margin = 0.1 * (y_max - y_min)
                        ax.set_ylim(y_min - margin, y_max + margin)
                max_len = 0
                if sim_plotted:
                    max_len = max(max_len, len(self.sim_values))
                if med_plotted:
                    max_len = max(max_len, len(self.med_values))
                if max_len > 0:
                    ax.set_xlim(0, max_len - 1)
                ax.grid(True, which='both', linestyle='--', alpha=0.5)
        except Exception:
            pass
        try:
            self.canvas.draw()
        except Exception:
            pass


class TextFormatDialog(QDialog):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        from PyQt5.QtWidgets import (
            QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFontComboBox,
            QSpinBox, QCheckBox, QPushButton, QColorDialog, QWidget, QGridLayout
        )
        from PyQt5.QtGui import QColor
        try:
            self.setWindowTitle(
                traducir('Agregar etiqueta de texto al circuito'))
        except Exception:
            self.setWindowTitle('Agregar texto')
        layout = QVBoxLayout(self)
        form_layout = QGridLayout()
        row = 0
        self.text_input = QLineEdit()
        lbl_text = QLabel(traducir('Texto'))
        form_layout.addWidget(lbl_text, row, 0)
        form_layout.addWidget(self.text_input, row, 1, 1, 2)
        row += 1
        lbl_font = QLabel(traducir('Fuente')
                          if 'Fuente' in TRANSLATIONS else 'Fuente')
        self.font_combo = QFontComboBox()
        try:
            from PyQt5.QtGui import QFontDatabase
            self.font_combo.setWritingSystem(QFontDatabase.Latin)
        except Exception:
            pass
        form_layout.addWidget(lbl_font, row, 0)
        form_layout.addWidget(self.font_combo, row, 1, 1, 2)
        row += 1
        lbl_size = QLabel(traducir('Tamaño')
                          if 'Tamaño' in TRANSLATIONS else 'Tamaño')
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(12)
        form_layout.addWidget(lbl_size, row, 0)
        form_layout.addWidget(self.size_spin, row, 1)
        row += 1
        self.chk_bold = QCheckBox(
            traducir('Negrita') if 'Negrita' in TRANSLATIONS else 'Negrita')
        self.chk_italic = QCheckBox(
            traducir('Cursiva') if 'Cursiva' in TRANSLATIONS else 'Cursiva')
        self.chk_underline = QCheckBox(
            traducir('Subrayado') if 'Subrayado' in TRANSLATIONS else 'Subrayado')
        form_layout.addWidget(self.chk_bold, row, 0)
        form_layout.addWidget(self.chk_italic, row, 1)
        form_layout.addWidget(self.chk_underline, row, 2)
        row += 1
        lbl_color = QLabel(
            traducir('Color') if 'Color' in TRANSLATIONS else 'Color')
        self.color_button = QPushButton()
        self._selected_color = QColor('black')
        self._actualizar_boton_color()
        self.color_button.clicked.connect(self._elegir_color)
        form_layout.addWidget(lbl_color, row, 0)
        form_layout.addWidget(self.color_button, row, 1)
        row += 1
        layout.addLayout(form_layout)
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(
            traducir('Sí') if 'Sí' in TRANSLATIONS else 'OK')
        self.cancel_button = QPushButton(
            traducir('No') if 'No' in TRANSLATIONS else 'Cancel')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def _elegir_color(self) -> None:
        from PyQt5.QtWidgets import QColorDialog
        col = QColorDialog.getColor(self._selected_color, self)
        if col.isValid():
            self._selected_color = col
            self._actualizar_boton_color()

    def _actualizar_boton_color(self) -> None:
        col = self._selected_color.name()
        self.color_button.setStyleSheet(f"background-color: {col};")

    def obtener_valores(self) -> Dict[str, Any]:
        return {
            'text': self.text_input.text(),
            'font_family': self.font_combo.currentFont().family(),
            'font_size': self.size_spin.value(),
            'bold': self.chk_bold.isChecked(),
            'italic': self.chk_italic.isChecked(),
            'underline': self.chk_underline.isChecked(),
            'color': self._selected_color,
        }


class EditorComponentesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor de Componentes")
        from PyQt5.QtWidgets import QFormLayout, QLineEdit, QPushButton, QMessageBox
        layout = QFormLayout(self)
        self.nombre_input = QLineEdit()
        self.pines_input = QLineEdit()
        self.modelo_input = QLineEdit()
        layout.addRow("Nombre del componente:", self.nombre_input)
        layout.addRow("Pines (separados por coma):", self.pines_input)
        layout.addRow("Modelo SPICE:", self.modelo_input)
        self.btn_guardar = QPushButton("Guardar")
        layout.addRow(self.btn_guardar)
        self.btn_guardar.clicked.connect(self.guardar)

    def guardar(self) -> None:
        from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
        nombre = self.nombre_input.text().strip()
        pines_text = self.pines_input.text().strip()
        modelo = self.modelo_input.text().strip()
        if not nombre or not pines_text or not modelo:
            QMessageBox.warning(self, "Editor de Componentes",
                                "Debe completar todos los campos.")
            return
        pines = [p.strip() for p in pines_text.split(",") if p.strip()]
        if not pines:
            QMessageBox.warning(self, "Editor de Componentes",
                                "Debe especificar al menos un pin.")
            return
        try:
            if CUSTOM_COMPONENTS_FILE.exists():
                try:
                    with open(CUSTOM_COMPONENTS_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            else:
                data = {}
            data[nombre] = {"pins": pines, "model": modelo}
            with open(CUSTOM_COMPONENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            try:
                COMPONENT_SYNONYMS.setdefault(nombre.lower(), [nombre.lower()])
            except Exception:
                pass
            QMessageBox.information(
                self, "Editor de Componentes", "Componente guardado correctamente.")
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Editor de Componentes",
                                 f"No se pudo guardar el componente:\n{exc}")


def abrir_modo_laboratorio(self) -> None:
    from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
    try:
        sim_data = None
        if getattr(self, "ultima_grafica", None):
            try:
                volt_labels, volt_values, _cur_labels, _cur_values = self.ultima_grafica
                sim_data = (volt_labels, volt_values)
            except Exception:
                sim_data = None
        if sim_data is None:
            try:
                elementos = self.extraer_topologia()
                nodo_gnd = None
                for comp in self.componentes:
                    if getattr(comp, 'tipo', None) == "GND" and comp.terminales:
                        nodo_gnd = comp.terminales[0].node_group
                        break
                if nodo_gnd is None:
                    raise RuntimeError(
                        "Debes incluir un nodo GND para simular.")
                try:
                    voltajes, corrientes_dict, _ = self.analizar_circuito(
                        elementos, nodo_gnd)
                except Exception as e:
                    raise RuntimeError(str(e))
                nodos_set = set()
                for e in elementos:
                    for n in e["nodos"]:
                        nodos_set.add(n)
                nodos_sorted = sorted(n for n in nodos_set if n != nodo_gnd)
                nodo_idx = {n: i for i, n in enumerate(nodos_sorted)}
                volt_labels = []
                volt_values = []
                for elem in elementos:
                    try:
                        n1, n2 = elem.get("nodos", [None, None])
                        v1 = 0.0 if n1 == nodo_gnd else voltajes[nodo_idx.get(
                            n1, 0)]
                        v2 = 0.0 if n2 == nodo_gnd else voltajes[nodo_idx.get(
                            n2, 0)]
                        dv = abs(v1 - v2)
                        volt_labels.append(elem.get("nombre", ""))
                        volt_values.append(dv)
                    except Exception:
                        continue
                try:
                    self.ultima_grafica = (volt_labels, volt_values, list(
                        corrientes_dict.keys()), list(corrientes_dict.values()))
                except Exception:
                    self.ultima_grafica = None
                sim_data = (volt_labels, volt_values)
            except Exception as exc_sim:
                sim_data = None
                try:
                    QMessageBox.warning(self, traducir(
                        "Simulación inválida"), traducir(str(exc_sim)))
                except Exception:
                    pass
        dlg = ModoLaboratorioDialog(self, simulacion=sim_data)
        dlg.exec_()
    except Exception as exc:
        try:
            QMessageBox.critical(self, "Modo laboratorio",
                                 f"No se pudo abrir el modo laboratorio:\n{exc}")
        except Exception:
            pass


def guardar_medicion_a_db(self) -> None:
    from PyQt5.QtWidgets import QInputDialog, QMessageBox
    equipo, ok1 = QInputDialog.getText(
        self, "Guardar Medición", "Equipo de medición:")
    if not ok1:
        return
    circuito, ok2 = QInputDialog.getText(self, "Guardar Medición", "Circuito:")
    if not ok2:
        return
    parametros, ok3 = QInputDialog.getText(
        self, "Guardar Medición", "Parámetros de prueba:")
    if not ok3:
        return
    try:
        fecha = datetime.now().isoformat()
        inicializar_bd()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO mediciones (fecha, equipo, circuito, parametros) VALUES (?,?,?,?)",
            (fecha, equipo, circuito, parametros),
        )
        conn.commit()
        conn.close()
        QMessageBox.information(self, _("Información"),
                                "Medición guardada en la base de datos.")
    except Exception as exc:
        try:
            logger.exception(f"Error guardando medición: {exc}")
        except Exception:
            pass
        QMessageBox.critical(
            self, _("Error"), f"No se pudo guardar la medición:\n{exc}")


def mostrar_base_de_datos(self) -> None:
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
    try:
        inicializar_bd()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        filas = c.execute(
            "SELECT id, fecha, equipo, circuito, parametros FROM mediciones ORDER BY id DESC"
        ).fetchall()
        conn.close()
    except Exception as exc:
        try:
            QMessageBox.critical(
                self, _("Error"), f"No se pudieron leer las mediciones:\n{exc}")
        except Exception:
            pass
        return
    dlg = QDialog(self)
    dlg.setWindowTitle("Historial de mediciones")
    layout = QVBoxLayout(dlg)
    table = QTableWidget(len(filas), 5)
    table.setHorizontalHeaderLabels(
        ["ID", "Fecha", "Equipo", "Circuito", "Parámetros"])
    for i, fila in enumerate(filas):
        for j, col in enumerate(fila):
            item = QTableWidgetItem(str(col))
            table.setItem(i, j, item)
    try:
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    except Exception:
        pass
    layout.addWidget(table)
    dlg.setLayout(layout)
    dlg.exec_()


def abrir_editor_componentes(self) -> None:
    dlg = EditorComponentesDialog(self)
    dlg.exec_()


def agregar_mejoras(self) -> None:
    try:
        accion_modo_lab = QAction(traducir('Modo Laboratorio'), self)
        accion_modo_lab.setToolTip(traducir_descripcion_emergente(
            'Comparar curva simulada y medida en tiempo real'))
        accion_modo_lab.triggered.connect(
            lambda: self.abrir_modo_laboratorio())
        self.accion_modo_lab = accion_modo_lab

        accion_guardar = QAction(traducir('Guardar Medición'), self)
        accion_guardar.setToolTip(traducir_descripcion_emergente(
            'Guardar medición actual en la base de datos'))
        accion_guardar.triggered.connect(lambda: self.guardar_medicion_a_db())
        self.accion_guardar_medicion = accion_guardar

        accion_mostrar_db = QAction(traducir('Ver mediciones'), self)
        accion_mostrar_db.setToolTip(traducir_descripcion_emergente(
            'Mostrar historial de mediciones guardadas'))
        accion_mostrar_db.triggered.connect(
            lambda: self.mostrar_base_de_datos())
        self.accion_ver_mediciones = accion_mostrar_db

        if hasattr(self, 'menu_simulacion') and self.menu_simulacion is not None:
            self.menu_simulacion.addSeparator()
            self.menu_simulacion.addAction(accion_modo_lab)
            self.menu_simulacion.addAction(accion_guardar)
            self.menu_simulacion.addAction(accion_mostrar_db)
        else:
            self.menuBar().addAction(accion_modo_lab)
            self.menuBar().addAction(accion_guardar)
            self.menuBar().addAction(accion_mostrar_db)
    except Exception:
        pass
    try:
        accion_editor = QAction("Editor de Componentes", self)
        accion_editor.setToolTip(
            "Crear o editar símbolos y componentes personalizados")
        accion_editor.triggered.connect(
            lambda: self.abrir_editor_componentes())
        if hasattr(self, 'menu_herramientas') and self.menu_herramientas is not None:
            self.menu_herramientas.addSeparator()
            self.menu_herramientas.addAction(accion_editor)
        else:
            self.menuBar().addAction(accion_editor)
    except Exception:
        pass


def aplicar_a(clase=None):
    clase = clase or _base.CircuitSimulator
    for nombre in ['abrir_modo_laboratorio', 'guardar_medicion_a_db', 'mostrar_base_de_datos', 'abrir_editor_componentes', 'agregar_mejoras']:
        if nombre in globals():
            setattr(clase, nombre, globals()[nombre])
    for nombre in ['ModoLaboratorioDialog', 'TextFormatDialog', 'EditorComponentesDialog']:
        if nombre in globals():
            setattr(_base, nombre, globals()[nombre])
    return clase
