import Interfaz as _base
from Interfaz import *
try:
    _ = _base._
except Exception:
    def _(text):
        return text


class VLSMCalculatorDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(traducir('Calculadora de subred VSLM'))
        self.setModal(True)

        form_layout = QFormLayout()
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.0.0.0")
        form_layout.addRow(traducir('Dirección IP'), self.ip_edit)

        self.prefix_spin = QSpinBox()
        self.prefix_spin.setRange(1, 32)
        self.prefix_spin.setValue(24)
        form_layout.addRow(traducir('Prefijo de red'), self.prefix_spin)

        self.subnets_spin = QSpinBox()
        self.subnets_spin.setRange(1, 64)
        self.subnets_spin.setValue(1)
        form_layout.addRow(traducir('Número de subredes'), self.subnets_spin)

        self.hosts_table = QTableWidget()
        self.hosts_table.setColumnCount(2)
        self.hosts_table.setHorizontalHeaderLabels(
            [traducir('Subred'), traducir('Número de Hosts')])
        self.hosts_table.horizontalHeader().setStretchLastSection(True)
        self.hosts_table.verticalHeader().setVisible(False)

        self.calc_button = QPushButton(traducir('Calcular'))
        self.calc_button.clicked.connect(self.calcular)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            traducir('Subred'), traducir('Nº de Hosts'), traducir(
                'IP de red'), traducir('Prefijo'),
            traducir('Máscara'), traducir('Primer Host'), traducir(
                'Último Host'), traducir('Broadcast')
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.verticalHeader().setVisible(False)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.hosts_table)
        layout.addWidget(self.calc_button)
        layout.addWidget(self.results_table)

        self.subnets_spin.valueChanged.connect(self.actualizar_tabla_hosts)
        self.actualizar_tabla_hosts()

    def actualizar_tabla_hosts(self) -> None:
        count = self.subnets_spin.value()
        self.hosts_table.setRowCount(count)
        for row in range(count):
            base_label = traducir('Subred')
            item0 = QTableWidgetItem(f"{base_label} {row + 1}")
            item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)
            self.hosts_table.setItem(row, 0, item0)
            if not self.hosts_table.item(row, 1):
                self.hosts_table.setItem(row, 1, QTableWidgetItem(""))

    def sanear_ip(self, ip_str: str) -> str:
        parts = [p for p in ip_str.strip().split('.') if p != '']
        if len(parts) > 4:
            parts = parts[:4]
        return '.'.join(parts)

    def calcular(self) -> None:
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        ip_raw = self.ip_edit.text().strip()
        ip_clean = self.sanear_ip(ip_raw)
        prefix = self.prefix_spin.value()
        try:
            network = ipaddress.ip_network(
                f"{ip_clean}/{prefix}", strict=False)
        except Exception as exc:
            try:
                network = ipaddress.ip_network(
                    f"0.0.0.0/{prefix}", strict=False)
            except Exception:
                QMessageBox.critical(
                    self, "Error", f"Dirección IP o prefijo inválido:\n{exc}")
                return
        host_counts: List[int] = []
        for row in range(self.hosts_table.rowCount()):
            item = self.hosts_table.item(row, 1)
            txt = item.text().strip() if item else ''
            if not txt:
                host_counts.append(0)
            else:
                try:
                    val = int(txt)
                    host_counts.append(max(val, 0))
                except Exception:
                    host_counts.append(0)
        try:
            results = self.calcular_vlsm(network, host_counts)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return
        sorted_results = sorted(
            results, key=lambda r: r.get("hosts", 0), reverse=True)
        for idx, res in enumerate(sorted_results):
            res["subnet"] = f"{traducir('Subred')} {idx + 1}"
        self.results_table.setRowCount(len(sorted_results))
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            traducir('Subred'), traducir('Nº de Hosts'), traducir(
                'IP de red'), traducir('Prefijo'),
            traducir('Máscara'), traducir('Primer Host'), traducir(
                'Último Host'), traducir('Broadcast')
        ])
        for row, res in enumerate(sorted_results):
            self.results_table.setItem(row, 0, QTableWidgetItem(res["subnet"]))
            self.results_table.setItem(
                row, 1, QTableWidgetItem(str(res["hosts"])))
            self.results_table.setItem(
                row, 2, QTableWidgetItem(res["network"]))
            self.results_table.setItem(
                row, 3, QTableWidgetItem(f"/{res['prefix']}"))
            self.results_table.setItem(
                row, 4, QTableWidgetItem(res["netmask"]))
            self.results_table.setItem(
                row, 5, QTableWidgetItem(res["first_host"]))
            self.results_table.setItem(
                row, 6, QTableWidgetItem(res["last_host"]))
            self.results_table.setItem(
                row, 7, QTableWidgetItem(res["broadcast"]))
        try:
            self.results_table.resizeColumnsToContents()
        except Exception:
            pass

    def calcular_vlsm(self, base_network: ipaddress.IPv4Network, host_counts: List[int]) -> List[Dict[str, Any]]:
        indexed = []
        for idx, cnt in enumerate(host_counts):
            try:
                cnt_int = int(cnt)
            except Exception:
                cnt_int = 0
            if cnt_int < 0:
                cnt_int = 0
            indexed.append((idx, cnt_int))
        sorted_hosts = sorted(indexed, key=lambda x: -x[1])
        allocations: Dict[int, Dict[str, Any]] = {}
        current_addr = base_network.network_address
        for orig_idx, hosts_needed in sorted_hosts:
            needed = hosts_needed + 2 if hosts_needed > 0 else 2
            bits = (needed - 1).bit_length()
            prefix = 32 - bits
            if prefix < base_network.prefixlen:
                prefix = base_network.prefixlen
            try:
                subnet = ipaddress.ip_network(
                    f"{current_addr}/{prefix}", strict=False)
            except Exception as exc:
                raise ValueError(f"No se puede crear la subred: {exc}")
            if not (subnet.network_address >= base_network.network_address and subnet.broadcast_address <= base_network.broadcast_address):
                raise ValueError(
                    "Las subredes exceden el rango de la red base.")
            total_addrs = subnet.num_addresses
            if total_addrs <= 2:
                first_host = str(subnet.network_address)
                last_host = str(subnet.broadcast_address)
            else:
                first_host = str(subnet.network_address + 1)
                last_host = str(subnet.broadcast_address - 1)
            allocations[orig_idx] = {
                "subnet": f"Subred {orig_idx + 1}",
                "hosts": hosts_needed,
                "network": str(subnet.network_address),
                "prefix": subnet.prefixlen,
                "netmask": str(subnet.netmask),
                "first_host": first_host,
                "last_host": last_host,
                "broadcast": str(subnet.broadcast_address),
            }
            try:
                current_addr = subnet.broadcast_address + 1
            except Exception:
                current_addr = subnet.broadcast_address
        return [allocations[i] for i in range(len(host_counts))]


def aplicar_a(clase=None):
    _base.VLSMCalculatorDialog = VLSMCalculatorDialog
    return VLSMCalculatorDialog
