import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


class EsimulatorCore:
    @staticmethod
    def construir_modelo(componentes_scene: List[Any]) -> "CircuitModel":
        return ModelBuilder.desde_escena(componentes_scene)

    @staticmethod
    def ejecutar_comprobaciones(model: "CircuitModel") -> List["Issue"]:
        checker = EarlyElectricalChecks(model)
        return checker.ejecutar_todo()


class Pin:
    comp_name: str
    comp_type: str
    index: int
    net_id: int

    def clave(self) -> Tuple[str, int]:
        return (self.comp_name, self.index)


class Net:
    id: int
    pins: List[Pin] = field(default_factory=list)
    is_gnd: bool = False


class Component:
    name: str
    type: str
    pins: List[Pin] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)


class CircuitModel:
    components: List[Component]
    nets: Dict[int, Net]

    def encontrar_componente(self, name: str) -> Optional[Component]:
        for c in self.components:
            if c.name == name:
                return c
        return None


class ModelBuilder:
    @staticmethod
    def desde_escena(componentes_scene: List[Any]) -> CircuitModel:
        nets: Dict[int, Net] = {}
        comps: List[Component] = []
        for comp in componentes_scene:
            nombre = getattr(comp, "nombre", "Comp")
            tipo = getattr(comp, "tipo", "Desconocido")
            params_list = list(getattr(comp, "parametros", []))
            params: Dict[str, str] = {}
            for p in params_list:
                if ":" in p:
                    k, v = p.split(":", 1)
                    params[k.strip()] = v.strip()
            pins: List[Pin] = []
            for idx, term in enumerate(getattr(comp, "terminales", [])):
                net_id = getattr(term, "node_group", None)
                if net_id is None:
                    net_id = -100000 - len(pins)
                pin = Pin(nombre, tipo, idx, net_id)
                pins.append(pin)
                if net_id not in nets:
                    nets[net_id] = Net(id=net_id, pins=[], is_gnd=False)
            component = Component(nombre, tipo, pins, params)
            comps.append(component)
            for p in pins:
                nets[p.net_id].pins.append(p)
        for comp in comps:
            if comp.type == "GND" and comp.pins:
                nid = comp.pins[0].net_id
                if nid in nets:
                    nets[nid].is_gnd = True
        return CircuitModel(components=comps, nets=nets)


class Issue:
    level: str
    code: str
    msg: str
    details: str = ""


class EarlyElectricalChecks:
    VOLTAGE_NAMES = {"Fuente Voltaje", "Batería", "Generador de funciones"}
    CURRENT_NAMES = {"Fuente Corriente"}

    def __init__(self, model: CircuitModel):
        self.m = model

    def ejecutar_todo(self) -> List[Issue]:
        issues: List[Issue] = []
        issues += self._comprobar_presencia_gnd()
        issues += self._comprobar_nodos_flotantes()
        issues += self._comprobar_cortos_en_componentes()
        issues += self._comprobar_fuentes_voltaje_en_conflicto()
        issues += self._comprobar_fuente_en_cortocircuito()
        issues += self._comprobar_gnd_duplicado()
        issues += self._comprobar_subredes_desconectadas()
        issues += self._comprobar_fuentes_voltaje_opuestas()
        return issues

    def _comprobar_gnd_duplicado(self) -> List[Issue]:
        gnd_nets = [net.id for net in self.m.nets.values() if net.is_gnd]
        if not gnd_nets or len(set(gnd_nets)) <= 1:
            return []
        detalles = f"IDs de tierras detectadas: {', '.join(str(n) for n in sorted(set(gnd_nets)))}"
        return [Issue("warning", "MULTI_GND",
                      "Se detectaron múltiples nodos de tierra (GND). Verifica que sólo exista una referencia común.",
                      detalles)]

    def _comprobar_subredes_desconectadas(self) -> List[Issue]:
        adjacency: Dict[int, set] = {}
        for comp in self.m.components:
            nets = [p.net_id for p in comp.pins]
            for n in nets:
                adjacency.setdefault(n, set())
            for i in range(len(nets)):
                for j in range(i + 1, len(nets)):
                    n1, n2 = nets[i], nets[j]
                    adjacency[n1].add(n2)
                    adjacency[n2].add(n1)
        if not adjacency:
            return []
        visited = set()
        subnets = 0
        for net_id in adjacency.keys():
            if net_id in visited:
                continue
            subnets += 1
            stack = [net_id]
            while stack:
                curr = stack.pop()
                if curr in visited:
                    continue
                visited.add(curr)
                for neigh in adjacency.get(curr, set()):
                    if neigh not in visited:
                        stack.append(neigh)
        if subnets > 1:
            return [Issue("warning", "DISCONNECTED",
                          f"Se encontraron {subnets} subredes eléctricas desconectadas. Algunos componentes no interactúan entre sí.")]
        return []

    def _comprobar_fuentes_voltaje_opuestas(self) -> List[Issue]:
        out: List[Issue] = []
        pair_map: Dict[Tuple[int, int], List[Tuple[int, int, str]]] = {}
        for c in self.m.components:
            if c.type in self.VOLTAGE_NAMES and len(c.pins) >= 2:
                a = c.pins[0].net_id
                b = c.pins[1].net_id
                key = tuple(sorted((a, b)))
                pair_map.setdefault(key, []).append((a, b, c.name))
        for key, lst in pair_map.items():
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    a1, b1, name1 = lst[i]
                    a2, b2, name2 = lst[j]
                    if a1 == b2 and b1 == a2:
                        out.append(Issue("warning", "OPPOSING_VSRC",
                                         f"Fuentes de voltaje enfrentadas entre nodos {key}: {name1} y {name2}.",))
                        break
        return out

    def _comprobar_presencia_gnd(self) -> List[Issue]:
        if any(n.is_gnd for n in self.m.nets.values()):
            return []
        return [Issue("error", "NO_GND",
                      "No se encontró un nodo de tierra (GND). "
                      "Agrega al menos un 'GND' conectado al circuito.")]

    def _comprobar_nodos_flotantes(self) -> List[Issue]:
        out: List[Issue] = []
        for net in self.m.nets.values():
            if net.is_gnd:
                continue
            if len(net.pins) <= 1:
                comps = ", ".join(
                    {p.comp_name for p in net.pins}) or "(sin componente)"
                out.append(Issue("warning", "FLOAT_NODE",
                                 f"Nodo flotante id={net.id}: solo un terminal conectado ({comps})."))
        return out

    def _comprobar_cortos_en_componentes(self) -> List[Issue]:
        out: List[Issue] = []
        for c in self.m.components:
            if c.type in {"Push Button Cerrado"}:
                continue
            nets_ids = [p.net_id for p in c.pins]
            if len(nets_ids) >= 2 and len(set(nets_ids)) == 1:
                out.append(Issue("error", "INTRA_SHORT",
                                 f"Corto interno en '{c.name}' ({c.type}): sus terminales "
                                 f"están en el mismo nodo {nets_ids[0]}."))
        return out

    def _comprobar_fuentes_voltaje_en_conflicto(self) -> List[Issue]:
        out: List[Issue] = []
        pair_map: Dict[Tuple[int, int], List[str]] = {}
        for c in self.m.components:
            if c.type in self.VOLTAGE_NAMES and len(c.pins) >= 2:
                a, b = c.pins[0].net_id, c.pins[1].net_id
                key = tuple(sorted((a, b)))
                pair_map.setdefault(key, []).append(c.name)
        for key, lst in pair_map.items():
            if len(lst) >= 2:
                out.append(Issue("warning", "PAR_VSRC",
                                 f"Hay {len(lst)} fuentes de voltaje en paralelo entre nodos {key}: {', '.join(lst)}. "
                                 "Si sus valores son distintos, el sistema será singular."))
        return out

    def _comprobar_fuente_en_cortocircuito(self) -> List[Issue]:
        out: List[Issue] = []
        for c in self.m.components:
            if c.type in self.VOLTAGE_NAMES and len(c.pins) >= 2:
                a, b = c.pins[0].net_id, c.pins[1].net_id
                if a == b:
                    out.append(Issue("error", "VSRC_SHORT",
                                     f"La fuente '{c.name}' está cortocircuitada (ambos pines en el nodo {a})."))
        return out


def problemas_a_html(issues: List[Issue]) -> str:
    try:
        if not issues:
            header = traducir('Chequeo eléctrico')
            ok_msg = traducir('sin problemas.')
            return f"<b>{header}:</b> {ok_msg}"
        lines: List[str] = []
        level_emoji = {"error": "⛔", "warning": "⚠️", "info": "ℹ️"}
        for i in issues:
            pref = level_emoji.get(i.level, "•")
            msg_translated = traducir_mensaje_problema(i.msg)
            lines.append(f"{pref} <b>{i.code}</b>: {msg_translated}")
            if i.details:
                detail_translated = traducir_mensaje_problema(i.details)
                lines.append(f"<i>{detail_translated}</i>")
        return "<br>".join(lines)
    except Exception:
        basic_lines: List[str] = []
        level_emoji = {"error": "⛔", "warning": "⚠️", "info": "ℹ️"}
        for i in issues:
            pref = level_emoji.get(i.level, "•")
            basic_lines.append(f"{pref} <b>{i.code}</b>: {i.msg}")
            if i.details:
                basic_lines.append(f"<i>{i.details}</i>")
        return "<br>".join(basic_lines)


def aplicar_a(clase=None):
    for nombre in ['Pin', 'Net', 'Component', 'CircuitModel', 'ModelBuilder', 'Issue', 'EarlyElectricalChecks', 'problemas_a_html', 'EsimulatorCore']:
        if nombre in globals():
            setattr(_base, nombre, globals()[nombre])
    return True
