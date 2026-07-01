import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


def simular_transitorio_stub(self):
    from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
    QMessageBox.information(self, "Transitorio (próximo)",
                            "Módulo de Transitorio simple quedará activado en la siguiente iteración.")


def modelos_no_lineales(self):
    from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
    try:
        self.resolver_matriz_nodos()
        QMessageBox.information(
            self,
            "Modelos no lineales",
            "Simulación completada con modelos no lineales para diodos, BJT y MOSFET.\n"
            "Los valores mostrados consideran aproximaciones numéricas iterativas."
        )
    except Exception as exc:
        try:
            QMessageBox.warning(
                self,
                "Modelos no lineales",
                f"No se pudo completar la simulación no lineal: {exc}"
            )
        except Exception:
            pass


def iniciar_analisis_ac(self):
    from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
    try:
        self.iniciar_bode()
    except Exception as exc:
        try:
            QMessageBox.warning(self, "Análisis AC",
                                f"No se pudo iniciar el análisis AC: {exc}")
        except Exception:
            pass


def simular_transitorio(self):
    import numpy as np
    from PyQt5.QtWidgets import QInputDialog, QMessageBox
    try:
        nodo_gnd, nodos_sorted, nodo_idx = self._mapear_nodos_actual()
    except Exception as exc:
        QMessageBox.warning(self, "Simulación transitoria",
                            f"No se pudo preparar la simulación: {exc}")
        return
    try:
        params_str, ok = QInputDialog.getText(
            self, "Parámetros de simulación transitoria",
            "Ingresa dt, tmax (segundos):", text="0.001, 1.0")
        if not ok or not params_str.strip():
            return
        parts = [p.strip() for p in params_str.split(',')]
        if len(parts) >= 1:
            dt = float(parts[0])
        else:
            dt = 0.001
        if len(parts) >= 2:
            tmax = float(parts[1])
        else:
            tmax = 1.0
    except Exception:
        QMessageBox.warning(self, "Parámetros inválidos",
                            "No se pudo interpretar los parámetros ingresados.")
        return
    if dt <= 0 or tmax <= 0 or tmax <= dt:
        QMessageBox.warning(self, "Parámetros inválidos",
                            "El tiempo y el paso deben ser positivos y tmax > dt.")
        return
    try:
        sel = self.autodetectar_bode()
    except Exception:
        sel = None
    if sel is None:
        sel = self.dialogo_bode_combo()
        if sel is None:
            QMessageBox.information(self, "Simulación transitoria",
                                    "No se seleccionaron terminales; se cancela la simulación.")
            return
    tinp, tinm, toutp, toutm = sel

    def _id_nodo(term):
        return getattr(term, "node_group", None)
    n_inp, n_inm = _id_nodo(tinp), _id_nodo(tinm)
    n_outp, n_outm = _id_nodo(toutp), _id_nodo(toutm)
    elementos_res = []
    elementos_cap = []
    elementos_src_v = []
    elementos_src_i = []

    def obtener_valor(comp):
        try:
            params = getattr(comp, "parametros", [])
            val_str = params[0].split(":", 1)[1].strip()
            return interpretar_valor_prefijo(val_str)
        except Exception:
            return 1.0
    for comp in getattr(self, "componentes", []):
        tipo = getattr(comp, "tipo", "")
        nodos = []
        for t in getattr(comp, "terminales", []):
            nodos.append(getattr(t, "node_group", None))
        if len(nodos) < 2:
            continue
        val = obtener_valor(comp)
        nombre = getattr(comp, "nombre", tipo)
        if tipo in ("Resistencia", "Resistor", "Resistencia variable"):
            elementos_res.append((nodos[0], nodos[1], val, nombre))
        elif tipo in ("Capacitor", "Condensador"):
            elementos_cap.append((nodos[0], nodos[1], val, nombre))
        elif tipo in ("Fuente Voltaje", "Batería"):
            elementos_src_v.append((nodos[0], nodos[1], val, nombre))
        elif tipo in ("Fuente Corriente", ):
            elementos_src_i.append((nodos[0], nodos[1], val, nombre))
    N = len(nodos_sorted)
    M = len(elementos_src_v)
    B_total = np.zeros((N, M))
    E_total = np.zeros(M)
    for idx, (n1, n2, valor, _nom) in enumerate(elementos_src_v):
        if n1 != nodo_gnd:
            B_total[nodo_idx[n1], idx] = 1.0
        if n2 != nodo_gnd:
            B_total[nodo_idx[n2], idx] = -1.0
        E_total[idx] = valor
    G_res = np.zeros((N, N))
    for (n1, n2, Rval, _nom) in elementos_res:
        if abs(Rval) < 1e-30:
            continue
        g = 1.0 / Rval
        if n1 != nodo_gnd:
            i = nodo_idx[n1]
            G_res[i, i] += g
        if n2 != nodo_gnd:
            j = nodo_idx[n2]
            G_res[j, j] += g
        if n1 != nodo_gnd and n2 != nodo_gnd:
            i = nodo_idx[n1]
            j = nodo_idx[n2]
            G_res[i, j] -= g
            G_res[j, i] -= g
    G_cap = np.zeros((N, N))
    caps_precalc = []
    for (n1, n2, Cval, _nom) in elementos_cap:
        if abs(Cval) < 1e-30:
            continue
        Gc = Cval / dt
        caps_precalc.append((n1, n2, Gc))
        if n1 != nodo_gnd:
            i = nodo_idx[n1]
            G_cap[i, i] += Gc
        if n2 != nodo_gnd:
            j = nodo_idx[n2]
            G_cap[j, j] += Gc
        if n1 != nodo_gnd and n2 != nodo_gnd:
            i = nodo_idx[n1]
            j = nodo_idx[n2]
            G_cap[i, j] -= Gc
            G_cap[j, i] -= Gc
    G_total = G_res + G_cap
    I_const = np.zeros(N)
    for (n1, n2, Ival, _nom) in elementos_src_i:
        if n1 != nodo_gnd:
            I_const[nodo_idx[n1]] -= Ival
        if n2 != nodo_gnd:
            I_const[nodo_idx[n2]] += Ival
    V_prev = np.zeros(N)
    A_top = np.hstack((G_total, B_total)) if M > 0 else G_total
    if M > 0:
        A_bottom = np.hstack((B_total.T, np.zeros((M, M))))
        A_mat = np.vstack((A_top, A_bottom))
    else:
        A_mat = A_top
    n_steps = int(np.ceil(tmax / dt)) + 1
    t_vals = np.linspace(0.0, dt * (n_steps - 1), n_steps)
    v_out_vals = np.zeros(n_steps, dtype=float)
    z_vec = np.zeros(N + M)
    for k in range(n_steps):
        t = t_vals[k]
        I_vec = I_const.copy()
        for (n1, n2, Gc) in caps_precalc:
            v_diff_prev = 0.0
            if n1 != nodo_gnd:
                v1 = V_prev[nodo_idx[n1]]
            else:
                v1 = 0.0
            if n2 != nodo_gnd:
                v2 = V_prev[nodo_idx[n2]]
            else:
                v2 = 0.0
            v_diff_prev = v1 - v2
            I_hist = -Gc * v_diff_prev
            if n1 != nodo_gnd:
                I_vec[nodo_idx[n1]] += I_hist
            if n2 != nodo_gnd:
                I_vec[nodo_idx[n2]] -= I_hist
        if M > 0:
            z_vec[:N] = I_vec
            z_vec[N:] = E_total
        else:
            z_vec[:N] = I_vec
        try:
            x = np.linalg.solve(A_mat, z_vec)
        except Exception as ex:
            QMessageBox.critical(self, "Simulación transitoria",
                                 f"Error al resolver el sistema en t = {t:.4g}s: {ex}")
            return
        V_sol = x[:N] if M > 0 else x
        V_prev = V_sol.copy()

        def voltaje_nodo(n):
            if n is None or n == nodo_gnd:
                return 0.0
            return V_sol[nodo_idx[n]]
        v_out_vals[k] = voltaje_nodo(n_outp) - voltaje_nodo(n_outm)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t_vals, v_out_vals)
    ax.set_xlabel('Tiempo (s)')
    ax.set_ylabel('Tensión de salida (V)')
    ax.set_title('Simulación transitoria')
    ax.grid(True)
    cursor_line = {'line': None}
    annotation = fig.text(
        0.01, 0.95, '', transform=fig.transFigure, color='red', fontsize=9)

    def al_mover(event):
        if event.inaxes != ax:
            return
        t_cur = event.xdata
        if t_cur is None:
            return
        idx = int(np.argmin(np.abs(t_vals - t_cur)))
        idx = max(0, min(len(t_vals) - 1, idx))
        t_val = t_vals[idx]
        v_val = v_out_vals[idx]
        if cursor_line['line'] is not None:
            try:
                cursor_line['line'].remove()
            except Exception:
                pass
        cursor_line['line'] = ax.axvline(
            t_val, color='red', linestyle='--', alpha=0.7)
        annotation.set_text(f"t = {t_val:.5g} s | V = {v_val:.5g} V")
        fig.canvas.draw_idle()
    fig.canvas.mpl_connect('motion_notify_event', al_mover)
    plt.tight_layout()
    plt.show()


def carta_smith_interactiva(self):
    import numpy as np
    import matplotlib.pyplot as plt
    from PyQt5.QtWidgets import QInputDialog, QMessageBox
    try:
        nodo_gnd, nodos_sorted, nodo_idx = self._mapear_nodos_actual()
    except Exception as exc:
        QMessageBox.warning(self, "Carta Smith",
                            f"No se pudo preparar la simulación: {exc}")
        return
    try:
        sel = self.autodetectar_bode()
    except Exception:
        sel = None
    if sel is None:
        sel = self.dialogo_bode_combo()
        if sel is None:
            QMessageBox.information(self, "Carta Smith",
                                    "No se seleccionaron terminales; se cancela la carta Smith.")
            return
    tinp, tinm, _toutp, _toutm = sel

    def _id_nodo(term):
        return getattr(term, "node_group", None)
    n_inp, n_inm = _id_nodo(tinp), _id_nodo(tinm)
    if None in (n_inp, n_inm):
        QMessageBox.warning(self, "Carta Smith",
                            "Terminales seleccionadas no tienen nodos válidos.")
        return
    try:
        cfg = preferences.get('smith_config', None)
        if isinstance(cfg, (list, tuple)) and len(cfg) == 4:
            default_Z0, def_fmin, def_fmax, def_npts = cfg
            default_Z0 = float(default_Z0)
            def_fmin = float(def_fmin)
            def_fmax = float(def_fmax)
            def_npts = int(def_npts)
        else:
            default_Z0, def_fmin, def_fmax, def_npts = 50.0, 1e3, 1e6, 401
    except Exception:
        default_Z0, def_fmin, def_fmax, def_npts = 50.0, 1e3, 1e6, 401
    try:
        z0_str, ok = QInputDialog.getText(self, _("Impedancia característica"),
                                          _("Ingresa el valor de Z0 en ohms:"),
                                          text=str(default_Z0))
        if not ok or not z0_str or not z0_str.strip():
            return
        Z0 = float(z0_str.replace(',', '.'))
    except Exception:
        QMessageBox.warning(self, _("Carta Smith"),
                            _("Valor de Z0 no válido."))
        return
    try:
        default_rng = f"{def_fmin}, {def_fmax}, {def_npts}"
    except Exception:
        default_rng = "1e3, 1e6, 401"
    try:
        rng_str, ok2 = QInputDialog.getText(self, _("Rango de frecuencias"),
                                            _("fmin, fmax, puntos (Hz):"),
                                            text=default_rng)
        if ok2 and rng_str and rng_str.strip():
            parts = [p.strip() for p in rng_str.split(',')]
            fmin = float(parts[0]) if len(parts) >= 1 else def_fmin
            fmax = float(parts[1]) if len(parts) >= 2 else def_fmax
            npts = int(parts[2]) if len(parts) >= 3 else def_npts
        else:
            fmin, fmax, npts = def_fmin, def_fmax, def_npts
        try:
            preferences['smith_config'] = [Z0, fmin, fmax, npts]
            guardar_preferencias()
        except Exception:
            pass
    except Exception:
        QMessageBox.warning(self, _("Carta Smith"), _(
            "No se pudo interpretar el rango de frecuencias."))
        return
    if fmin <= 0 or fmax <= 0 or fmax <= fmin:
        QMessageBox.warning(self, _("Carta Smith"), _(
            "Rango de frecuencias no válido."))
        return
    elementos = []

    def obtener_valor(comp):
        try:
            params = getattr(comp, "parametros", [])
            val_str = params[0].split(":", 1)[1].strip()
            return interpretar_valor_prefijo(val_str)
        except Exception:
            return 1.0
    for comp in getattr(self, "componentes", []):
        tipo = getattr(comp, "tipo", "")
        nodos = []
        for t in getattr(comp, "terminales", []):
            nodos.append(getattr(t, "node_group", None))
        if len(nodos) < 2:
            continue
        val = obtener_valor(comp)
        if tipo in ("Resistencia", "Resistor", "Resistencia variable"):
            elementos.append(
                {"tipo": "Resistencia", "nodos": nodos[:2], "valor": val})
        elif tipo in ("Capacitor", "Condensador"):
            elementos.append(
                {"tipo": "Capacitor", "nodos": nodos[:2], "valor": val})
        elif tipo in ("Bobina", "Inductor"):
            elementos.append(
                {"tipo": "Bobina", "nodos": nodos[:2], "valor": val})
    f = np.logspace(np.log10(fmin), np.log10(fmax), int(npts))
    w = 2.0 * np.pi * f
    N = len(nodos_sorted)
    Z_in = np.zeros(len(w), dtype=complex)

    def construir_Y(omega):
        Y_mat = np.zeros((N, N), dtype=complex)

        def estampar_admitancia(n1, n2, y):
            if n1 != nodo_gnd:
                i = nodo_idx[n1]
                Y_mat[i, i] += y
            if n2 != nodo_gnd:
                j = nodo_idx[n2]
                Y_mat[j, j] += y
            if n1 != nodo_gnd and n2 != nodo_gnd:
                i = nodo_idx[n1]
                j = nodo_idx[n2]
                Y_mat[i, j] -= y
                Y_mat[j, i] -= y
        for el in elementos:
            n1, n2 = el["nodos"][0], el["nodos"][1]
            val = el["valor"]
            if el["tipo"] == "Resistencia":
                if abs(val) < 1e-30:
                    continue
                y = 1.0 / val
            elif el["tipo"] == "Capacitor":
                y = 1j * omega * val
            elif el["tipo"] == "Bobina":
                if abs(val) < 1e-30:
                    continue
                y = 1.0 / (1j * omega * val)
            else:
                continue
            estampar_admitancia(n1, n2, y)
        return Y_mat
    for idx_w, omega in enumerate(w):
        Y_mat = construir_Y(omega)
        I_vec = np.zeros(N, dtype=complex)
        if n_inp != nodo_gnd:
            I_vec[nodo_idx[n_inp]] -= 1.0
        if n_inm != nodo_gnd:
            I_vec[nodo_idx[n_inm]] += 1.0
        try:
            V = np.linalg.solve(Y_mat, I_vec)
        except Exception:
            Z_in[idx_w] = complex('inf')
            continue

        def voltaje_nodo(n):
            if n is None or n == nodo_gnd:
                return 0.0
            return V[nodo_idx[n]]
        V_port = voltaje_nodo(n_inp) - voltaje_nodo(n_inm)
        Z_in[idx_w] = V_port
    Gamma = (Z_in - Z0) / (Z_in + Z0)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title('Carta Smith')
    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color='black', linestyle='-')
    for r in [0, 0.5, 1, 2, 5, 10]:
        c = r / (1.0 + r)
        rad = 1.0 / (1.0 + r)
        x = c + rad * np.cos(theta)
        y = rad * np.sin(theta)
        ax.plot(x, y, color='lightgray', linestyle='--', linewidth=0.5)
    for x in [-5, -2, -1, -0.5, 0.5, 1, 2, 5]:
        xc = 1.0
        yc = 1.0 / x
        rad = 1.0 / abs(x)
        phi = np.linspace(0, 2 * np.pi, 400)
        xs = xc + rad * np.cos(phi)
        ys = yc + rad * np.sin(phi)
        mask = (xs**2 + ys**2) <= 1.0 + 1e-6
        ax.plot(xs[mask], ys[mask], color='lightgray',
                linestyle='--', linewidth=0.5)
    ax.plot(Gamma.real, Gamma.imag, color='blue', marker='o',
            markersize=3, linestyle='-', label='Γ(f)')
    ax.set_xlabel('Re{Γ}')
    ax.set_ylabel('Im{Γ}')
    ax.set_aspect('equal')
    ax.grid(False)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    annotation = fig.text(
        0.01, 0.95, '', transform=fig.transFigure, color='red', fontsize=9)
    marker_line = {'dot': None}

    def al_mover(event):
        if event.inaxes != ax:
            return
        xcur, ycur = event.xdata, event.ydata
        if xcur is None or ycur is None:
            return
        idx = int(np.argmin(np.abs(Gamma.real - xcur) +
                  np.abs(Gamma.imag - ycur)))
        idx = max(0, min(len(Gamma) - 1, idx))
        f_val = f[idx]
        z_val = Z_in[idx]
        g_val = Gamma[idx]
        if marker_line['dot'] is not None:
            try:
                marker_line['dot'].remove()
            except Exception:
                pass
        marker_line['dot'] = ax.plot(g_val.real, g_val.imag, marker='o', markersize=6,
                                     color='red')[0]
        annotation.set_text(
            f"f = {f_val:.4g} Hz | Z_in = {z_val.real:.3g} + j{z_val.imag:.3g} Ω"
        )
        fig.canvas.draw_idle()
    fig.canvas.mpl_connect('motion_notify_event', al_mover)
    plt.tight_layout()
    plt.show()


def aplicar_a(clase=None):
    clase = clase or _base.CircuitSimulator
    for nombre in ['simular_transitorio_stub', 'modelos_no_lineales', 'iniciar_analisis_ac', 'simular_transitorio', 'carta_smith_interactiva']:
        if nombre in globals():
            setattr(clase, nombre, globals()[nombre])
    return clase
