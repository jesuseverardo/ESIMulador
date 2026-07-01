import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


class ItemComponente(QWidget):
    def __init__(self, icono: QIcon, texto: str, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("""
            QWidget { outline: none; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.icono = QLabel(self)
        pixmap = icono.pixmap(36, 36).scaled(
            36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icono.setPixmap(pixmap)
        self.icono.setAlignment(Qt.AlignCenter)

        self.etiqueta = QLabel(texto, self)
        self.etiqueta.setTextInteractionFlags(Qt.NoTextInteraction)
        self.etiqueta.setStyleSheet("""
            font-size: 9pt;
            border: none;
            background: transparent;
        """)
        self.etiqueta.setWordWrap(True)
        self.etiqueta.setAlignment(Qt.AlignCenter)
        self.icono.setFocusPolicy(Qt.NoFocus)
        self.etiqueta.setFocusPolicy(Qt.NoFocus)
        self.setFocusPolicy(Qt.NoFocus)
        self.etiqueta.setStyleSheet("font-size: 9pt;")

        layout.addWidget(self.icono)
        layout.addWidget(self.etiqueta)


class TerminalItem(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(-4, -4, 8, 8, parent)
        self.setBrush(Qt.black)
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.conexiones = []
        self.is_logic_pin: bool = False
        self.is_logic_output: bool = False
        self.logic_value: int = 0


class Conexion:
    def __init__(self, scene, t1, t2):
        self.scene = scene
        self.t1 = t1
        self.t2 = t2
        self.is_logic: bool = bool(
            getattr(t1, 'is_logic_pin', False) and getattr(t2, 'is_logic_pin', False))
        self.lines = []
        self.crear_lineas()
        self.t1.conexiones.append(self)
        self.t2.conexiones.append(self)

    def ajustar_a_cuadricula(self, point, grid=10):
        x = round(point.x() / grid) * grid
        y = round(point.y() / grid) * grid
        return QPointF(x, y)

    def crear_lineas(self):
        if getattr(self, 'is_logic', False):
            pen = QPen(Qt.blue, 2)
        else:
            pen = QPen(Qt.black, 2)
        for _ in range(3):
            line = self.scene.addLine(0, 0, 0, 0, pen)
            line.setFlags(QGraphicsItem.ItemIsSelectable)
            self.lines.append(line)
        self.actualizar_posicion()

    def actualizar_posicion(self):
        p1 = self.ajustar_a_cuadricula(self.t1.scenePos())
        p2 = self.ajustar_a_cuadricula(self.t2.scenePos())
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        grid = 20
        margin = grid

        horizontal_preferred = abs(dx) >= abs(dy)

        def segmento_interseca_rectangulo(s: QPointF, e: QPointF, rect: QRectF) -> bool:
            if s.x() == e.x():
                x = s.x()
                y1 = min(s.y(), e.y())
                y2 = max(s.y(), e.y())
                if x >= rect.left() and x <= rect.right() and y2 >= rect.top() and y1 <= rect.bottom():
                    return True
                return False
            else:
                y = s.y()
                x1 = min(s.x(), e.x())
                x2 = max(s.x(), e.x())
                if y >= rect.top() and y <= rect.bottom() and x2 >= rect.left() and x1 <= rect.right():
                    return True
                return False

        comp1 = self.t1.parentItem()
        comp2 = self.t2.parentItem()
        try:
            rect1 = comp1.mapRectToScene(comp1.boundingRect()).boundingRect()
            rect2 = comp2.mapRectToScene(comp2.boundingRect()).boundingRect()
        except Exception:
            rect1 = QRectF()
            rect2 = QRectF()
        union_rect = rect1.united(rect2)

        if self.scene is not None:
            for item in self.scene.items():
                if hasattr(item, 'terminales') and item not in [comp1, comp2]:
                    try:
                        rect = item.mapRectToScene(
                            item.boundingRect()).boundingRect()
                    except Exception:
                        continue
                    union_rect = union_rect.united(rect)

        union_rect = union_rect.adjusted(-margin, -margin, margin, margin)

        def construir_segmentos_horizontales(mid_y: float):
            return [
                (p1, QPointF(p1.x(), mid_y)),
                (QPointF(p1.x(), mid_y), QPointF(p2.x(), mid_y)),
                (QPointF(p2.x(), mid_y), p2)
            ]

        def construir_segmentos_verticales(mid_x: float):
            return [
                (p1, QPointF(mid_x, p1.y())),
                (QPointF(mid_x, p1.y()), QPointF(mid_x, p2.y())),
                (QPointF(mid_x, p2.y()), p2)
            ]

        final_segs: List[Tuple[QPointF, QPointF]] = []

        if horizontal_preferred:
            mid_y = round(((p1.y() + p2.y()) / 2) / grid) * grid
            candidate_segs = construir_segmentos_horizontales(mid_y)
            intersects = any(segmento_interseca_rectangulo(
                s, e, union_rect) for s, e in candidate_segs)
            if not intersects:
                final_segs = candidate_segs
            else:
                above_y = round((union_rect.top() - grid) / grid) * grid
                below_y = round((union_rect.bottom() + grid) / grid) * grid
                len_above = abs(p1.y() - above_y) + \
                    abs(p2.y() - above_y) + abs(dx)
                len_below = abs(p1.y() - below_y) + \
                    abs(p2.y() - below_y) + abs(dx)
                chosen_y = above_y if len_above <= len_below else below_y
                final_segs = construir_segmentos_horizontales(chosen_y)
        else:
            mid_x = round(((p1.x() + p2.x()) / 2) / grid) * grid
            candidate_segs = construir_segmentos_verticales(mid_x)
            intersects = any(segmento_interseca_rectangulo(
                s, e, union_rect) for s, e in candidate_segs)
            if not intersects:
                final_segs = candidate_segs
            else:
                left_x = round((union_rect.left() - grid) / grid) * grid
                right_x = round((union_rect.right() + grid) / grid) * grid
                len_left = abs(p1.x() - left_x) + \
                    abs(p2.x() - left_x) + abs(dy)
                len_right = abs(p1.x() - right_x) + \
                    abs(p2.x() - right_x) + abs(dy)
                chosen_x = left_x if len_left <= len_right else right_x
                final_segs = construir_segmentos_verticales(chosen_x)

        for i in range(3):
            if i < len(final_segs):
                s, e = final_segs[i]
                self.lines[i].setLine(QLineF(s, e))
            else:
                pt = p1
                self.lines[i].setLine(QLineF(pt, pt))

    def eliminar(self):
        for line in self.lines:
            self.scene.removeItem(line)
        self.t1.conexiones.remove(self)
        self.t2.conexiones.remove(self)


class SceneConCuadricula(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_size = 20
        self.grid_pen = QPen(Qt.lightGray)
        self.grid_pen.setStyle(Qt.DotLine)

    def drawBackground(self, painter, rect):
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)

        lines = []
        x = left
        while x < rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += self.grid_size

        y = top
        while y < rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += self.grid_size

        painter.setPen(self.grid_pen)
        painter.drawLines(lines)


class ComponenteInteractivo(QGraphicsItem):
    def hoverEnterEvent(self, event):
        translated_params = []
        for param in self.parametros:
            if ":" in param:
                key, val = param.split(":", 1)
                key_translated = traducir(key.strip())
                translated_params.append(f"{key_translated}:{val}")
            else:
                translated_params.append(param)
        if len(translated_params) > 1:
            tooltip = f"<b>{self.nombre}:</b><br>" + \
                "<br>".join(translated_params)
        else:
            tooltip = f"<b>{self.nombre}:</b> " + " ".join(translated_params)
        self.setToolTip(tooltip)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setToolTip("")
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for terminal in self.terminales:
                for conn in terminal.conexiones:
                    conn.actualizar_posicion()
            try:
                self.actualizar_guias()
            except Exception:
                pass
        return super().itemChange(change, value)

    def actualizar_guias(self) -> None:
        scene = self.scene()
        if scene is None:
            return
        views = scene.views()
        if not views:
            return
        ventana = None
        try:
            ventana = views[0].window()
        except Exception:
            ventana = None
        if ventana is None or not hasattr(ventana, 'guideline_items'):
            return
        for linea in list(ventana.guideline_items):
            try:
                scene.removeItem(linea)
            except Exception:
                pass
        ventana.guideline_items = []
        rect = scene.sceneRect()
        try:
            punto = self.scenePos()
        except Exception:
            punto = self.pos()
        x = punto.x()
        y = punto.y()
        pen = QPen(Qt.blue)
        pen.setStyle(Qt.DashLine)
        linea_v = scene.addLine(x, rect.top(), x, rect.bottom(), pen)
        linea_h = scene.addLine(rect.left(), y, rect.right(), y, pen)
        ventana.guideline_items = [linea_v, linea_h]
    LOGIC_GATES = ["AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"]

    def __init__(self, pixmap, parametros, nombre, tipo, terminales=2, vertical=False, invertir=False):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.terminales = []
        self.vertical = vertical
        self.invertir = invertir
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        self.tipo = tipo
        self.parametros = parametros
        self.nombre = nombre
        if not os.path.exists(pixmap):
            print(f"[ERROR] El archivo SVG no existe: {pixmap}")
        self.svg_item = QGraphicsSvgItem(pixmap, self)

        self.svg_item.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)

        self.tooltip_texto = f"{nombre}:" + "".join(self.parametros)
        self.svg_item.setScale(1.2)

        self.nombre_label = QGraphicsTextItem(nombre, self)
        fuente = self.nombre_label.font()
        fuente.setPointSizeF(8)
        self.nombre_label.setFont(fuente)

        self.nombre_label.setDefaultTextColor(Qt.blue)

        if self.tipo == "GND":
            self.svg_item.setOpacity(0.4)
            self.nombre_label.setDefaultTextColor(Qt.darkRed)

        self.nombre_label.setVisible(True)

        self.nombre_label.setZValue(2)
        self.nombre_label.setParentItem(self)

        bounding = self.svg_item.boundingRect()
        ancho = bounding.width()
        alto = bounding.height()
        cx = ancho / 2
        cy = alto / 2

        alto_escalado = bounding.height() * self.svg_item.scale()
        if self.tipo in ["LED", "Fuente Corriente", "Fuente Voltaje", "Diodo Zener", "Batería"]:
            x = ancho + 2
            y = (alto - self.nombre_label.boundingRect().height()) / 2
        else:
            x = (ancho - self.nombre_label.boundingRect().width()) / 2
            y = alto + 5 if not self.vertical else -25
        self.nombre_label.setPos(x, y)

        if tipo == "GND":
            posiciones = [QPointF(cx, 0)]
        elif tipo in ["Push Button", "Push Button Cerrado"]:
            posiciones = [QPointF(10, alto - 5), QPointF(ancho - 10, alto - 5)]
        elif tipo in ["Transistor NPN", "Transistor PNP", "Mosfet"]:
            posiciones = [
                QPointF(0, cy),
                QPointF(ancho - 2, 0),
                QPointF(ancho - 2, alto)
            ]
        elif tipo == "OpAmp":
            posiciones = [
                QPointF(0, alto * 0.35),
                QPointF(0, alto * 0.65),
                QPointF(ancho, cy)
            ]
        elif tipo == "Potenciómetro":
            posiciones = [
                QPointF(0, cy),
                QPointF(ancho, cy),
                QPointF(cx, alto)
            ]

        elif tipo == "Generador de funciones":
            posiciones = [QPointF(ancho * 0.18, alto),
                          QPointF(ancho * 0.82, alto)]
        elif tipo in ["AND", "OR", "NAND", "NOR", "XOR"]:
            posiciones = [
                QPointF(0, alto * 0.25),
                QPointF(0, alto * 0.75),
                QPointF(ancho, cy)
            ]
        elif tipo == "NOT":
            posiciones = [
                QPointF(0, cy),
                QPointF(ancho, cy)
            ]
        elif self.vertical ^ self.invertir:
            posiciones = {
                2: [QPointF(0, cy), QPointF(ancho, cy)],
                3: [QPointF(0, cy), QPointF(cx, 0), QPointF(ancho, cy)]
            }[terminales]
        else:
            posiciones = {
                2: [QPointF(cx, 0), QPointF(cx, alto)],
                3: [QPointF(cx, 0), QPointF(cx, alto / 2), QPointF(cx, alto)]
            }.get(terminales, [])

        for pos in posiciones:
            terminal = TerminalItem(self)
            terminal.setPos(pos)
            self.terminales.append(terminal)

        try:
            if self.tipo in self.LOGIC_GATES:
                self._inicializar_compuerta_logica()
        except Exception:
            pass

        if self.tipo in self.LOGIC_GATES:
            try:
                num_inputs = max(1, len(getattr(self, 'terminales', [])) - 1)
                self.logic_input_names = [
                    chr(ord('A') + i) for i in range(num_inputs)]
                self.logic_output_name = 'Y'
            except Exception:
                self.logic_input_names = []
                self.logic_output_name = 'Y'
            try:
                self.actualizar_posiciones_etiquetas_logicas()
            except Exception:
                pass

    def actualizar_escala_terminales(self):
        componente_escala = self.scale() or 0.1
        factor_ampliacion = 1.0
        for terminal in self.terminales:
            terminal.setScale((1.0 / componente_escala) * factor_ampliacion)

    def reposicionar_terminales(self):
        bounding = self.svg_item.boundingRect()
        ancho = bounding.width() * self.svg_item.scale()
        alto = bounding.height() * self.svg_item.scale()
        cx = ancho / 2
        cy = alto / 2

        alto_escalado = bounding.height() * self.svg_item.scale()
        if self.tipo in ["LED", "Fuente Corriente", "Fuente Voltaje", "Diodo Zener", "Batería"]:
            self.nombre_label.setPos(
                ancho + 5, (alto - self.nombre_label.boundingRect().height()) / 2)
        elif not self.vertical:
            self.nombre_label.setPos(
                (ancho - self.nombre_label.boundingRect().width()) / 2, alto + 5)
        else:
            self.nombre_label.setPos(
                (ancho - self.nombre_label.boundingRect().width()) / 2, -35)

        tipo = self.tipo
        terminales = len(self.terminales)

        if tipo in ["Amperímetro", "Voltímetro", "Ohmímetro"]:
            posiciones = [
                QPointF(ancho * 0.29, alto),
                QPointF(ancho * 0.71, alto)
            ]
            for i, pos in enumerate(posiciones):
                if i < len(self.terminales):
                    self.terminales[i].setPos(pos)
                    self.terminales[i].setVisible(True)
            self.nombre_label.setPos(
                (ancho - self.nombre_label.boundingRect().width()) / 2, alto + 5)
            self.actualizar_escala_terminales()
            return

        if tipo == "GND":
            posiciones = [QPointF(cx, 0)]
        elif tipo in ["Push Button", "Push Button Cerrado"]:
            posiciones = [QPointF(10, alto - 5), QPointF(ancho - 10, alto - 5)]
        elif tipo in ["Transistor NPN", "Transistor PNP", "Mosfet"]:
            posiciones = [
                QPointF(0, cy),
                QPointF(ancho - 2, 0),
                QPointF(ancho - 2, alto)
            ]
        elif tipo == "OpAmp":
            posiciones = [
                QPointF(0, alto * 0.35),
                QPointF(0, alto * 0.65),
                QPointF(ancho, cy)
            ]
        elif tipo == "Potenciómetro":
            posiciones = [
                QPointF(0, cy),
                QPointF(ancho, cy),
                QPointF(cx, alto)
            ]
        elif tipo == "Generador de funciones":
            posiciones = [QPointF(ancho * 0.18, alto),
                          QPointF(ancho * 0.82, alto)]
        elif tipo == "Motor":
            posiciones = [QPointF(0, cy), QPointF(ancho, cy)]
        elif tipo in ["AND", "OR", "NAND", "NOR", "XOR"]:
            posiciones = [
                QPointF(0, alto * 0.25),
                QPointF(0, alto * 0.75),
                QPointF(ancho, alto * 0.5)
            ]
        elif tipo == "NOT":
            posiciones = [
                QPointF(0, alto * 0.5),
                QPointF(ancho, alto * 0.5)
            ]
        elif tipo in ["Resistencia", "Capacitor", "Bobina"]:
            posiciones = [QPointF(0, cy), QPointF(ancho, cy)]
        elif tipo == "Transformador":
            posiciones = [
                QPointF(0, alto * 0.1),
                QPointF(0, alto * 0.9),
                QPointF(ancho, alto * 0.1),
                QPointF(ancho, alto * 0.9)
            ]
            for pos in posiciones:
                terminal = TerminalItem(self)
                terminal.setPos(pos)
                self.terminales.append(terminal)
                terminal.setVisible(True)
            self.actualizar_escala_terminales()
        elif terminales == 4:
            posiciones = [
                QPointF(0, alto * 0.3), QPointF(0, alto * 0.7),
                QPointF(ancho, alto * 0.3), QPointF(ancho, alto * 0.7)
            ]
        else:
            posiciones = {
                2: [QPointF(cx, 0), QPointF(cx, alto)],
                3: [QPointF(cx, 0), QPointF(cx, alto / 2), QPointF(cx, alto)]
            }.get(terminales, [])

        for i, pos in enumerate(posiciones):
            if i < len(self.terminales):
                self.terminales[i].setPos(pos)
                self.terminales[i].setVisible(True)
        self.actualizar_escala_terminales()

        try:
            if hasattr(self, "logic_inputs"):
                self.actualizar_posiciones_etiquetas_logicas()
        except Exception:
            pass

    def _inicializar_compuerta_logica(self):
        try:
            num_inputs = max(1, len(self.terminales) - 1)
            self.logic_inputs = [0 for _ in range(num_inputs)]
            self.logic_output = 0
            self.logic_input_labels = []
            font = self.nombre_label.font() if hasattr(self, 'nombre_label') else None
            if font is not None:
                font.setPointSizeF(7)
            for idx in range(num_inputs):
                lbl = QGraphicsTextItem(self)
                lbl.logic_input_index = idx
                try:
                    lbl.setAcceptedMouseButtons(Qt.NoButton)
                except Exception:
                    pass
                if font is not None:
                    lbl.setFont(font)
                lbl.setDefaultTextColor(Qt.darkGreen)
                lbl.setZValue(3)
                try:
                    if hasattr(self, 'logic_input_names') and idx < len(self.logic_input_names):
                        var_name = self.logic_input_names[idx]
                    else:
                        var_name = chr(65 + idx)
                except Exception:
                    var_name = chr(65 + idx)
                lbl.setPlainText(f"{var_name}=0")
                self.logic_input_labels.append(lbl)
            self.output_indicator = QGraphicsEllipseItem(-4, -4, 8, 8, self)
            self.output_indicator.setBrush(Qt.red)
            self.output_indicator.setZValue(2)
            self.output_indicator.output_indicator_flag = True
            try:
                self.output_indicator.setAcceptedMouseButtons(Qt.NoButton)
            except Exception:
                pass
            self.output_label = QGraphicsTextItem(self)
            self.output_label.output_label_flag = True
            try:
                self.output_label.setAcceptedMouseButtons(Qt.NoButton)
            except Exception:
                pass
            if font is not None:
                self.output_label.setFont(font)
            self.output_label.setDefaultTextColor(Qt.darkGreen)
            self.output_label.setZValue(3)
            try:
                if hasattr(self, 'logic_output_name'):
                    out_var = self.logic_output_name
                else:
                    out_var = 'Y'
            except Exception:
                out_var = 'Y'
            self.output_label.setPlainText(f"{out_var}=0")
            for idx, term in enumerate(self.terminales):
                term.is_logic_pin = True
                term.is_logic_output = (idx == len(self.terminales) - 1)
                term.logic_value = 0
            self.actualizar_estado_logico()
            self.actualizar_posiciones_etiquetas_logicas()
        except Exception:
            pass

    def _calcular_salida(self, inputs):
        try:
            normalized = [1 if val else 0 for val in inputs]
            if not normalized:
                normalized = [0]
            t = self.tipo
            if t == "AND":
                return 1 if all(normalized) else 0
            elif t == "OR":
                return 1 if any(normalized) else 0
            elif t == "NAND":
                return 0 if all(normalized) else 1
            elif t == "NOR":
                return 0 if any(normalized) else 1
            elif t == "XOR":
                return 1 if (sum(normalized) % 2 == 1) else 0
            elif t == "XNOR":
                return 1 if (sum(normalized) % 2 == 0) else 0
            elif t == "NOT":
                return 0 if normalized[0] else 1
            else:
                return 0
        except Exception:
            return 0

    def actualizar_estado_logico(self):
        def _actualizar_compuerta(gate: 'ComponenteInteractivo', visited: Optional[set] = None) -> None:
            if visited is None:
                visited = set()
            if gate in visited:
                return
            visited.add(gate)
            try:
                gate.logic_output = gate._calcular_salida(gate.logic_inputs)
                if hasattr(gate, "output_indicator"):
                    gate.output_indicator.setBrush(
                        Qt.green if gate.logic_output else Qt.red)
                if hasattr(gate, "output_label"):
                    gate.output_label.setPlainText(f"Y={gate.logic_output}")
                if gate.terminales:
                    out_term = gate.terminales[-1]
                    out_term.logic_value = gate.logic_output
                    for conn in list(out_term.conexiones):
                        try:
                            if not getattr(conn, 'is_logic', False):
                                continue
                            other = conn.t1 if conn.t2 is out_term else conn.t2
                            if getattr(other, 'is_logic_output', False):
                                continue
                            other.logic_value = gate.logic_output
                            dest_gate = other.parentItem()
                            if isinstance(dest_gate, ComponenteInteractivo) and hasattr(dest_gate, 'logic_inputs'):
                                try:
                                    idx = dest_gate.terminales.index(other)
                                except ValueError:
                                    idx = -1
                                if idx >= 0 and idx < len(dest_gate.logic_inputs):
                                    dest_gate.logic_inputs[idx] = other.logic_value
                                    _actualizar_compuerta(dest_gate, visited)
                        except Exception:
                            continue
            except Exception:
                pass
        _actualizar_compuerta(self)

    def actualizar_posiciones_etiquetas_logicas(self):
        try:
            num_inputs = len(self.logic_inputs) if hasattr(
                self, 'logic_inputs') else 0
            for idx in range(num_inputs):
                if idx >= len(self.terminales):
                    continue
                term = self.terminales[idx]
                if idx < len(self.logic_input_labels):
                    lbl = self.logic_input_labels[idx]
                else:
                    continue
                try:
                    if hasattr(self, 'logic_input_names') and idx < len(self.logic_input_names):
                        var_name = self.logic_input_names[idx]
                    else:
                        var_name = chr(ord('A') + idx)
                except Exception:
                    var_name = chr(ord('A') + idx)
                lbl.setPlainText(f"{var_name}={self.logic_inputs[idx]}")
                pos = term.pos()
                lbl.setPos(pos.x() - 38, pos.y() - 10)
            if self.terminales:
                out_term = self.terminales[-1]
                if hasattr(self, "output_indicator"):
                    self.output_indicator.setPos(out_term.pos())
                if hasattr(self, "output_label"):
                    try:
                        out_var = self.logic_output_name if hasattr(
                            self, 'logic_output_name') else 'Y'
                    except Exception:
                        out_var = 'Y'
                    self.output_label.setPlainText(
                        f"{out_var}={self.logic_output}")
                    self.output_label.setPos(
                        out_term.pos().x() + 10, out_term.pos().y() - 10)
        except Exception:
            pass

    def establecer_nombres_logicos(self, input_names: List[str], output_name: str) -> None:
        try:
            if not hasattr(self, 'logic_inputs'):
                return
            self.logic_input_names = list(input_names) if input_names else []
            self.logic_output_name = output_name or 'Y'
            self.actualizar_posiciones_etiquetas_logicas()
        except Exception:
            pass

    def boundingRect(self):
        return self.svg_item.mapToParent(self.svg_item.boundingRect()).boundingRect()

    def paint(self, painter, option, widget):
        pass

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.tipo in self.LOGIC_GATES:
            try:
                dlg = TruthTableDialog(self)
                dlg.exec_()
            except Exception:
                pass
            return
        if event.button() == Qt.LeftButton:
            print(f"Se hizo doble clic en el componente {self.nombre}")
            views = self.scene().views()
            if not views:
                super().mouseDoubleClickEvent(event)
                return

            parent = None
            for view in views:
                for cand in [getattr(view, "window", lambda: None)(), getattr(view, "parent", lambda: None)()]:
                    if cand and hasattr(cand, "pedir_valores_componente"):
                        parent = cand
                        break
                    try:
                        tw = getattr(cand, "tab_widget", None)
                        if tw is not None:
                            cw = tw.currentWidget()
                            if cw and hasattr(cw, "pedir_valores_componente"):
                                parent = cw
                                break
                    except Exception:
                        pass
                if parent:
                    break

            if not parent:
                super().mouseDoubleClickEvent(event)
                return

            nuevas_entradas = parent.pedir_valores_componente(self.tipo)
            if nuevas_entradas:
                self.parametros = nuevas_entradas

                translated_params = []
                for param in self.parametros:
                    if ":" in param:
                        key, val = param.split(":", 1)
                        key_translated = traducir(key.strip())
                        translated_params.append(f"{key_translated}:{val}")
                    else:
                        translated_params.append(param)
                if len(translated_params) > 1:
                    nuevo_tooltip = f"<b>{self.nombre}:</b><br>" + \
                        "<br>".join(translated_params)
                else:
                    nuevo_tooltip = f"<b>{self.nombre}:</b> " + \
                        " ".join(translated_params)
                self.svg_item.setToolTip(nuevo_tooltip)
                self.update()
            else:
                print("No se ingresaron los valores.")
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setRotation((self.rotation() + 90) % 360)
            try:
                scene = self.scene()
                views = scene.views() if scene else []
                ventana = views[0].window() if views else None
                if ventana and hasattr(ventana, 'registrar_historial'):
                    ventana.registrar_historial()
            except Exception:
                pass
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            grid = 20
            pos = self.pos()
            snapped = QPointF(
                round(pos.x() / grid) * grid,
                round(pos.y() / grid) * grid
            )
            self.setPos(snapped)
        try:
            scene = self.scene()
            views = scene.views() if scene else []
            ventana = views[0].window() if views else None
            if ventana and hasattr(ventana, 'guideline_items'):
                for linea in list(ventana.guideline_items):
                    try:
                        scene.removeItem(linea)
                    except Exception:
                        pass
                ventana.guideline_items = []
        except Exception:
            pass
        try:
            scene = self.scene()
            views = scene.views() if scene else []
            ventana = views[0].window() if views else None
            if ventana and hasattr(ventana, 'registrar_historial'):
                ventana.registrar_historial()
        except Exception:
            pass
        super().mouseReleaseEvent(event)


class TruthTableDialog(QDialog):

    def __init__(self, gate: ComponenteInteractivo):
        super().__init__(gate)
        self.gate = gate
        self.setWindowTitle(f"Tabla de verdad - {gate.tipo}")
        layout = QVBoxLayout(self)
        num_inputs = len(getattr(gate, 'logic_inputs', [])) or 1
        row_count = 2 ** num_inputs
        if hasattr(gate, 'logic_input_names') and gate.logic_input_names:
            column_labels = list(gate.logic_input_names[:num_inputs])
        else:
            column_labels = [chr(ord('A') + i) for i in range(num_inputs)]
        if hasattr(gate, 'logic_output_name'):
            column_labels.append(gate.logic_output_name)
        else:
            column_labels.append("Y")
        self.table = QTableWidget(row_count, num_inputs + 1, self)
        self.table.setHorizontalHeaderLabels(column_labels)
        self.table.verticalHeader().setVisible(False)
        combinations = []
        for i in range(row_count):
            combo = []
            for bit_idx in range(num_inputs):
                combo.append((i >> bit_idx) & 1)
            combinations.append(combo)
        for row, combo in enumerate(combinations):
            for col, val in enumerate(combo):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
            out = gate._calcular_salida(combo)
            out_item = QTableWidgetItem(str(out))
            out_item.setFlags(out_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, num_inputs, out_item)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellClicked.connect(self.al_hacer_clic_en_celda)
        layout.addWidget(self.table)
        self.resaltar_estado_actual()

    def resaltar_estado_actual(self):
        try:
            num_inputs = len(getattr(self.gate, 'logic_inputs', [])) or 1
            idx = 0
            for i, val in enumerate(self.gate.logic_inputs):
                idx |= (val << (num_inputs - 1 - i))
            self.table.selectRow(idx)
            for row in range(self.table.rowCount()):
                color = Qt.yellow if row == idx else Qt.white
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        item.setBackground(color)
        except Exception:
            pass

    def al_hacer_clic_en_celda(self, row: int, column: int):
        try:
            num_inputs = len(getattr(self.gate, 'logic_inputs', [])) or 1
            new_inputs = []
            for col in range(num_inputs):
                item = self.table.item(row, col)
                new_inputs.append(int(item.text()) if item else 0)
            self.gate.logic_inputs = new_inputs
            self.gate.actualizar_estado_logico()
            self.gate.actualizar_posiciones_etiquetas_logicas()
            self.resaltar_estado_actual()
        except Exception:
            pass


class DigitalTruthTableDialog(QDialog):

    def __init__(self, rows: list[dict[str, int]], columns: list[str], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tabla de verdad")
        layout = QVBoxLayout(self)
        row_count = len(rows)
        column_count = len(columns)
        self.table = QTableWidget(row_count, column_count, self)
        self.table.setHorizontalHeaderLabels(columns)
        self.table.verticalHeader().setVisible(False)
        for r_idx, row in enumerate(rows):
            for c_idx, col_name in enumerate(columns):
                val = row.get(col_name, 0)
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r_idx, c_idx, item)
        try:
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
        except Exception:
            pass
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)


class VistaConZoom(QGraphicsView):
    def wheelEvent(self, event):
        try:
            from PyQt5.QtCore import Qt
            if event.modifiers() & Qt.ControlModifier:
                zoom_in_factor = 1.15
                zoom_out_factor = 1 / zoom_in_factor
                zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
                self.scale(zoom_factor, zoom_factor)
                return
        except Exception:
            pass
        super().wheelEvent(event)


def aplicar_a(clase=None):
    for nombre in ['ItemComponente', 'TerminalItem', 'Conexion', 'SceneConCuadricula', 'ComponenteInteractivo', 'TruthTableDialog', 'DigitalTruthTableDialog', 'VistaConZoom']:
        if nombre in globals():
            setattr(_base, nombre, globals()[nombre])
    return True
