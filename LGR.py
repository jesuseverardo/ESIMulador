import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


def iniciar_lgr(self):
    from PyQt5.QtWidgets import QInputDialog, QMessageBox
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        import sympy as sp
        try:
            if getattr(self, 'modo_oscuro', False):
                plt.style.use('dark_background')
            else:
                plt.style.use('default')
        except Exception:
            pass
    except Exception:
        QMessageBox.warning(self, "Dependencia faltante",
                            "Necesitas 'numpy', 'matplotlib' y 'sympy' para graficar el LGR.")
        return
    try:
        import control as ct
        s = sp.Symbol('s')

        default_lgr = preferences.get(
            'lgr_function', "1/(s*(s+1)*(s**2+2*s+5))")
        func_str, ok = QInputDialog.getText(
            self,
            _("Gráfica LGR limpia"),
            _("Ingresa la función de transferencia G(s):"),
            text=str(default_lgr)
        )
        if not ok or not func_str:
            return
        try:
            preferences['lgr_function'] = func_str
            guardar_preferencias()
        except Exception:
            pass

        expr = sp.sympify(func_str.replace('^', '**'))
        num_expr, den_expr = expr.as_numer_denom()
        num = [float(c) for c in sp.Poly(num_expr, s).all_coeffs()]
        den = [float(c) for c in sp.Poly(den_expr, s).all_coeffs()]

        G = ct.tf(num, den)
        ct.root_locus(G, grid=True)
        try:
            fig = plt.gcf()
            fig.suptitle("")
        except Exception:
            pass
        plt.title(f"G(S): {func_str}")
        plt.show()
        return
    except Exception:
        pass
    default_lgr2 = preferences.get('lgr_function', "1/(s*(s+1)*(s**2+2*s+5))")
    expr, ok = QInputDialog.getText(
        self,
        _("LGR de función de transferencia"),
        _("Ingresa H(s) (usa s para la variable compleja):"),
        text=str(default_lgr2)
    )
    if not ok or not expr or not expr.strip():
        return
    try:
        preferences['lgr_function'] = expr.strip()
        guardar_preferencias()
    except Exception:
        pass
    expr_input = expr.strip()
    expr_eval = expr_input.replace('^', '**')
    import re
    expr_eval = re.sub(r'S', 's', expr_eval)
    expr_eval = re.sub(r'(\d|\))\s*(s)', r'\1*\2', expr_eval)
    expr_eval = re.sub(r'(\d|\))\s*\(', r'\1*(', expr_eval)
    expr_eval = re.sub(r'(s)\s*(\d|\()', r'\1*\2', expr_eval)
    expr_eval = re.sub(r'(\))\s*(\()', r'\1*\2', expr_eval)

    try:
        s = sp.symbols('s')
        expr_sym = sp.sympify(expr_eval, {'s': s})
    except Exception as ex:
        QMessageBox.critical(self, "Error al evaluar H(s)",
                             f"No se pudo interpretar la expresión:\n{ex}")
        return

    try:
        num, den = sp.fraction(sp.simplify(expr_sym))
        num_poly = sp.Poly(num, s)
        den_poly = sp.Poly(den, s)
        num_coeffs = [complex(coef) for coef in num_poly.all_coeffs()]
        den_coeffs = [complex(coef) for coef in den_poly.all_coeffs()]
    except Exception as ex:
        QMessageBox.critical(self, "Error al procesar H(s)",
                             f"No se pudo obtener numerador y denominador:\n{ex}")
        return
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    try:
        QApplication.setOverrideCursor(Qt.WaitCursor)
    except Exception:
        pass
    K_vals = np.logspace(-2, 3, 200)
    len_diff = len(den_coeffs) - len(num_coeffs)
    if len_diff > 0:
        num_coeffs_pad = [0] * len_diff + num_coeffs
        den_coeffs_pad = den_coeffs
    elif len_diff < 0:
        den_coeffs_pad = [0] * (-len_diff) + den_coeffs
        num_coeffs_pad = num_coeffs
    else:
        den_coeffs_pad = den_coeffs
        num_coeffs_pad = num_coeffs
    den_coeffs_pad = np.array(den_coeffs_pad, dtype=complex)
    num_coeffs_pad = np.array(num_coeffs_pad, dtype=complex)

    roots_by_k = []
    for K in K_vals:
        char_coeffs = den_coeffs_pad + K * num_coeffs_pad
        try:
            roots = np.roots(char_coeffs)
        except Exception:
            roots = []
        roots_by_k.append(roots)
    try:
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()
    except Exception:
        pass

    if not roots_by_k or len(roots_by_k[0]) == 0:
        QMessageBox.warning(
            self, "LGR", "No se pudo calcular raíces para el rango de ganancia.")
        return

    nbranches = len(roots_by_k[0])
    initial_roots = sorted(roots_by_k[0], key=lambda r: r.real)
    branches = [[r] for r in initial_roots]
    for roots in roots_by_k[1:]:
        sorted_roots = sorted(roots, key=lambda r: r.real)
        for idx in range(min(nbranches, len(sorted_roots))):
            branches[idx].append(sorted_roots[idx])

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, nbranches))
    for branch, color in zip(branches, colors):
        b_arr = np.array(branch)
        ax.plot(b_arr.real, b_arr.imag, color=color)
    try:
        poles = np.roots(den_coeffs)
    except Exception:
        poles = []
    try:
        zeros = np.roots(num_coeffs)
    except Exception:
        zeros = []
    if len(poles) > 0:
        ax.plot(np.real(poles), np.imag(poles), 'x',
                markersize=10, color='red', label='Polos')
    if len(zeros) > 0:
        ax.plot(np.real(zeros), np.imag(zeros), 'o', markersize=8,
                mfc='none', color='blue', label='Ceros')

    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.set_xlabel('Real Axis')
    ax.set_ylabel('Imaginary Axis')
    try:
        ax.set_title(f'Root Locus: {expr_input}')
    except Exception:
        ax.set_title('Root Locus')
    ax.grid(True, which='both', ls='--', alpha=0.5)
    if len(poles) + len(zeros) > 0:
        ax.legend()
    plt.tight_layout()
    plt.show()


def aplicar_a(clase=None):
    clase = clase or _base.CircuitSimulator
    setattr(clase, 'iniciar_lgr', iniciar_lgr)
    return clase
