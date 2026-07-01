import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


def interpretar_valor_prefijo(cadena):
    prefijos = {
        'p': 1e-12,
        'n': 1e-9,
        'μ': 1e-6,
        'u': 1e-6,
        'm': 1e-3,
        '': 1,
        'k': 1e3,
        'K': 1e3,
        'M': 1e6,
        'G': 1e9
    }

    import re
    match = re.match(r"([0-9.,]+)\s*([pnumkKMGμ]*)", cadena.strip())
    if not match:
        raise ValueError("Formato no reconocido")

    numero, prefijo = match.groups()
    numero = float(numero.replace(",", "."))
    factor = prefijos.get(prefijo, 1)
    return numero * factor


def formatear_valor_con_prefijo(valor):
    unidades = [
        ("GV", 1e9), ("MV", 1e6), ("kV", 1e3), ("V", 1),
        ("mV", 1e-3), ("µV", 1e-6), ("nV", 1e-9), ("pV", 1e-12)
    ]
    for sufijo, factor in unidades:
        if abs(valor) >= factor:
            return f"{valor / factor:.4f} {sufijo}"
    return f"{valor:.4f} V"


def formatear_resistencia_con_prefijo(valor):
    unidades = [("GΩ", 1e9), ("MΩ", 1e6), ("kΩ", 1e3), ("Ω", 1),
                ("mΩ", 1e-3), ("µΩ", 1e-6), ("nΩ", 1e-9), ("pΩ", 1e-12)]
    for sufijo, factor in unidades:
        if abs(valor) >= factor:
            return f"{valor / factor:.4f} {sufijo}"
    return f"{valor:.4f} Ω"


class ResistenciasCalculatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(traducir('Calculadora de resistencias'))
        self.setModal(True)
        if CURRENT_LANGUAGE == 'en':
            self.digit_colors = [
                "Black", "Brown", "Red", "Orange", "Yellow",
                "Green", "Blue", "Violet", "Gray", "White"
            ]
            self.digit_map = {color: i for i,
                              color in enumerate(self.digit_colors)}
            self.multiplier_colors = [
                "Black", "Brown", "Red", "Orange", "Yellow",
                "Green", "Blue", "Violet", "Gray", "White",
                "Gold", "Silver"
            ]
            self.multiplier_map = {
                "Black": 1,
                "Brown": 10,
                "Red": 100,
                "Orange": 1_000,
                "Yellow": 10_000,
                "Green": 100_000,
                "Blue": 1_000_000,
                "Violet": 10_000_000,
                "Gray": 100_000_000,
                "White": 1_000_000_000,
                "Gold": 0.1,
                "Silver": 0.01
            }
            self.tolerance_colors = [
                "Brown", "Red", "Green", "Blue", "Violet",
                "Gray", "Gold", "Silver"
            ]
            self.tolerance_map = {
                "Brown": 0.01,
                "Red": 0.02,
                "Green": 0.005,
                "Blue": 0.0025,
                "Violet": 0.001,
                "Gray": 0.0005,
                "Gold": 0.05,
                "Silver": 0.10
            }
            self.ppm_colors = [
                "Brown", "Red", "Orange", "Yellow", "Green",
                "Blue", "Violet", "Gray"
            ]
            self.ppm_map = {
                "Brown": 100,
                "Red": 50,
                "Orange": 15,
                "Yellow": 25,
                "Green": 20,
                "Blue": 10,
                "Violet": 5,
                "Gray": 1
            }
        else:
            self.digit_colors = [
                "Negro", "Marrón", "Rojo", "Naranja", "Amarillo",
                "Verde", "Azul", "Violeta", "Gris", "Blanco"
            ]
            self.digit_map = {color: i for i,
                              color in enumerate(self.digit_colors)}
            self.multiplier_colors = [
                "Negro", "Marrón", "Rojo", "Naranja", "Amarillo",
                "Verde", "Azul", "Violeta", "Gris", "Blanco",
                "Dorado", "Plateado"
            ]
            self.multiplier_map = {
                "Negro": 1,
                "Marrón": 10,
                "Rojo": 100,
                "Naranja": 1_000,
                "Amarillo": 10_000,
                "Verde": 100_000,
                "Azul": 1_000_000,
                "Violeta": 10_000_000,
                "Gris": 100_000_000,
                "Blanco": 1_000_000_000,
                "Dorado": 0.1,
                "Plateado": 0.01
            }
            self.tolerance_colors = [
                "Marrón", "Rojo", "Verde", "Azul", "Violeta",
                "Gris", "Dorado", "Plateado"
            ]
            self.tolerance_map = {
                "Marrón": 0.01,
                "Rojo": 0.02,
                "Verde": 0.005,
                "Azul": 0.0025,
                "Violeta": 0.001,
                "Gris": 0.0005,
                "Dorado": 0.05,
                "Plateado": 0.10
            }
            self.ppm_colors = [
                "Marrón", "Rojo", "Naranja", "Amarillo", "Verde",
                "Azul", "Violeta", "Gris"
            ]
            self.ppm_map = {
                "Marrón": 100,
                "Rojo": 50,
                "Naranja": 15,
                "Amarillo": 25,
                "Verde": 20,
                "Azul": 10,
                "Violeta": 5,
                "Gris": 1
            }
        main_layout = QVBoxLayout(self)

        bands_layout = QHBoxLayout()
        bands_label = QLabel(traducir('Cantidad de bandas:'))
        self.bands_combo = QComboBox()
        self.bands_combo.addItems(
            [traducir('4 bandas'), traducir('5 bandas'), traducir('6 bandas')])
        self.bands_combo.currentIndexChanged.connect(self._actualizar_campos)
        bands_layout.addWidget(bands_label)
        bands_layout.addWidget(self.bands_combo)
        bands_layout.addStretch()
        main_layout.addLayout(bands_layout)

        self.fields_layout = QFormLayout()
        main_layout.addLayout(self.fields_layout)

        self.result_label = QLabel("")
        main_layout.addWidget(self.result_label)

        buttons_layout = QHBoxLayout()
        self.calc_button = QPushButton(traducir('Calcular'))
        self.calc_button.clicked.connect(self._calcular)
        self.clear_button = QPushButton(traducir('Limpiar'))
        self.clear_button.clicked.connect(self._limpiar_seleccion)
        buttons_layout.addWidget(self.calc_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        self._actualizar_campos()

    def _limpiar_disposicion(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _actualizar_campos(self):
        self._limpiar_disposicion(self.fields_layout)
        self.band_combos = []
        nbands = 4 + self.bands_combo.currentIndex()
        num_digit_bands = 2 if nbands == 4 else 3
        for i in range(num_digit_bands):
            combo = QComboBox()
            combo.addItems(self.digit_colors)
            self.band_combos.append(combo)
            label_text = traducir(f"{i+1}.ª banda de color")
            self.fields_layout.addRow(label_text, combo)
        self.multiplier_combo = QComboBox()
        self.multiplier_combo.addItems(self.multiplier_colors)
        self.fields_layout.addRow(
            traducir('Multiplicador'), self.multiplier_combo)
        self.tolerance_combo = QComboBox()
        self.tolerance_combo.addItems(self.tolerance_colors)
        self.fields_layout.addRow(traducir('Tolerancia'), self.tolerance_combo)
        if nbands == 6:
            self.ppm_combo = QComboBox()
            self.ppm_combo.addItems(self.ppm_colors)
            self.fields_layout.addRow(traducir('ppm'), self.ppm_combo)
        else:
            self.ppm_combo = None
        self.result_label.setText("")

    def _limpiar_seleccion(self):
        for combo in getattr(self, 'band_combos', []):
            combo.setCurrentIndex(0)
        if hasattr(self, 'multiplier_combo') and self.multiplier_combo:
            self.multiplier_combo.setCurrentIndex(0)
        if hasattr(self, 'tolerance_combo') and self.tolerance_combo:
            self.tolerance_combo.setCurrentIndex(0)
        if hasattr(self, 'ppm_combo') and self.ppm_combo:
            self.ppm_combo.setCurrentIndex(0)
        self.result_label.setText("")

    def _calcular(self):
        try:
            nbands = 4 + self.bands_combo.currentIndex()
            digits = [self.digit_map[combo.currentText()]
                      for combo in self.band_combos]
            if nbands == 4:
                base = digits[0] * 10 + digits[1]
            else:
                base = digits[0] * 100 + digits[1] * 10 + digits[2]
            multiplier_value = self.multiplier_map[self.multiplier_combo.currentText(
            )]
            resistance_value = base * multiplier_value
            tolerance_value = self.tolerance_map[self.tolerance_combo.currentText(
            )]
            valor_str = formatear_resistencia_con_prefijo(resistance_value)
            if CURRENT_LANGUAGE == 'en':
                result_text = f"{traducir('Valor nominal')}: {valor_str}\n{traducir('Tolerancia')}: \u00b1{tolerance_value*100:.2f}%"
                if nbands == 6 and self.ppm_combo is not None:
                    ppm_value = self.ppm_map[self.ppm_combo.currentText()]
                    result_text += f"\n{traducir('Confiabilidad')}: {ppm_value} ppm/K"
            else:
                result_text = f"Valor nominal: {valor_str}\nTolerancia: \u00b1{tolerance_value*100:.2f}%"
                if nbands == 6 and self.ppm_combo is not None:
                    ppm_value = self.ppm_map[self.ppm_combo.currentText()]
                    result_text += f"\nConfiabilidad: {ppm_value}\u00a0ppm/K"
            self.result_label.setText(result_text)
        except Exception as exc:
            try:
                mostrar_error(self, "calcular resistencia", exc)
            except Exception:
                pass
            self.result_label.setText(f"Error al calcular: {exc}")


def aplicar_a(clase=None):
    _base.ResistenciasCalculatorDialog = ResistenciasCalculatorDialog
    _base.interpretar_valor_prefijo = interpretar_valor_prefijo
    _base.formatear_resistencia_con_prefijo = formatear_resistencia_con_prefijo
    return ResistenciasCalculatorDialog
