import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


def _obtener_valor_componente(comp) -> Optional[float]:
    try:
        plist = getattr(comp, 'parametros', None)
    except Exception:
        plist = comp.get('parametros') if isinstance(comp, dict) else None
    if plist:
        try:
            for param in plist:
                if isinstance(param, str) and ':' in param:
                    _, val_str = param.split(':', 1)
                    try:
                        return interpretar_valor_prefijo(val_str.strip())
                    except Exception:
                        continue
        except Exception:
            pass
    try:
        val = getattr(comp, 'valor')
    except Exception:
        val = comp.get('valor') if isinstance(comp, dict) else None
    if isinstance(val, str):
        try:
            return interpretar_valor_prefijo(val)
        except Exception:
            pass
    try:
        return float(val) if val is not None else None
    except Exception:
        return None


def _obtener_terminales(comp) -> list:
    try:
        terms = getattr(comp, 'terminales')
    except Exception:
        terms = comp.get('terminales') if isinstance(comp, dict) else None
    if terms is None:
        try:
            nodos = comp.get('nodos')
        except Exception:
            nodos = None
        if nodos:
            class SimpleTerm:
                def __init__(self, node_group):
                    self.node_group = node_group
            return [SimpleTerm(n) for n in nodos]
    return terms or []


class SimulationAPI:

    def __init__(self, componentes: list):
        self.componentes = componentes

    def _recopilar_nodos(self):
        nodo_ids = set()
        nodo_gnd = None
        for comp in self.componentes:
            ctype = getattr(comp, 'tipo', None) or (
                comp.get('tipo') if isinstance(comp, dict) else None)
            terms = _obtener_terminales(comp)
            if ctype == 'GND':
                if terms:
                    try:
                        nodo_gnd = getattr(terms[0], 'node_group', None)
                    except Exception:
                        nodo_gnd = terms[0].get('node_group') if isinstance(
                            terms[0], dict) else None
            for t in terms:
                try:
                    node = getattr(t, 'node_group')
                except Exception:
                    node = t.get('node_group') if isinstance(t, dict) else None
                if node is not None:
                    nodo_ids.add(node)
        if nodo_gnd is None:
            if 0 in nodo_ids:
                nodo_gnd = 0
            elif nodo_ids:
                nodo_gnd = min(nodo_ids)
            else:
                nodo_gnd = 0
        nodos_sorted = sorted(n for n in nodo_ids if n != nodo_gnd)
        nodo_idx = {n: i for i, n in enumerate(nodos_sorted)}
        return nodo_gnd, nodo_idx

    def _construir_mna(self, omega: float = 0.0):
        import numpy as _np
        nodo_gnd, nodo_idx = self._recopilar_nodos()
        N = len(nodo_idx)
        resistors = []
        capacitors = []
        inductors = []
        current_srcs = []
        voltage_srcs = []
        op_amps = []
        for comp in self.componentes:
            ctype = getattr(comp, 'tipo', None) or (
                comp.get('tipo') if isinstance(comp, dict) else None)
            terms = _obtener_terminales(comp)
            nodes = []
            for t in terms:
                try:
                    node = getattr(t, 'node_group')
                except Exception:
                    node = t.get('node_group') if isinstance(t, dict) else None
                nodes.append(node)
            val = _obtener_valor_componente(comp)
            if ctype == 'Resistencia' or ctype == 'Resistor' or ctype == 'Res':
                if len(nodes) >= 2 and val not in (None, 0):
                    resistors.append((nodes[0], nodes[1], val))
            elif ctype == 'Capacitor' or ctype == 'C':
                if len(nodes) >= 2 and val is not None:
                    capacitors.append((nodes[0], nodes[1], val))
            elif ctype == 'Bobina' or ctype == 'Inductor' or ctype == 'L':
                if len(nodes) >= 2 and val is not None:
                    inductors.append((nodes[0], nodes[1], val))
            elif ctype == 'Fuente Corriente' or ctype == 'CurrentSource':
                if len(nodes) >= 2 and val is not None:
                    current_srcs.append((nodes[0], nodes[1], val))
            elif ctype in ('Fuente Voltaje', 'Batería', 'FuenteCorrienteControlada', 'VoltageSource', 'Generador de funciones'):
                if len(nodes) >= 2:
                    voltage_srcs.append(
                        (comp, nodes, val if val is not None else 0.0))
            elif ctype == 'OpAmp':
                if len(nodes) >= 3:
                    op_amps.append((comp, nodes))
        M = len(voltage_srcs)
        O = len(op_amps)
        B_total = _np.zeros((N, M + O), dtype=complex)
        E_total = _np.zeros(M, dtype=complex)
        for idx_f, (comp, nodes, v_val) in enumerate(voltage_srcs):
            n1, n2 = nodes[0], nodes[1]
            if n1 != nodo_gnd:
                B_total[nodo_idx[n1], idx_f] = 1.0
            if n2 != nodo_gnd:
                B_total[nodo_idx[n2], idx_f] = -1.0
            E_total[idx_f] = v_val
        for j, (comp, nodes) in enumerate(op_amps):
            n_out = nodes[2]
            if n_out != nodo_gnd and n_out in nodo_idx:
                B_total[nodo_idx[n_out], M + j] = 1.0

        def agregar_admitancia(mat, i1, i2, y):
            if y == 0:
                return
            if i1 != -1:
                mat[i1, i1] += y
            if i2 != -1:
                mat[i2, i2] += y
            if i1 != -1 and i2 != -1:
                mat[i1, i2] -= y
                mat[i2, i1] -= y
        G_mat = _np.zeros((N, N), dtype=complex)
        I_vec = _np.zeros(N, dtype=complex)
        for n1, n2, r_val in resistors:
            if r_val in (None, 0):
                continue
            g = 1.0 / r_val
            i1 = nodo_idx.get(n1, -1) if n1 != nodo_gnd else -1
            i2 = nodo_idx.get(n2, -1) if n2 != nodo_gnd else -1
            agregar_admitancia(G_mat, i1, i2, g)
        for n1, n2, c_val in capacitors:
            if c_val is None or c_val == 0:
                continue
            y = 1j * omega * c_val
            i1 = nodo_idx.get(n1, -1) if n1 != nodo_gnd else -1
            i2 = nodo_idx.get(n2, -1) if n2 != nodo_gnd else -1
            agregar_admitancia(G_mat, i1, i2, y)
        for n1, n2, l_val in inductors:
            if l_val is None:
                continue
            if omega == 0 or l_val == 0:
                y = 0.0
            else:
                y = 1.0 / (1j * omega * l_val)
            i1 = nodo_idx.get(n1, -1) if n1 != nodo_gnd else -1
            i2 = nodo_idx.get(n2, -1) if n2 != nodo_gnd else -1
            agregar_admitancia(G_mat, i1, i2, y)
        for n1, n2, i_val in current_srcs:
            if i_val is None:
                continue
            if n1 != nodo_gnd and n1 in nodo_idx:
                I_vec[nodo_idx[n1]] -= i_val
            if n2 != nodo_gnd and n2 in nodo_idx:
                I_vec[nodo_idx[n2]] += i_val
        dim = N + M + O
        A_mat = _np.zeros((dim, dim), dtype=complex)
        A_mat[:N, :N] = G_mat
        if M + O > 0:
            A_mat[:N, N:] = B_total
            A_mat[N:, :N] = B_total.T
        z_vec = _np.zeros(dim, dtype=complex)
        z_vec[:N] = I_vec
        if M > 0:
            z_vec[N:N + M] = E_total[:M]
        mu = 1.0e8
        for j, (comp, nodes) in enumerate(op_amps):
            row = N + M + j
            A_mat[row, :] = 0.0
            n_plus, n_minus, n_out = nodes[0], nodes[1], nodes[2]
            if n_out != nodo_gnd and n_out in nodo_idx:
                A_mat[row, nodo_idx[n_out]] = 1.0
            if n_plus != nodo_gnd and n_plus in nodo_idx:
                A_mat[row, nodo_idx[n_plus]] -= mu
            if n_minus != nodo_gnd and n_minus in nodo_idx:
                A_mat[row, nodo_idx[n_minus]] += mu
        return A_mat, z_vec, nodo_idx, nodo_gnd, M, O

    def resolver_dc(self):
        import numpy as _np
        A_mat, z_vec, nodo_idx, nodo_gnd, M, O = self._construir_mna(omega=0.0)
        try:
            x = _np.linalg.solve(A_mat, z_vec)
        except Exception:
            return {'voltages': {}, 'currents': [], 'branch_details': []}

        N = len(nodo_idx)
        V_nodes = x[:N]
        voltages = {}
        for node_id, idx in nodo_idx.items():
            voltages[node_id] = V_nodes[idx].real
        voltages[nodo_gnd] = 0.0
        currents = list(x[N:N + M + O])
        branch_details = []
        for comp in self.componentes:
            ctype = getattr(comp, 'tipo', None) or (
                comp.get('tipo') if isinstance(comp, dict) else None)
            if ctype not in ('Resistencia', 'Resistor', 'Res'):
                continue
            terms = _obtener_terminales(comp)
            if len(terms) < 2:
                continue
            n1 = getattr(terms[0], 'node_group', None) if not isinstance(
                terms[0], dict) else terms[0].get('node_group')
            n2 = getattr(terms[1], 'node_group', None) if not isinstance(
                terms[1], dict) else terms[1].get('node_group')
            val = _obtener_valor_componente(comp)
            if val in (None, 0):
                continue
            v1 = voltages.get(n1, 0.0)
            v2 = voltages.get(n2, 0.0)
            vdrop = v1 - v2
            i = vdrop / val
            branch_details.append({
                'tipo': ctype,
                'nodos': (n1, n2),
                'valor': val,
                'voltaje': vdrop,
                'corriente': i,
                'potencia': vdrop * i,
            })
        return {'voltages': voltages, 'currents': currents, 'branch_details': branch_details}

    def bode(self, tinp, tinm, toutp, toutm, fmin=1e-3, fmax=1e5, npts=401):
        # El motor de Bode heredado trabaja con objetos de la interfaz. La API
        # publica tambien acepta diccionarios (por ejemplo, las plantillas),
        # asi que los adaptamos sin modificar los datos originales.
        from types import SimpleNamespace

        componentes = []
        for comp in self.componentes:
            if not isinstance(comp, dict):
                componentes.append(comp)
                continue

            def _node_group(term):
                if isinstance(term, dict):
                    return term.get('node_group')
                return getattr(term, 'node_group', None)
            terminales = [
                SimpleNamespace(node_group=_node_group(term))
                for term in _obtener_terminales(comp)
            ]
            componentes.append(SimpleNamespace(
                tipo=comp.get('tipo'),
                valor=comp.get('valor'),
                parametros=comp.get('parametros'),
                terminales=terminales,
            ))
        return simulation_core.calcular_bode(
            componentes, tinp, tinm, toutp, toutm, fmin, fmax, npts
        )

    def tabla_verdad_digital(self) -> List[Dict[str, Dict[str, int]]]:
        model = ModelBuilder.desde_escena(self.componentes)
        LOGIC_TYPES = {"AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"}
        gates: List[_LogicGate] = []
        net_to_gate: Dict[int, _LogicGate] = {}
        for comp in model.components:
            if comp.type not in LOGIC_TYPES:
                continue
            if not comp.pins:
                continue
            input_nets = [p.net_id for p in comp.pins[:-1]]
            output_net = comp.pins[-1].net_id
            gate = _LogicGate(comp.type, input_nets, output_net)
            gates.append(gate)
            net_to_gate[output_net] = gate
        if not gates:
            return []
        used_nets = set()
        for g in gates:
            used_nets.update(g.input_nets)
            used_nets.add(g.output_net)
        input_nets: List[int] = []
        for net in used_nets:
            if net not in net_to_gate:
                net_obj = model.nets.get(net)
                if net_obj is not None and not net_obj.is_gnd:
                    input_nets.append(net)

        def red_es_entrada_de_alguna_compuerta(net_id: int) -> bool:
            for g in gates:
                if net_id in g.input_nets:
                    return True
            return False
        output_nets: List[int] = []
        for g in gates:
            if not red_es_entrada_de_alguna_compuerta(g.output_net):
                output_nets.append(g.output_net)
        input_nets = list(dict.fromkeys(sorted(input_nets)))
        output_nets = list(dict.fromkeys(sorted(output_nets)))
        input_names: Dict[int, str] = {}
        for idx, net in enumerate(input_nets):
            input_names[net] = chr(ord('A') + idx)
        output_names: Dict[int, str] = {}
        for idx, net in enumerate(output_nets):
            output_names[net] = chr(ord('Z') - idx)

        def evaluar_red(net_id: int, assignment: Dict[int, int], memo: Dict[int, int]) -> int:
            if net_id in memo:
                return memo[net_id]
            if net_id in net_to_gate:
                gate = net_to_gate[net_id]
                vals = [evaluar_red(n, assignment, memo)
                        for n in gate.input_nets]
                value = gate.calcular(vals)
                memo[net_id] = value
                return value
            return assignment.get(net_id, 0)
        table: List[Dict[str, Dict[str, int]]] = []
        num_inputs = len(input_nets)
        total_combinations = 1 << num_inputs
        for combo in range(total_combinations):
            assignment: Dict[int, int] = {}
            for bit_idx, net in enumerate(input_nets):
                assignment[net] = (combo >> bit_idx) & 1
            memo: Dict[int, int] = {}
            outputs_values: Dict[int, int] = {}
            for net in output_nets:
                outputs_values[net] = evaluar_red(net, assignment, memo)
            row = {
                'inputs': {input_names[net]: assignment[net] for net in input_nets},
                'outputs': {output_names[net]: outputs_values[net] for net in output_nets}
            }
            table.append(row)
        return table

    def tabla_verdad_digital_extendida(self) -> tuple[list[dict[str, int]], list[str]]:
        model = ModelBuilder.desde_escena(self.componentes)
        LOGIC_TYPES = {"AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"}
        gates: list[_LogicGate] = []
        net_to_gate: dict[int, _LogicGate] = {}
        for comp in model.components:
            if comp.type not in LOGIC_TYPES:
                continue
            if not comp.pins:
                continue
            input_nets = [p.net_id for p in comp.pins[:-1]]
            output_net = comp.pins[-1].net_id
            gate = _LogicGate(comp.type, input_nets, output_net)
            gates.append(gate)
            net_to_gate[output_net] = gate
        if not gates:
            self.last_net_name_map = {}
            return [], []
        used_nets: set[int] = set()
        for g in gates:
            used_nets.update(g.input_nets)
            used_nets.add(g.output_net)
        input_candidate_nets: set[int] = set()
        for net in used_nets:
            if net not in net_to_gate:
                net_obj = model.nets.get(net)
                if net_obj is not None and not net_obj.is_gnd:
                    input_candidate_nets.add(net)

        def red_es_entrada(net_id: int) -> bool:
            for g in gates:
                if net_id in g.input_nets:
                    return True
            return False
        input_nets: list[int] = []
        seen_inputs: set[int] = set()
        for comp in model.components:
            if comp.type not in {"AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"}:
                continue
            for pin in comp.pins[:-1]:
                net = pin.net_id
                if net not in net_to_gate and net not in seen_inputs and net in input_candidate_nets:
                    seen_inputs.add(net)
                    input_nets.append(net)
        for net in input_candidate_nets:
            if net not in seen_inputs:
                input_nets.append(net)
        output_nets: list[int] = []
        for g in gates:
            if not red_es_entrada(g.output_net):
                output_nets.append(g.output_net)
        intermediate_nets: list[int] = []
        for g in gates:
            net = g.output_net
            if net in output_nets:
                continue
            intermediate_nets.append(net)
        input_names: dict[int, str] = {}
        for idx, net in enumerate(input_nets):
            input_names[net] = chr(ord('A') + idx)
        intermediate_names: dict[int, str] = {}
        next_letter_code = ord('A') + len(input_nets)
        seen_intermediate: set[int] = set()
        for comp in model.components:
            if comp.type not in {"AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"}:
                continue
            if not comp.pins:
                continue
            net = comp.pins[-1].net_id
            if net in intermediate_nets and net not in seen_intermediate:
                intermediate_names[net] = chr(next_letter_code)
                next_letter_code += 1
                seen_intermediate.add(net)
        output_names: dict[int, str] = {}
        seen_outputs: set[int] = set()
        ordered_outputs: list[int] = []
        for comp in model.components:
            if comp.type not in {"AND", "OR", "NAND", "NOR", "XOR", "XNOR", "NOT"}:
                continue
            if not comp.pins:
                continue
            net = comp.pins[-1].net_id
            if net in output_nets and net not in seen_outputs:
                seen_outputs.add(net)
                ordered_outputs.append(net)
        for net in output_nets:
            if net not in seen_outputs:
                ordered_outputs.append(net)
        output_nets = ordered_outputs
        for idx, net in enumerate(output_nets):
            output_names[net] = chr(ord('Z') - idx)
        net_name_map: dict[int, str] = {}
        net_name_map.update(input_names)
        net_name_map.update(intermediate_names)
        net_name_map.update(output_names)
        self.last_net_name_map = net_name_map
        currently_eval: set[int] = set()

        def evaluar_red(net_id: int, assignment: dict[int, int], memo: dict[int, int]) -> int:
            if net_id in memo:
                return memo[net_id]
            if net_id in currently_eval:
                memo[net_id] = 0
                return 0
            if net_id in net_to_gate:
                gate = net_to_gate[net_id]
                currently_eval.add(net_id)
                vals = [evaluar_red(n, assignment, memo)
                        for n in gate.input_nets]
                currently_eval.discard(net_id)
                value = gate.calcular(vals)
                memo[net_id] = value
                return value
            return assignment.get(net_id, 0)
        num_inputs = len(input_nets)
        total_combinations = 1 << num_inputs
        rows: list[dict[str, int]] = []
        column_order: list[str] = []
        for net in input_nets:
            column_order.append(input_names[net])
        for net in intermediate_nets:
            if net in intermediate_names:
                column_order.append(intermediate_names[net])
        for net in output_nets:
            column_order.append(output_names[net])
        for combo in range(total_combinations):
            assignment: dict[int, int] = {}
            for bit_idx, net in enumerate(input_nets):
                assignment[net] = (combo >> bit_idx) & 1
            memo: dict[int, int] = {}
            row: dict[str, int] = {}
            for net in input_nets:
                name = input_names[net]
                row[name] = assignment[net]
            for g in gates:
                net = g.output_net
                if net in intermediate_names:
                    val = evaluar_red(net, assignment, memo)
                    name = intermediate_names[net]
                    row[name] = val
            for net in output_nets:
                val = evaluar_red(net, assignment, memo)
                name = output_names[net]
                row[name] = val
            rows.append(row)
        return rows, column_order

    def funciones_booleanas_digitales(self) -> Dict[str, str]:

        try:
            table = self.tabla_verdad_digital()
        except Exception:
            return {}
        if not table:
            return {}
        first_row = table[0]
        input_vars = list(first_row.get('inputs', {}).keys())
        output_vars = list(first_row.get('outputs', {}).keys())
        functions: Dict[str, str] = {}
        for out in output_vars:
            terms: List[str] = []
            all_zero = True
            for row in table:
                out_val = row['outputs'].get(out, 0)
                if out_val == 1:
                    all_zero = False
                    term_parts: List[str] = []
                    for var in input_vars:
                        val = row['inputs'].get(var, 0)
                        if val:
                            term_parts.append(var)
                        else:
                            term_parts.append(f"{var}'")
                    term = ''.join(term_parts) if term_parts else '1'
                    terms.append(term)
            if not terms:
                if all_zero:
                    expr = '0'
                else:
                    expr = '0'
            else:
                if len(terms) == (1 << len(input_vars)):
                    expr = '1'
                else:
                    expr = ' + '.join(terms)
            functions[out] = expr

    def expresiones_booleanas_digitales(self) -> Dict[str, Dict[str, str]]:
        try:
            table = self.tabla_verdad_digital()
        except Exception:
            return {}
        if not table:
            return {}
        first_row = table[0]
        input_vars = list(first_row.get('inputs', {}).keys())
        output_vars = list(first_row.get('outputs', {}).keys())
        try:
            import sympy
        except Exception:
            sympy = None
        result: Dict[str, Dict[str, str]] = {}
        for out in output_vars:
            terms: List[str] = []
            minterms: List[List[int]] = []
            all_zero = True
            for row in table:
                out_val = row['outputs'].get(out, 0)
                if out_val == 1:
                    all_zero = False
                    term_parts: List[str] = []
                    mt: List[int] = []
                    for var in input_vars:
                        val = row['inputs'].get(var, 0)
                        mt.append(val)
                        if val:
                            term_parts.append(var)
                        else:
                            term_parts.append(f"{var}'")
                    term = ''.join(term_parts) if term_parts else '1'
                    terms.append(term)
                    minterms.append(mt)
            if not terms:
                if all_zero:
                    canonical_expr = '0'
                else:
                    canonical_expr = '0'
            else:
                if len(terms) == (1 << len(input_vars)):
                    canonical_expr = '1'
                else:
                    canonical_expr = ' + '.join(terms)
            simplified_expr: str
            if sympy is None or len(input_vars) == 0:
                simplified_expr = canonical_expr
            else:
                try:
                    symbols = sympy.symbols(' '.join(input_vars))
                    if not isinstance(symbols, (tuple, list)):
                        symbols = (symbols,)
                    if not minterms:
                        simplified_expr = '0'
                    elif len(minterms) == (1 << len(input_vars)):
                        simplified_expr = '1'
                    else:
                        sop_expr = sympy.SOPform(list(symbols), minterms)
                        try:
                            simple_expr = sympy.simplify_logic(
                                sop_expr, form='dnf')
                        except Exception:
                            simple_expr = sop_expr

                        def expresion_a_texto(expr) -> str:
                            if expr == sympy.true:
                                return '1'
                            if expr == sympy.false:
                                return '0'
                            if isinstance(expr, sympy.Symbol):
                                return str(expr)
                            from sympy.logic.boolalg import Not, And, Or
                            if expr.func == Not:
                                return f"{expresion_a_texto(expr.args[0])}'"
                            if expr.func == And:
                                parts: List[str] = []
                                for arg in expr.args:
                                    if arg.func == Or:
                                        parts.append(
                                            f"({expresion_a_texto(arg)})")
                                    else:
                                        parts.append(expresion_a_texto(arg))
                                return ''.join(parts)
                            if expr.func == Or:
                                parts = [expresion_a_texto(
                                    arg) for arg in expr.args]
                                return ' + '.join(parts)
                            return str(expr)
                        simplified_expr = expresion_a_texto(simple_expr)
                except Exception:
                    simplified_expr = canonical_expr
            result[out] = {'canonical': canonical_expr,
                           'simplified': simplified_expr}
        return result
        return functions


class _LogicGate:
    def __init__(self, gate_type: str, input_nets: List[int], output_net: int) -> None:
        self.gate_type: str = (gate_type or '').upper()
        self.input_nets: List[int] = list(input_nets or [])
        self.output_net: int = output_net

    def calcular(self, inputs: List[int]) -> int:
        normalized = [1 if val else 0 for val in inputs]
        if not normalized:
            normalized = [0]
        t = self.gate_type
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


TEMPLATES = {
    'divisor_resistivo': {
        'descripcion': 'Divisor resistivo simple: dos resistencias en serie conectadas a una fuente de voltaje.',
        'componentes': [
            {'tipo': 'Fuente Voltaje', 'valor': 10.0, 'nodos': (1, 0)},
            {'tipo': 'Resistencia', 'valor': 1000.0, 'nodos': (1, 2)},
            {'tipo': 'Resistencia', 'valor': 1000.0, 'nodos': (2, 0)},
        ],
        'parametros_sugeridos': {
            'frecuencia_bode': {'fmin': 10, 'fmax': 10000, 'npts': 100},
        },
        'medidas': {
            'voltaje_nodo2_medido': None,
            'corriente_fuente_medido': None,
        },
    },
    'filtro_rc': {
        'descripcion': 'Filtro RC paso bajo: una resistencia en serie seguida de un capacitor a tierra.',
        'componentes': [
            {'tipo': 'Fuente Voltaje', 'valor': 1.0, 'nodos': (1, 0)},
            {'tipo': 'Resistencia', 'valor': 1000.0, 'nodos': (1, 2)},
            {'tipo': 'Capacitor', 'valor': 1e-6, 'nodos': (2, 0)},
        ],
        'parametros_sugeridos': {
            'frecuencia_bode': {'fmin': 1, 'fmax': 100000, 'npts': 1000},
        },
        'medidas': {
            'frecuencia_corte_medido': None,
            'ganancia_db_1khz_medido': None,
        },
    },
}


def obtener_plantilla(name: str) -> dict:
    tpl = TEMPLATES.get(name)
    if tpl is None:
        raise KeyError(f"Template '{name}' not found")
    return deepcopy(tpl)


def _casi_iguales(a: float, b: float, tol: float = 1e-2) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(b))


def ejecutar_pruebas_internas(verbose: bool = True) -> bool:
    success = True
    messages = []
    tpl = obtener_plantilla('divisor_resistivo')
    api = SimulationAPI(tpl['componentes'])
    dc = api.resolver_dc()
    v = dc['voltages'].get(2, None)
    if v is None or not _casi_iguales(v, 5.0, 1e-2):
        success = False
        messages.append(
            f"Resistive divider: expected 5.0 V at node 2, got {v}")
    tpl2 = obtener_plantilla('filtro_rc')
    api2 = SimulationAPI(tpl2['componentes'])

    class FakeTerm:
        def __init__(self, node_group):
            self.node_group = node_group
    tinp = FakeTerm(1)
    tinm = FakeTerm(0)
    toutp = FakeTerm(2)
    toutm = FakeTerm(0)
    f, mag_db, phase_deg = api2.bode(tinp, tinm, toutp, toutm, 10, 200000, 200)
    import numpy as _np
    theoretical_fc = 1.0 / (2.0 * 3.141592653589793 * 1000.0 * 1e-6)
    idx = _np.argmin(_np.abs(_np.array(f) - theoretical_fc))
    db_at_fc = mag_db[idx]
    if not _casi_iguales(db_at_fc, -3.0, 0.5):
        success = False
        messages.append(
            f"RC filter: expected ≈ -3 dB at fc, got {db_at_fc:.2f} dB at {f[idx]:.2f} Hz")
    if verbose:
        if success:
            print("All internal tests passed.")
        else:
            print("Some internal tests failed:")
            for msg in messages:
                print("  -", msg)
    return success


def ejecutar_cli(args=None):
    import argparse
    import json
    parser = argparse.ArgumentParser(
        description="Circuit simulator CLI", prog="Prueba5.py")
    parser.add_argument(
        'command', nargs='?', help='Subcommand to run (list-templates, show-template, simulate, run-tests)')
    parser.add_argument('argument', nargs='?',
                        help='Argument for the subcommand (template name or file name)')
    parser.add_argument('--no-verbose', action='store_true',
                        help='Silence test output when running tests')
    parsed = parser.parse_args(args)
    cmd = parsed.command
    if cmd is None:
        parser.print_help()
        return 0
    if cmd == 'list-templates':
        print("Available templates:")
        for name, tpl in TEMPLATES.items():
            print(f"  - {name}: {tpl['descripcion']}")
    elif cmd == 'show-template':
        if not parsed.argument:
            print("Please specify a template name.")
            return 1
        name = parsed.argument
        try:
            tpl = obtener_plantilla(name)
        except KeyError:
            print(f"Template '{name}' not found.")
            return 1
        print(f"Template '{name}':")
        print(json.dumps(tpl, indent=4, ensure_ascii=False))
    elif cmd == 'simulate':
        if not parsed.argument:
            print("Please specify a JSON file containing the circuit description.")
            return 1
        fname = parsed.argument
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                comp_list = json.load(f)
        except Exception as exc:
            print(f"Error loading '{fname}': {exc}")
            return 1
        comps = []
        for comp in comp_list:
            if 'terminales' not in comp and 'nodos' in comp:
                comp = dict(comp)
                comp['terminales'] = [{'node_group': n} for n in comp['nodos']]
            comps.append(comp)
        api = SimulationAPI(comps)
        dc = api.resolver_dc()
        print("DC voltages (V):")
        for node_id, v in sorted(dc['voltages'].items()):
            print(f"  Node {node_id}: {v:.6g}")
        print("\nResistor details:")
        for detail in dc['branch_details']:
            n1, n2 = detail['nodos']
            print(
                f"  {detail['tipo']} between {n1}-{n2}: V={detail['voltaje']:.6g} V, I={detail['corriente']:.6g} A, P={detail['potencia']:.6g} W")
        return 0
    elif cmd == 'run-tests':
        ok = ejecutar_pruebas_internas(verbose=not parsed.no_verbose)
        return 0 if ok else 1
    else:
        print(f"Unknown command '{cmd}'.")
        parser.print_help()
        return 1


def aplicar_a(clase=None):
    _base.SimulationAPI = SimulationAPI
    _base._LogicGate = _LogicGate
    _base.ejecutar_pruebas_internas = ejecutar_pruebas_internas
    _base.ejecutar_cli = ejecutar_cli
    return SimulationAPI
