
import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


def autodetectar_bode(self):
    nodo_gnd, nodos_sorted, nodo_idx = self._mapear_nodos_actual()

    def es_fuente_v(c):
        t = (getattr(c, "tipo", "") or "").lower()
        return ("fuente" in t and "volt" in t) or ("voltaje" in t)

    fuentes = [c for c in self.componentes if es_fuente_v(c)]
    if len(fuentes) != 1:
        return None
    fv = fuentes[0]
    if len(getattr(fv, "terminales", [])) < 2:
        return None
    tinp = fv.terminales[0]
    tinm = fv.terminales[1]

    for comp in self.componentes:
        nom = (getattr(comp, "nombre", "") or "").upper()
        if nom in ("OUT", "SALIDA") and getattr(comp, "terminales", []):
            toutp = comp.terminales[0]

            class DummyTerm:
                def __init__(self, node): self.node_group = node
            toutm = DummyTerm(nodo_gnd)
            return (tinp, tinm, toutp, toutm)

    from collections import defaultdict, deque
    grafo = defaultdict(set)

    for comp in self.componentes:
        terms = getattr(comp, "terminales", [])
        if len(terms) >= 2:
            n1 = getattr(terms[0], "node_group", None)
            n2 = getattr(terms[1], "node_group", None)
            if None not in (n1, n2) and n1 != n2:
                grafo[n1].add(n2)
                grafo[n2].add(n1)

    origen = getattr(tinp, "node_group", None)
    if origen is None:
        return None

    dist = {origen: 0}
    q = deque([origen])
    while q:
        u = q.popleft()
        for v in grafo.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)

    candidatos = [(d, n) for n, d in dist.items() if n != nodo_gnd]
    if not candidatos:
        return None
    candidatos.sort(reverse=True)
    n_out = candidatos[0][1]

    toutp = None
    for comp in self.componentes:
        for t in getattr(comp, "terminales", []):
            if getattr(t, "node_group", None) == n_out:
                toutp = t
                break
        if toutp:
            break
    if toutp is None:
        return None

    class DummyTerm:
        def __init__(self, node): self.node_group = node
    toutm = DummyTerm(nodo_gnd)

    return (tinp, tinm, toutp, toutm)


def dialogo_bode_combo(self):
    from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QComboBox

    try:
        nodo_gnd, nodos_sorted, nodo_idx = self._mapear_nodos_actual()
    except Exception as e:
        QMessageBox.warning(self, "Topología no válida", str(e))
        return None

    opciones = ["GND"] + [f"N{n}" for n in nodos_sorted]

    def crear_combo(idx0=0):
        cb = QComboBox()
        cb.addItems(opciones)
        cb.setCurrentIndex(idx0)
        return cb

    dlg = QDialog(self)
    dlg.setWindowTitle("Configurar Bode (AC)")
    lay = QFormLayout(dlg)
    c_inp = crear_combo()
    c_inm = crear_combo(0)
    c_outp = crear_combo()
    c_outm = crear_combo(0)
    lay.addRow("IN +", c_inp)
    lay.addRow("IN −", c_inm)
    lay.addRow("OUT +", c_outp)
    lay.addRow("OUT −", c_outm)

    btns = QDialogButtonBox(QDialogButtonBox.Ok |
                            QDialogButtonBox.Cancel, parent=dlg)
    lay.addWidget(btns)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)

    if dlg.exec_() != QDialog.Accepted:
        return None

    class DummyTerm:
        def __init__(self, node): self.node_group = node

    def a_terminal(txt):
        if txt == "GND":
            return DummyTerm(nodo_gnd)
        node_val = int(txt[1:])
        for comp in self.componentes:
            for t in getattr(comp, "terminales", []):
                if getattr(t, "node_group", None) == node_val:
                    return t

        dt = DummyTerm(node_val)
        return dt

    tinp = a_terminal(c_inp.currentText())
    tinm = a_terminal(c_inm.currentText())
    toutp = a_terminal(c_outp.currentText())
    toutm = a_terminal(c_outm.currentText())

    if None in (tinp, tinm, toutp, toutm):
        QMessageBox.warning(self, "Selección inválida",
                            "Alguno de los nodos seleccionados no existe en el esquema.")
        return None
    return (tinp, tinm, toutp, toutm)


def iniciar_bode(self):
    try:
        import numpy as np
        import matplotlib.pyplot as plt
    except Exception:
        QMessageBox.warning(self, "Dependencia faltante",
                            "Necesitas 'numpy' y 'matplotlib' para graficar Bode.")
        return

    sel = None
    try:
        comps_util = [c for c in getattr(self, 'componentes', []) if getattr(
            c, 'tipo', '') not in ('GND',)]
        if len(comps_util) < 2:
            self._bode_por_transferencia()
            return
    except Exception:
        pass
    try:
        sel = self.autodetectar_bode()
    except Exception:
        sel = None

    if sel is None:
        sel = self.dialogo_bode_combo()
        if sel is None:
            self._bode_por_transferencia()
            return

    tinp, tinm, toutp, toutm = sel
    self._graficar_bode(tinp, tinm, toutp, toutm)


def _mapear_nodos_actual(self):
    try:
        self.extraer_topologia()
    except Exception:
        pass

    try:
        nodo_gnd = self._nodo_gnd_actual()
    except Exception:
        nodo_gnd = None
    if nodo_gnd is None:
        raise RuntimeError("Debes colocar un GND para poder simular.")

    nodos_set = set()
    for comp in getattr(self, "componentes", []):
        for t in getattr(comp, "terminales", []):
            grp = getattr(t, "node_group", None)
            if grp is not None:
                nodos_set.add(grp)

    nodos_sorted = sorted(n for n in nodos_set if n != nodo_gnd)
    nodo_idx = {n: i for i, n in enumerate(nodos_sorted)}
    return nodo_gnd, nodos_sorted, nodo_idx


def _graficar_bode(self, tinp, tinm, toutp, toutm):
    import numpy as np
    import matplotlib.pyplot as plt
    from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication

    try:
        f, mag_db, phase_deg = simulation_core.calcular_bode(
            getattr(self, 'componentes', []), tinp, tinm, toutp, toutm
        )
    except Exception as exc:
        QMessageBox.warning(self, "Simulación AC",
                            f"No se pudo preparar la simulación: {exc}")
        return
    import matplotlib.pyplot as plt
    try:
        if getattr(self, 'modo_oscuro', False):
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
    except Exception:
        pass
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(211)
    ax1.semilogx(f, mag_db)
    ax1.set_ylabel('|H(jω)| (dB)')
    ax1.grid(True, which='both', ls='--', alpha=0.5)
    ax1.set_title('Bode: Magnitud y Fase')
    if len(mag_db) > 0:
        m_min = float(np.min(mag_db))
        m_max = float(np.max(mag_db))
        if m_min == m_max:
            margen = 1.0
            ax1.set_ylim(m_min - margen, m_max + margen)
        else:
            margen = 0.1 * (m_max - m_min)
            ax1.set_ylim(m_min - margen, m_max + margen)
    ax2 = fig.add_subplot(212)
    ax2.semilogx(f, phase_deg)
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('Fase (°)')
    ax2.grid(True, which='both', ls='--', alpha=0.5)
    if len(phase_deg) > 0:
        p_min = float(np.min(phase_deg))
        p_max = float(np.max(phase_deg))
        if p_min == p_max:
            margen = 10.0
            ax2.set_ylim(p_min - margen, p_max + margen)
        else:
            margen = 0.1 * (p_max - p_min)
            ax2.set_ylim(p_min - margen, p_max + margen)
    try:
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()
    except Exception:
        pass
    cursor_lines = {'ax1': None, 'ax2': None}
    annotation = fig.text(
        0.01, 0.95, '', transform=fig.transFigure, color='red', fontsize=9)

    def al_mover(event):
        if event.inaxes not in (ax1, ax2):
            return
        freq = event.xdata
        if freq is None:
            return
        idx = int(np.argmin(np.abs(f - freq)))
        idx = max(0, min(len(f) - 1, idx))
        freq_val = f[idx]
        mag_val = mag_db[idx]
        phase_val = phase_deg[idx]
        for key, ax in [('ax1', ax1), ('ax2', ax2)]:
            if cursor_lines[key] is not None:
                try:
                    cursor_lines[key].remove()
                except Exception:
                    pass
            cursor_lines[key] = ax.axvline(
                freq_val, color='red', linestyle='--', alpha=0.7)
        annotation.set_text(
            f"f = {freq_val:.4g} Hz | |H| = {mag_val:.2f} dB | ∠H = {phase_val:.1f}°"
        )
        fig.canvas.draw_idle()
    fig.canvas.mpl_connect('motion_notify_event', al_mover)

    plt.tight_layout()
    plt.show()


def _bode_por_transferencia(self):
    from PyQt5.QtWidgets import QInputDialog, QMessageBox
    import numpy as np
    import cmath
    import math

    expr, ok = QInputDialog.getText(
        self,
        traducir('Bode de función de transferencia'),
        traducir('Ingresa H(s) (usa s para la variable compleja):'),
        text="s(s-1)/((1+s+3s**2)(s+1))"
    )
    if not ok or not expr.strip():
        return

    expr_input = expr.strip()
    expr_eval = expr_input.replace('^', '**')
    import re
    expr_eval = re.sub(r'S', 's', expr_eval)
    expr_eval = re.sub(r'(\d|\))\s*(s)', r'\1*\2', expr_eval)
    expr_eval = re.sub(r'(\d|\))\s*\(', r'\1*(', expr_eval)
    expr_eval = re.sub(r'(s)\s*(\d|\()', r'\1*\2', expr_eval)
    expr_eval = re.sub(r'(\))\s*(\()', r'\1*\2', expr_eval)

    try:
        cfg = preferences.get('bode_config', None)
        if isinstance(cfg, (list, tuple)) and len(cfg) == 3:
            fmin, fmax, npts = float(cfg[0]), float(cfg[1]), int(cfg[2])
        else:
            fmin, fmax, npts = 1e-3, 1e4, 401
    except Exception:
        fmin, fmax, npts = 1e-3, 1e4, 401
    try:
        default_text = f"{fmin}, {fmax}, {npts}"
    except Exception:
        default_text = "0.001, 10000, 401"
    try:
        rng_str, ok2 = QInputDialog.getText(self, _("Rango de frecuencias"),
                                            _("fmin, fmax, puntos (Hz):"),
                                            text=default_text)
        if ok2 and rng_str and rng_str.strip():
            parts = [p.strip() for p in rng_str.split(',')]
            if len(parts) >= 2:
                fmin = float(parts[0])
                fmax = float(parts[1])
            if len(parts) >= 3:
                npts = int(parts[2])
            try:
                preferences['bode_config'] = [fmin, fmax, npts]
                guardar_preferencias()
            except Exception:
                pass
    except Exception:
        pass
    if fmin <= 0 or fmax <= 0 or fmax <= fmin:
        QMessageBox.warning(self, "Parámetros inválidos",
                            "Rango de frecuencias no válido.")
        return

    f = np.logspace(np.log10(fmin), np.log10(fmax), int(npts))
    w = 2*np.pi*f

    safe = {
        '__builtins__': {},
        's': 0j,
        'j': 1j,
        'pi': math.pi,
        'e': math.e,
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'exp': math.exp, 'sqrt': math.sqrt, 'log': math.log, 'abs': abs
    }
    H = np.zeros_like(w, dtype=complex)
    for i, omega in enumerate(w):
        safe['s'] = 1j*omega
        try:
            val = eval(expr_eval, safe, {})
        except Exception as ex:
            QMessageBox.critical(self, "Error al evaluar H(s)",
                                 f"No se pudo evaluar la expresión:\n{ex}")
            return
        H[i] = complex(val)

    mag_db = 20*np.log10(np.maximum(np.abs(H), 1e-20))
    phase_deg = np.angle(H, deg=True)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(211)
    ax1.semilogx(f, mag_db)
    ax1.set_ylabel('|H(jω)| (dB)')
    ax1.grid(True, which='both', ls='--', alpha=0.5)
    try:
        ax1.set_title(f'Bode: {expr_input}')
    except Exception:
        ax1.set_title('Bode')
    if len(mag_db) > 0:
        m_min = float(np.min(mag_db))
        m_max = float(np.max(mag_db))
        if m_min == m_max:
            margen = 1.0
            ax1.set_ylim(m_min - margen, m_max + margen)
        else:
            margen = 0.1 * (m_max - m_min)
            ax1.set_ylim(m_min - margen, m_max + margen)
    ax2 = fig.add_subplot(212)
    ax2.semilogx(f, phase_deg)
    ax2.set_xlabel(traducir('Frecuencia (Hz)'))
    ax2.set_ylabel(traducir('Fase (°)'))
    ax2.grid(True, which='both', ls='--', alpha=0.5)
    if len(phase_deg) > 0:
        p_min = float(np.min(phase_deg))
        p_max = float(np.max(phase_deg))
        if p_min == p_max:
            margen = 10.0
            ax2.set_ylim(p_min - margen, p_max + margen)
        else:
            margen = 0.1 * (p_max - p_min)
            ax2.set_ylim(p_min - margen, p_max + margen)
    try:
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()
    except Exception:
        pass
    plt.tight_layout()
    plt.show()


def aplicar_a(clase=None):
    clase = clase or _base.CircuitSimulator
    for nombre in [
        'autodetectar_bode', 'dialogo_bode_combo', 'iniciar_bode',
        '_mapear_nodos_actual', '_graficar_bode', '_bode_por_transferencia'
    ]:
        if nombre in globals():
            setattr(clase, nombre, globals()[nombre])
    return clase
