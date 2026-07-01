from PyQt5.QtWidgets import QMessageBox, QMenu, QApplication
from PyQt5.QtCore import Qt
from typing import Any, Optional, Dict, List, Tuple

CURRENT_LANGUAGE: str = 'es'

TRANSLATIONS = {
    'Archivo': {'es': 'Archivo', 'en': 'File'},
    'Simulación': {'es': 'Simulación', 'en': 'Simulation'},
    'Edición': {'es': 'Edición', 'en': 'Edit'},
    'Herramientas': {'es': 'Herramientas', 'en': 'Tools'},
    'Plantillas': {'es': 'Plantillas', 'en': 'Templates'},
    'Insertar': {'es': 'Insertar', 'en': 'Insert'},
    'Ver': {'es': 'Ver', 'en': 'View'},
    'Ayuda': {'es': 'Ayuda', 'en': 'Help'},
    'Plugins': {'es': 'Plugins', 'en': 'Plugins'},
    'Idiomas': {'es': 'Idiomas', 'en': 'Languages'},
    'Español': {'es': 'Español', 'en': 'Spanish'},
    'Inglés': {'es': 'Inglés', 'en': 'English'},
    'Reestablecer': {'es': 'Reestablecer', 'en': 'Undo'},
    'Restablecer': {'es': 'Restablecer', 'en': 'Reset'},
    'solo números': {'es': 'solo números', 'en': 'numbers only'},
    'Entrada de parámetro': {'es': 'Entrada de parámetro', 'en': 'Parameter input'},
    'Tolerancia': {'es': 'Tolerancia', 'en': 'Tolerance'},
    'Selecciona la tolerancia (%):': {'es': 'Selecciona la tolerancia (%):', 'en': 'Select the tolerance (%):'},
    'Potencia nominal': {'es': 'Potencia nominal', 'en': 'Nominal power'},
    'Selecciona la potencia nominal:': {'es': 'Selecciona la potencia nominal:', 'en': 'Select the nominal power:'},
    'Valor del Potenciómetro': {'es': 'Valor del Potenciómetro', 'en': 'Potentiometer value'},
    'Selecciona valor comercial:': {'es': 'Selecciona valor comercial:', 'en': 'Select commercial value:'},
    'Porcentaje del cursor': {'es': 'Porcentaje del cursor', 'en': 'Cursor percentage'},
    'Ingresa el % del cursor (0-100):': {'es': 'Ingresa el % del cursor (0-100):', 'en': 'Enter the cursor percentage (0-100):'},
    'Voltaje del generador': {'es': 'Voltaje del generador', 'en': 'Generator voltage'},
    'Voltaje': {'es': 'Voltaje', 'en': 'Voltage'},
    'Voltaje (solo números):': {'es': 'Voltaje (solo números):', 'en': 'Voltage (numbers only):'},
    'Frecuencia del generador': {'es': 'Frecuencia del generador', 'en': 'Generator frequency'},
    'Frecuencia': {'es': 'Frecuencia', 'en': 'Frequency'},
    'Frecuencia (solo números):': {'es': 'Frecuencia (solo números):', 'en': 'Frequency (numbers only):'},
    'Offset DC': {'es': 'Offset DC', 'en': 'DC Offset'},
    'Offset DC (solo números):': {'es': 'Offset DC (solo números):', 'en': 'DC Offset (numbers only):'},
    'Fase': {'es': 'Fase', 'en': 'Phase'},
    'Fase (grados, solo números):': {'es': 'Fase (grados, solo números):', 'en': 'Phase (degrees, numbers only):'},
    'Forma de onda': {'es': 'Forma de onda', 'en': 'Waveform'},
    'Selecciona la forma de onda:': {'es': 'Selecciona la forma de onda:', 'en': 'Select the waveform:'},
    'Tensión de la batería': {'es': 'Tensión de la batería', 'en': 'Battery voltage'},
    'Selecciona tensión:': {'es': 'Selecciona tensión:', 'en': 'Select voltage:'},
    'Color del LED': {'es': 'Color del LED', 'en': 'LED color'},
    'Selecciona color:': {'es': 'Selecciona color:', 'en': 'Select color:'},
    'Modelo Transistor': {'es': 'Modelo Transistor', 'en': 'Transistor model'},
    'Modelo Op-Amp': {'es': 'Modelo Op-Amp', 'en': 'Op-Amp model'},
    'Selecciona modelo:': {'es': 'Selecciona modelo:', 'en': 'Select model:'},
    'Ciclo de trabajo': {'es': 'Ciclo de trabajo', 'en': 'Duty cycle'},
    'Ciclo de trabajo (%) (0-100):': {'es': 'Ciclo de trabajo (%) (0-100):', 'en': 'Duty cycle (%) (0-100):'},
    'Rehacer': {'es': 'Rehacer', 'en': 'Redo'},
    'Cortar': {'es': 'Cortar', 'en': 'Cut'},
    'Copiar': {'es': 'Copiar', 'en': 'Copy'},
    'Pegar': {'es': 'Pegar', 'en': 'Paste'},
    'Eliminar': {'es': 'Eliminar', 'en': 'Delete'},
    'Seleccionar': {'es': 'Seleccionar', 'en': 'Select'},
    'Seleccionar todo': {'es': 'Seleccionar todo', 'en': 'Select All'},
    'Rotar': {'es': 'Rotar', 'en': 'Rotate'},
    'Tierra': {'es': 'Tierra', 'en': 'Ground'},
    'Etiqueta Cable': {'es': 'Etiqueta Cable', 'en': 'Cable Label'},
    'Conexión': {'es': 'Conexión', 'en': 'Connection'},
    'Ampliar': {'es': 'Ampliar', 'en': 'Zoom In'},
    'Reducir': {'es': 'Reducir', 'en': 'Zoom Out'},
    'Ver Todo': {'es': 'Ver Todo', 'en': 'View All'},
    'Vista 1:1': {'es': 'Vista 1:1', 'en': '1:1 View'},
    'Gráfica Bode (AC)': {'es': 'Gráfica Bode (AC)', 'en': 'Bode Plot (AC)'},
    'Gráfica LGR': {'es': 'Gráfica LGR', 'en': 'LGR Plot'},
    'Calculadora de subred VSLM': {'es': 'Calculadora de subred VSLM', 'en': 'VLSM Subnet Calculator'},
    'Calculadora de resistencias': {'es': 'Calculadora de resistencias', 'en': 'Resistance Calculator'},
    'VNA View': {'es': 'VNA View', 'en': 'VNA View'},
    'Exportar Proyecto Extendido': {'es': 'Exportar Proyecto Extendido', 'en': 'Extended Project Export'},
    'Atajos de Teclado': {'es': 'Atajos de Teclado', 'en': 'Keyboard Shortcuts'},
    'Agregar Componente': {'es': 'Agregar Componente', 'en': 'Add Component'},
    'Conectar': {'es': 'Conectar', 'en': 'Connect'},
    'Simular Voltajes': {'es': 'Simular Voltajes', 'en': 'Simulate Voltages'},
    'Simular Corrientes': {'es': 'Simular Corrientes', 'en': 'Simulate Currents'},
    'Simular todo': {'es': 'Simular todo', 'en': 'Simulate All'},
    'Inspector de propiedades': {'es': 'Inspector de propiedades', 'en': 'Properties Inspector'},
    'Salir': {'es': 'Salir', 'en': 'Exit'},
    '¿Estás seguro que quieres salir?': {'es': '¿Estás seguro que quieres salir?', 'en': 'Are you sure you want to exit?'},
    'Sí': {'es': 'Sí', 'en': 'Yes'},
    'No': {'es': 'No', 'en': 'No'},
    'Modo Claro': {'es': 'Modo Claro', 'en': 'Light Mode'},
    'Modo Oscuro': {'es': 'Modo Oscuro', 'en': 'Dark Mode'},
    'Modo conexión activado': {'es': 'Modo conexión activado', 'en': 'Connection mode activated'},
    'Pestaña': {'es': 'Pestaña', 'en': 'Tab'},
    'Buscar componente...': {'es': 'Buscar componente...', 'en': 'Search component...'},
    'Atajos de teclado disponibles:': {'es': 'Atajos de teclado disponibles:', 'en': 'Available keyboard shortcuts:'},
    'Cortar componentes': {'es': 'Cortar componentes', 'en': 'Cut components'},
    'Copiar componentes': {'es': 'Copiar componentes', 'en': 'Copy components'},
    'Pegar componentes': {'es': 'Pegar componentes', 'en': 'Paste components'},
    'Eliminar selección': {'es': 'Eliminar selección', 'en': 'Delete selection'},
    'Deshacer': {'es': 'Deshacer', 'en': 'Undo'},
    'Rehacer': {'es': 'Rehacer', 'en': 'Redo'},
    'Seleccionar todo': {'es': 'Seleccionar todo', 'en': 'Select all'},
    'Acercar vista (zoom in)': {'es': 'Acercar vista (zoom in)', 'en': 'Zoom in'},
    'Alejar vista (zoom out)': {'es': 'Alejar vista (zoom out)', 'en': 'Zoom out'},
    'Ver todo': {'es': 'Ver todo', 'en': 'View all'},
    'Restablecer escala 1:1': {'es': 'Restablecer escala 1:1', 'en': 'Reset scale 1:1'},
    'Cargar circuito': {'es': 'Cargar circuito', 'en': 'Load circuit'},
    'Nueva pestaña': {'es': 'Nueva pestaña', 'en': 'New Tab'},
    'Guardar Circuito': {'es': 'Guardar Circuito', 'en': 'Save Circuit'},
    'Cargar': {'es': 'Cargar', 'en': 'Load'},
    'PDF': {'es': 'PDF', 'en': 'PDF'},
    'Txt': {'es': 'Txt', 'en': 'Txt'},
    'PNG': {'es': 'PNG', 'en': 'PNG'},
    'Lista de Materiales (BOM)': {'es': 'Lista de Materiales (BOM)', 'en': 'Bill of Materials (BOM)'},
    'Exportar datos y mediciones': {'es': 'Exportar datos y mediciones', 'en': 'Export data and measurements'},
    'Reporte PDF completo': {'es': 'Reporte PDF completo', 'en': 'Full PDF Report'},
    'Reporte Word completo': {'es': 'Reporte Word completo', 'en': 'Full Word Report'},
    'Abrir Proyecto Extendido': {'es': 'Abrir Proyecto Extendido', 'en': 'Open Extended Project'},
    'Recientes': {'es': 'Recientes', 'en': 'Recent'},
    'Exportar netlist SPICE/Qucs': {'es': 'Exportar netlist SPICE/Qucs', 'en': 'Export SPICE/Qucs netlist'},
    'Ejecutar SPICE/Qucs': {'es': 'Ejecutar SPICE/Qucs', 'en': 'Run SPICE/Qucs'},
    'Simular Voltaje': {'es': 'Simular Voltaje', 'en': 'Simulate Voltage'},
    'Simular Corriente': {'es': 'Simular Corriente', 'en': 'Simulate Current'},
    'Simular todo': {'es': 'Simular todo', 'en': 'Simulate All'},
    'Simular lógica': {'es': 'Simular lógica', 'en': 'Simulate Logic'},
    'Barrido Monte Carlo': {'es': 'Barrido Monte Carlo', 'en': 'Monte Carlo Sweep'},
    'Modo Laboratorio': {'es': 'Modo Laboratorio', 'en': 'Laboratory Mode'},
    'Guardar Medición': {'es': 'Guardar Medición', 'en': 'Save Measurement'},
    'Ver mediciones': {'es': 'Ver mediciones', 'en': 'View measurements'},
    'Medir Voltaje': {'es': 'Medir Voltaje', 'en': 'Measure Voltage'},
    'Medir Corriente': {'es': 'Medir Corriente', 'en': 'Measure Current'},
    'Medir Resistencia': {'es': 'Medir Resistencia', 'en': 'Measure Resistance'},
    'Mostrar Gráficas': {'es': 'Mostrar Gráficas', 'en': 'Show Graphs'},
    'Osciloscopio': {'es': 'Osciloscopio', 'en': 'Oscilloscope'},
    'Mediciones activas': {'es': 'Mediciones activas', 'en': 'Active Measurements'},
    'Consola de scripts': {'es': 'Consola de scripts', 'en': 'Script Console'},
    'Cantidad de bandas:': {'es': 'Cantidad de bandas:', 'en': 'Number of bands:'},
    '4 bandas': {'es': '4 bandas', 'en': '4 bands'},
    '5 bandas': {'es': '5 bandas', 'en': '5 bands'},
    '6 bandas': {'es': '6 bandas', 'en': '6 bands'},
    '1.ª banda de color': {'es': '1.ª banda de color', 'en': '1st color band'},
    '2.ª banda de color': {'es': '2.ª banda de color', 'en': '2nd color band'},
    '3.ª banda de color': {'es': '3.ª banda de color', 'en': '3rd color band'},
    'Multiplicador': {'es': 'Multiplicador', 'en': 'Multiplier'},
    'Tolerancia': {'es': 'Tolerancia', 'en': 'Tolerance'},
    'ppm': {'es': 'ppm', 'en': 'ppm'},
    'Calcular': {'es': 'Calcular', 'en': 'Calculate'},
    'Limpiar': {'es': 'Limpiar', 'en': 'Clear'},
    'Valor nominal': {'es': 'Valor nominal', 'en': 'Nominal value'},
    'Confiabilidad': {'es': 'Confiabilidad', 'en': 'Reliability'},
    'Bode de función de transferencia': {'es': 'Bode de función de transferencia', 'en': 'Bode of transfer function'},
    'Ingresa H(s) (usa s para la variable compleja):': {'es': 'Ingresa H(s) (usa s para la variable compleja):', 'en': 'Enter H(s) (use s for the complex variable):'},
    'Gráfica LGR limpia': {'es': 'Gráfica LGR limpia', 'en': 'Clean LGR plot'},
    'Ingresa la función de transferencia G(s):': {'es': 'Ingresa la función de transferencia G(s):', 'en': 'Enter the transfer function G(s):'},
    'LGR de función de transferencia': {'es': 'LGR de función de transferencia', 'en': 'LGR of transfer function'},
    'Dirección IP': {'es': 'Dirección IP', 'en': 'IP Address'},
    'Prefijo de red': {'es': 'Prefijo de red', 'en': 'Network prefix'},
    'Número de subredes': {'es': 'Número de subredes', 'en': 'Number of subnets'},
    'Subred': {'es': 'Subred', 'en': 'Subnet'},
    'Número de Hosts': {'es': 'Número de Hosts', 'en': 'Number of hosts'},
    'Nº de Hosts': {'es': 'Nº de Hosts', 'en': 'No. of hosts'},
    'IP de red': {'es': 'IP de red', 'en': 'Network IP'},
    'Prefijo': {'es': 'Prefijo', 'en': 'Prefix'},
    'Máscara': {'es': 'Máscara', 'en': 'Mask'},
    'Primer Host': {'es': 'Primer Host', 'en': 'First Host'},
    'Último Host': {'es': 'Último Host', 'en': 'Last Host'},
    'Broadcast': {'es': 'Broadcast', 'en': 'Broadcast'},
    'Resistencia': {'es': 'Resistencia', 'en': 'Resistor'},
    'Potenciómetro': {'es': 'Potenciómetro', 'en': 'Potentiometer'},
    'Push Button': {'es': 'Push Button', 'en': 'Push Button'},
    'Push Button Cerrado': {'es': 'Push Button Cerrado', 'en': 'Push Button Closed'},
    'Push Button Abierto': {'es': 'Push Button Abierto', 'en': 'Push Button Open'},
    'Fuente Voltaje': {'es': 'Fuente Voltaje', 'en': 'Voltage Source'},
    'Fuente Corriente': {'es': 'Fuente Corriente', 'en': 'Current Source'},
    'Transformador': {'es': 'Transformador', 'en': 'Transformer'},
    'Generador de funciones': {'es': 'Generador de funciones', 'en': 'Function generator'},
    'Capacitor': {'es': 'Capacitor', 'en': 'Capacitor'},
    'Bobina': {'es': 'Bobina', 'en': 'Inductor'},
    'Batería': {'es': 'Batería', 'en': 'Battery'},
    'Motor': {'es': 'Motor', 'en': 'Motor'},
    'GND': {'es': 'GND', 'en': 'GND'},
    'LED': {'es': 'LED', 'en': 'LED'},
    'Diodo Zener': {'es': 'Diodo Zener', 'en': 'Zener Diode'},
    'Mosfet': {'es': 'Mosfet', 'en': 'MOSFET'},
    'OpAmp': {'es': 'OpAmp', 'en': 'OpAmp'},
    'Transistor NPN': {'es': 'Transistor NPN', 'en': 'NPN Transistor'},
    'Transistor PNP': {'es': 'Transistor PNP', 'en': 'PNP Transistor'},
    'AND': {'es': 'AND', 'en': 'AND'},
    'OR': {'es': 'OR', 'en': 'OR'},
    'NAND': {'es': 'NAND', 'en': 'NAND'},
    'NOR': {'es': 'NOR', 'en': 'NOR'},
    'XOR': {'es': 'XOR', 'en': 'XOR'},
    'NOT': {'es': 'NOT', 'en': 'NOT'},
    'Amperímetro': {'es': 'Amperímetro', 'en': 'Ammeter'},
    'Voltímetro': {'es': 'Voltímetro', 'en': 'Voltmeter'},
    'Ohmímetro': {'es': 'Ohmímetro', 'en': 'Ohmmeter'},
    'Resultados y Mediciones': {'es': 'Resultados y Mediciones', 'en': 'Results and Measurements'},
    'Frecuencia (Hz)': {'es': 'Frecuencia (Hz)', 'en': 'Frequency (Hz)'},
    'Fase (°)': {'es': 'Fase (°)', 'en': 'Phase (°)'},
    'Valor fuera de rango': {'es': 'Valor fuera de rango', 'en': 'Value out of range'},
    'Por favor ingresa un valor entre 0 y 100.': {
        'es': 'Por favor ingresa un valor entre 0 y 100.',
        'en': 'Please enter a value between 0 and 100.'
    },
    'Valor inválido': {'es': 'Valor inválido', 'en': 'Invalid value'},
    'El valor no puede ser negativo.': {
        'es': 'El valor no puede ser negativo.',
        'en': 'The value cannot be negative.'
    },
    'Por favor ingresa un número válido para el voltaje.': {
        'es': 'Por favor ingresa un número válido para el voltaje.',
        'en': 'Please enter a valid number for the voltage.'
    },
    'El voltaje no puede ser negativo.': {
        'es': 'El voltaje no puede ser negativo.',
        'en': 'The voltage cannot be negative.'
    },
    'Por favor ingresa un número válido para la frecuencia.': {
        'es': 'Por favor ingresa un número válido para la frecuencia.',
        'en': 'Please enter a valid number for the frequency.'
    },
    'La frecuencia no puede ser negativa.': {
        'es': 'La frecuencia no puede ser negativa.',
        'en': 'The frequency cannot be negative.'
    },
    'Por favor ingresa un número válido para el offset.': {
        'es': 'Por favor ingresa un número válido para el offset.',
        'en': 'Please enter a valid number for the offset.'
    },
    'Por favor ingresa un número válido para la fase.': {
        'es': 'Por favor ingresa un número válido para la fase.',
        'en': 'Please enter a valid number for the phase.'
    },
    'Por favor ingresa un número válido para el ciclo de trabajo.': {
        'es': 'Por favor ingresa un número válido para el ciclo de trabajo.',
        'en': 'Please enter a valid number for the duty cycle.'
    },
    'El ciclo de trabajo debe estar entre 0 y 100.': {
        'es': 'El ciclo de trabajo debe estar entre 0 y 100.',
        'en': 'The duty cycle must be between 0 and 100.'
    },
    'Por favor ingresa un número válido (ej. 4.7, 100, 0.01).': {
        'es': 'Por favor ingresa un número válido (ej. 4.7, 100, 0.01).',
        'en': 'Please enter a valid number (e.g., 4.7, 100, 0.01).'
    },
    'Valor': {'es': 'Valor', 'en': 'Value'},
    'Cursor': {'es': 'Cursor', 'en': 'Cursor'},
    'Unidad': {'es': 'Unidad', 'en': 'Unit'},
    'Selecciona unidad para': {'es': 'Selecciona unidad para', 'en': 'Select unit for'},
    'Selecciona unidad para el voltaje:': {
        'es': 'Selecciona unidad para el voltaje:',
        'en': 'Select unit for the voltage:'
    },
    'Selecciona unidad para la frecuencia:': {
        'es': 'Selecciona unidad para la frecuencia:',
        'en': 'Select unit for the frequency:'
    },
    'Selecciona unidad para el offset:': {
        'es': 'Selecciona unidad para el offset:',
        'en': 'Select unit for the offset:'
    },
    'Unidad de voltaje': {'es': 'Unidad de voltaje', 'en': 'Voltage unit'},
    'Unidad de frecuencia': {'es': 'Unidad de frecuencia', 'en': 'Frequency unit'},
    'Unidad de offset': {'es': 'Unidad de offset', 'en': 'Offset unit'},
    'Voltaje del generador': {'es': 'Voltaje del generador', 'en': 'Generator voltage'},
    'Voltaje (solo números):': {'es': 'Voltaje (solo números):', 'en': 'Voltage (numbers only):'},
    'Frecuencia del generador': {'es': 'Frecuencia del generador', 'en': 'Generator frequency'},
    'Frecuencia (solo números):': {'es': 'Frecuencia (solo números):', 'en': 'Frequency (numbers only):'},
    'Offset DC': {'es': 'Offset DC', 'en': 'DC Offset'},
    'Offset DC (solo números):': {'es': 'Offset DC (solo números):', 'en': 'DC Offset (numbers only):'},
    'Fase': {'es': 'Fase', 'en': 'Phase'},
    'Fase (grados, solo números):': {'es': 'Fase (grados, solo números):', 'en': 'Phase (degrees, numbers only):'},
    'Forma de onda': {'es': 'Forma de onda', 'en': 'Waveform'},
    'Selecciona la forma de onda:': {
        'es': 'Selecciona la forma de onda:',
        'en': 'Select the waveform:'
    },
    'Ciclo de trabajo': {'es': 'Ciclo de trabajo', 'en': 'Duty cycle'},
    'Ciclo de trabajo (%) (0-100):': {
        'es': 'Ciclo de trabajo (%) (0-100):',
        'en': 'Duty cycle (%) (0-100):'
    },
    'Senoidal': {'es': 'Senoidal', 'en': 'Sine'},
    'Cuadrada': {'es': 'Cuadrada', 'en': 'Square'},
    'Triangular': {'es': 'Triangular', 'en': 'Triangular'},
    'Diente de sierra': {'es': 'Diente de sierra', 'en': 'Sawtooth'},
    'Forma': {'es': 'Forma', 'en': 'Waveform'},
    'Modelo MOSFET': {'es': 'Modelo MOSFET', 'en': 'MOSFET model'},
    'Tipo': {'es': 'Tipo', 'en': 'Type'},
    'Canal:': {'es': 'Canal:', 'en': 'Channel:'},
    'Canal N': {'es': 'Canal N', 'en': 'N-channel'},
    'Canal P': {'es': 'Canal P', 'en': 'P-channel'},
    'Tensión umbral (V):': {'es': 'Tensión umbral (V):', 'en': 'Threshold voltage (V):'},
    'Resistencia de conducción (Ω):': {
        'es': 'Resistencia de conducción (Ω):',
        'en': 'On resistance (Ω):'
    },
    'Ganancia de corriente (β):': {
        'es': 'Ganancia de corriente (β):',
        'en': 'Current gain (β):'
    },
    'Voltaje base-emisor (V):': {
        'es': 'Voltaje base-emisor (V):',
        'en': 'Base-emitter voltage (V):'
    },
    'hfe (factor de amplificación):': {
        'es': 'hfe (factor de amplificación):',
        'en': 'hfe (amplification factor):'
    },
    'Color': {'es': 'Color', 'en': 'Color'},
    'Offset': {'es': 'Offset', 'en': 'Offset'},
    'Voltaje Zener (V):': {'es': 'Voltaje Zener (V):', 'en': 'Zener voltage (V):'},
    'Corriente máxima (mA):': {'es': 'Corriente máxima (mA):', 'en': 'Maximum current (mA):'},
    'Tensión': {'es': 'Tensión', 'en': 'Voltage'},
    'Potencia': {'es': 'Potencia', 'en': 'Power'},
    'Exportar Resultados': {'es': 'Exportar Resultados', 'en': 'Export Results'},
    'Exportar Imagen': {'es': 'Exportar Imagen', 'en': 'Export Image'},
    'Exportar PDF': {'es': 'Exportar PDF', 'en': 'Export PDF'},
    'Limpiar Todo': {'es': 'Limpiar Todo', 'en': 'Clear All'},
    'Texto': {'es': 'Texto', 'en': 'Text'},
    'Exportar CSV (Med./Gráf.)': {'es': 'Exportar CSV (Med./Gráf.)', 'en': 'Export CSV (Meas./Graphs)'},
    'Unidad': {'es': 'Unidad', 'en': 'Unit'},
    'Unidad de voltaje': {'es': 'Unidad de voltaje', 'en': 'Voltage unit'},
    'Unidad de frecuencia': {'es': 'Unidad de frecuencia', 'en': 'Frequency unit'},
    'Unidad de offset': {'es': 'Unidad de offset', 'en': 'Offset unit'},
    'Selecciona unidad para': {'es': 'Selecciona unidad para', 'en': 'Select unit for'},
    'Selecciona unidad para el voltaje:': {'es': 'Selecciona unidad para el voltaje:', 'en': 'Select unit for the voltage:'},
    'Selecciona unidad para la frecuencia:': {'es': 'Selecciona unidad para la frecuencia:', 'en': 'Select unit for the frequency:'},
    'Selecciona unidad para el offset:': {'es': 'Selecciona unidad para el offset:', 'en': 'Select unit for the offset:'},
    'Selecciona unidad para Resistencia:': {'es': 'Selecciona unidad para Resistencia:', 'en': 'Select unit for Resistance:'},
    'Valor inválido': {'es': 'Valor inválido', 'en': 'Invalid value'},
    'Cargar Circuito': {'es': 'Cargar Circuito', 'en': 'Load Circuit'},
    'Mostrar Conexiones': {'es': 'Mostrar Conexiones', 'en': 'Show Connections'},
    'Inspector de Errores': {'es': 'Inspector de Errores', 'en': 'Error Inspector'},
    'Zoom +': {'es': 'Zoom +', 'en': 'Zoom +'},
    'Zoom -': {'es': 'Zoom -', 'en': 'Zoom -'},
    'Nodos explícitos': {'es': 'Nodos explícitos', 'en': 'Explicit nodes'},
    'Mostrar nodos': {'es': 'Mostrar nodos', 'en': 'Show nodes'},
    'Ocultar nodos': {'es': 'Ocultar nodos', 'en': 'Hide nodes'},
    'Etiquetas de red': {'es': 'Etiquetas de red', 'en': 'Net labels'},
    'Resaltado de red': {'es': 'Resaltado de red', 'en': 'Net highlighting'},
    'Alinear/Distribuir': {'es': 'Alinear/Distribuir', 'en': 'Align/Distribute'},
    'Alinear izquierda': {'es': 'Alinear izquierda', 'en': 'Align left'},
    'Alinear derecha': {'es': 'Alinear derecha', 'en': 'Align right'},
    'Alinear centro': {'es': 'Alinear centro', 'en': 'Align center'},
    'Distribuir horizontal': {'es': 'Distribuir horizontal', 'en': 'Distribute horizontally'},
    'Distribuir vertical': {'es': 'Distribuir vertical', 'en': 'Distribute vertically'},
    'Duplicar': {'es': 'Duplicar', 'en': 'Duplicate'},
    'Bloquear elementos': {'es': 'Bloquear elementos', 'en': 'Lock elements'},
    'Solo seleccionar cables': {'es': 'Solo seleccionar cables', 'en': 'Select only wires'},
    'Solo seleccionar componentes': {'es': 'Solo seleccionar componentes', 'en': 'Select only components'},
    'Ruteo inteligente': {'es': 'Ruteo inteligente', 'en': 'Smart routing'},
    'Puentes': {'es': 'Puentes', 'en': 'Jump-over'},
    'Función en desarrollo': {'es': 'Función en desarrollo', 'en': 'Feature under development'},
    'Chequeo eléctrico': {'es': 'Chequeo eléctrico', 'en': 'Electrical check'},
    'sin problemas.': {'es': 'sin problemas.', 'en': 'no problems.'},
    'Exportar como Imagen': {'es': 'Exportar como Imagen', 'en': 'Export Image'},
    'Acercar vista': {'es': 'Acercar vista', 'en': 'Zoom in'},
    'Alejar vista': {'es': 'Alejar vista', 'en': 'Zoom out'},
    'Mostrar y exportar la lista de materiales (BOM)': {
        'es': 'Mostrar y exportar la lista de materiales (BOM)',
        'en': 'Show and export the bill of materials (BOM)'
    },
    'Exporta datos de mediciones y gráficas a un archivo CSV con timestamp': {
        'es': 'Exporta datos de mediciones y gráficas a un archivo CSV con timestamp',
        'en': 'Export measurement and graph data to a timestamped CSV file'
    },
    'Exportar lógica': {'es': 'Exportar lógica', 'en': 'Export Logic'},
    'Exportar lógica a PDF': {'es': 'Exportar lógica a PDF', 'en': 'Export logic to PDF'},
    'Exportar lógica a Word': {'es': 'Exportar lógica a Word', 'en': 'Export logic to Word'},
    'Exportar lógica a TXT': {'es': 'Exportar lógica a TXT', 'en': 'Export logic to TXT'},
    'Exportar lógica a Excel': {'es': 'Exportar lógica a Excel', 'en': 'Export logic to Excel'},
    'Agregar etiqueta de texto al circuito': {
        'es': 'Agregar etiqueta de texto al circuito',
        'en': 'Add a text label to the circuit'
    },
    'Comparar curva simulada y medida en tiempo real': {
        'es': 'Comparar curva simulada y medida en tiempo real',
        'en': 'Compare simulated and real‑time measured curves'
    },
    'Guardar medición actual en la base de datos': {
        'es': 'Guardar medición actual en la base de datos',
        'en': 'Save the current measurement to the database'
    },
    'Mostrar historial de mediciones guardadas': {
        'es': 'Mostrar historial de mediciones guardadas',
        'en': 'Show history of saved measurements'
    },
    'Exporta el proyecto con layout, capas y netlist SPICE/Qucs': {
        'es': 'Exporta el proyecto con layout, capas y netlist SPICE/Qucs',
        'en': 'Export the project with layout, layers and SPICE/Qucs netlist'
    },
    'Exportar como imagen': {'es': 'Exportar como imagen', 'en': 'Export image'},
    'Eliminar': {'es': 'Eliminar', 'en': 'Delete'},
    'Cargar': {'es': 'Cargar', 'en': 'Load'},
    'Guardar': {'es': 'Guardar', 'en': 'Save'},
    'Restablecer': {'es': 'Restablecer', 'en': 'Reset'},

    'Fuente': {'es': 'Fuente', 'en': 'Font'},
    'Tamaño': {'es': 'Tamaño', 'en': 'Size'},
    'Negrita': {'es': 'Negrita', 'en': 'Bold'},
    'Cursiva': {'es': 'Cursiva', 'en': 'Italic'},
    'Subrayado': {'es': 'Subrayado', 'en': 'Underline'},
    'Aceptar': {'es': 'Aceptar', 'en': 'OK'},
    'Cancelar': {'es': 'Cancelar', 'en': 'Cancel'},
    'Nombre': {'es': 'Nombre', 'en': 'Name'},
    'Color etiqueta': {'es': 'Color etiqueta', 'en': 'Label color'},
    'Ver todo': {'es': 'Ver todo', 'en': 'View all'},
    'Establecer escala 1:1': {'es': 'Establecer escala 1:1', 'en': 'Set 1:1 scale'},
    'Simulando voltajes...': {'es': 'Simulando voltajes...', 'en': 'Simulating voltages...'},
    'Simulando corrientes...': {'es': 'Simulando corrientes...', 'en': 'Simulating currents...'},
    'Simulando circuito...': {'es': 'Simulando circuito...', 'en': 'Simulating circuit...'},
    'Simulación de voltajes completada': {'es': 'Simulación de voltajes completada', 'en': 'Voltage simulation completed'},
    'Simulación de corrientes completada': {'es': 'Simulación de corrientes completada', 'en': 'Current simulation completed'},
    'Simulación completa finalizada': {'es': 'Simulación completa finalizada', 'en': 'Complete simulation finished'},
    'Simulación inválida': {'es': 'Simulación inválida', 'en': 'Invalid simulation'},
    'No hay suficientes componentes conectados para simular.': {
        'es': 'No hay suficientes componentes conectados para simular.',
        'en': 'Not enough components connected to simulate.'
    },
    'Error de simulación': {'es': 'Error de simulación', 'en': 'Simulation error'},
    'No se encontró GND.\n\nAgrega un nodo de tierra (GND) para poder simular el circuito.': {
        'es': 'No se encontró GND.\n\nAgrega un nodo de tierra (GND) para poder simular el circuito.',
        'en': 'GND not found.\n\nAdd a ground node (GND) to simulate the circuit.'
    },
    'No se puede resolver el circuito: el sistema es singular. Verifica las conexiones.': {
        'es': 'No se puede resolver el circuito: el sistema es singular. Verifica las conexiones.',
        'en': 'The circuit cannot be solved: the system is singular. Check the connections.'
    },
    'Voltajes por componente:': {'es': 'Voltajes por componente:', 'en': 'Voltages per component:'},
    'Corrientes por componente:': {'es': 'Corrientes por componente:', 'en': 'Currents per component:'},
    'Resultados de Simulación': {'es': 'Resultados de Simulación', 'en': 'Simulation Results'},
    'Resultados de Corrientes': {'es': 'Resultados de Corrientes', 'en': 'Current Results'},
    'Acción restablecida (Ctrl+Z)': {
        'es': 'Acción restablecida (Ctrl+Z)',
        'en': 'Action restored (Ctrl+Z)'
    },
    'Circuito limpiado completamente.': {
        'es': 'Circuito limpiado completamente.',
        'en': 'Circuit completely cleared.'
    },
    'Circuito guardado': {'es': 'Circuito guardado', 'en': 'Circuit saved'},
    'Circuito cargado': {'es': 'Circuito cargado', 'en': 'Circuit loaded'},
}

TOOLTIPS_TRANSLATIONS = {
    'Haz clic aquí para iniciar una conexión entre terminales': {
        'es': 'Haz clic aquí para iniciar una conexión entre terminales',
        'en': 'Click here to start a connection between terminals'
    },
    'Ejecuta la simulación de voltajes en el circuito': {
        'es': 'Ejecuta la simulación de voltajes en el circuito',
        'en': 'Run the voltage simulation on the circuit'
    },
    'Ejecuta la simulación de corrientes en el circuito': {
        'es': 'Ejecuta la simulación de corrientes en el circuito',
        'en': 'Run the current simulation on the circuit'
    },
    'Simula voltajes y corrientes en una sola operación': {
        'es': 'Simula voltajes y corrientes en una sola operación',
        'en': 'Simulate voltages and currents in a single operation'
    },
    'Simula lógica digital y muestra la tabla de verdad del circuito': {
        'es': 'Simula lógica digital y muestra la tabla de verdad del circuito',
        'en': 'Simulates digital logic and displays the circuit truth table'
    },
    'Mostrar los atajos de teclado disponibles': {
        'es': 'Mostrar los atajos de teclado disponibles',
        'en': 'Show the available keyboard shortcuts'
    },
    'Agregar un nodo de tierra (GND) al circuito': {
        'es': 'Agregar un nodo de tierra (GND) al circuito',
        'en': 'Add a ground node (GND) to the circuit'
    },
    'Permite colocar una etiqueta de texto en el circuito': {
        'es': 'Permite colocar una etiqueta de texto en el circuito',
        'en': 'Allows placing a text label in the circuit'
    },
    'Iniciar una conexión entre terminales': {
        'es': 'Iniciar una conexión entre terminales',
        'en': 'Start a connection between terminals'
    },
    'Acercar la vista (zoom in)': {
        'es': 'Acercar la vista (zoom in)',
        'en': 'Zoom in'
    },
    'Alejar la vista (zoom out)': {
        'es': 'Alejar la vista (zoom out)',
        'en': 'Zoom out'
    },
    'Ajustar la vista para mostrar todos los elementos': {
        'es': 'Ajustar la vista para mostrar todos los elementos',
        'en': 'Adjust the view to show all elements'
    },
    'Abrir módulo VNA para mediciones de red': {
        'es': 'Abrir módulo VNA para mediciones de red',
        'en': 'Open VNA module for network measurements'
    },
    'Restablecer la vista a escala 1:1': {
        'es': 'Restablecer la vista a escala 1:1',
        'en': 'Reset the view to 1:1 scale'
    },
    'Ejecuta la inspección de errores de conexión': {
        'es': 'Ejecuta la inspección de errores de conexión',
        'en': 'Run the connection error inspection'
    },
    'Acercar vista': {
        'es': 'Acercar vista',
        'en': 'Zoom in'
    },
    'Alejar vista': {
        'es': 'Alejar vista',
        'en': 'Zoom out'
    },
    'Exporta datos de mediciones y gráficas a un archivo CSV con timestamp': {
        'es': 'Exporta datos de mediciones y gráficas a un archivo CSV con timestamp',
        'en': 'Export measurement and graph data to a timestamped CSV file'
    },
    'Mostrar y exportar la lista de materiales (BOM)': {
        'es': 'Mostrar y exportar la lista de materiales (BOM)',
        'en': 'Show and export the bill of materials (BOM)'
    },
    'Agregar etiqueta de texto al circuito': {
        'es': 'Agregar etiqueta de texto al circuito',
        'en': 'Add a text label to the circuit'
    },
    'Abrir módulo VNA para mediciones de red': {
        'es': 'Abrir módulo VNA para mediciones de red',
        'en': 'Open the VNA module for network measurements'
    },
    'Exporta el proyecto con layout, capas y netlist SPICE/Qucs': {
        'es': 'Exporta el proyecto con layout, capas y netlist SPICE/Qucs',
        'en': 'Export the project with layout, layers and SPICE/Qucs netlist'
    },
    'Comparar curva simulada y medida en tiempo real': {
        'es': 'Comparar curva simulada y medida en tiempo real',
        'en': 'Compare simulated and real‑time measured curves'
    },
    'Guardar medición actual en la base de datos': {
        'es': 'Guardar medición actual en la base de datos',
        'en': 'Save the current measurement to the database'
    },
    'Mostrar historial de mediciones guardadas': {
        'es': 'Mostrar historial de mediciones guardadas',
        'en': 'Show history of saved measurements'
    },
    'Exporta layout, capas, parámetros de simulación y netlist SPICE/Qucs': {
        'es': 'Exporta layout, capas, parámetros de simulación y netlist SPICE/Qucs',
        'en': 'Export layout, layers, simulation parameters and SPICE/Qucs netlist'
    },
    'Abre un proyecto extendido existente': {
        'es': 'Abre un proyecto extendido existente',
        'en': 'Open an existing extended project'
    },
    'Simula la distribución de voltajes en el circuito': {
        'es': 'Simula la distribución de voltajes en el circuito',
        'en': 'Simulate the distribution of voltages in the circuit'
    },
    'Simula la distribución de corrientes en el circuito': {
        'es': 'Simula la distribución de corrientes en el circuito',
        'en': 'Simulate the distribution of currents in the circuit'
    },
    'Simula tanto voltajes como corrientes en una sola operación': {
        'es': 'Simula tanto voltajes como corrientes en una sola operación',
        'en': 'Simulate both voltages and currents in a single operation'
    },
    'Realiza un análisis Monte Carlo de las tolerancias de los componentes': {
        'es': 'Realiza un análisis Monte Carlo de las tolerancias de los componentes',
        'en': 'Perform a Monte Carlo analysis of component tolerances'
    },
    'Genera un netlist con prefijos/modelos seleccionables': {
        'es': 'Genera un netlist con prefijos/modelos seleccionables',
        'en': 'Generate a netlist with selectable prefixes/models'
    },
    'Ejecuta el netlist en un motor SPICE/Qucs externo': {
        'es': 'Ejecuta el netlist en un motor SPICE/Qucs externo',
        'en': 'Run the netlist in an external SPICE/Qucs engine'
    },
    'Guardar Circuito': {
        'es': 'Guardar Circuito',
        'en': 'Save Circuit'
    },
    'Reestablecer': {
        'es': 'Reestablecer',
        'en': 'Undo'
    },
    'Rehacer': {
        'es': 'Rehacer',
        'en': 'Redo'
    },
    'Cargar': {
        'es': 'Cargar',
        'en': 'Load'
    },
    'Exportar Imagen': {
        'es': 'Exportar Imagen',
        'en': 'Export Image'
    },
    'Exportar PDF': {
        'es': 'Exportar PDF',
        'en': 'Export PDF'
    },
    'Reporte Word completo': {
        'es': 'Reporte Word completo',
        'en': 'Full Word Report'
    },
    'Exportar Resultados': {
        'es': 'Exportar Resultados',
        'en': 'Export Results'
    },
    'Eliminar': {
        'es': 'Eliminar',
        'en': 'Delete'
    },
    'Limpiar Todo': {
        'es': 'Limpiar Todo',
        'en': 'Clear All'
    },
    'Texto': {
        'es': 'Texto',
        'en': 'Text'
    },
    'Exportar CSV (Med./Gráf.)': {
        'es': 'Exportar CSV (Med./Gráf.)',
        'en': 'Export CSV (Meas./Graphs)'
    },
    'Lista de Materiales (BOM)': {
        'es': 'Lista de Materiales (BOM)',
        'en': 'Bill of Materials (BOM)'
    },
    'Acercar vista': {
        'es': 'Acercar vista',
        'en': 'Zoom in'
    },
    'Alejar vista': {
        'es': 'Alejar vista',
        'en': 'Zoom out'
    },
    'Inspector de Errores': {
        'es': 'Inspector de Errores',
        'en': 'Error Inspector'
    },
    'Agregar etiqueta de texto al circuito': {
        'es': 'Agregar etiqueta de texto al circuito',
        'en': 'Add a text label to the circuit'
    },
    'Atajos de Teclado': {
        'es': 'Atajos de Teclado',
        'en': 'Keyboard Shortcuts'
    }
}


def traducir(text: str) -> str:
    try:
        mapping = TRANSLATIONS.get(text)
        if mapping is None:
            for key, val in TRANSLATIONS.items():
                try:
                    if val.get('es') == text or val.get('en') == text:
                        mapping = val
                        break
                except Exception:
                    continue
        if mapping is None:
            return text
        return mapping.get(CURRENT_LANGUAGE, text)
    except Exception:
        return text


def traducir_descripcion_emergente(text: str) -> str:
    try:
        mapping = TOOLTIPS_TRANSLATIONS.get(text)
        if mapping is None:
            for key, val in TOOLTIPS_TRANSLATIONS.items():
                try:
                    if val.get('es') == text or val.get('en') == text:
                        mapping = val
                        break
                except Exception:
                    continue
        if mapping is None:
            return text
        return mapping.get(CURRENT_LANGUAGE, text)
    except Exception:
        return text


def traducir_mensaje_problema(msg: str) -> str:
    try:
        if CURRENT_LANGUAGE != 'en' or not isinstance(msg, str):
            return msg
        translations = {
            "Nodo flotante": "Floating node",
            "solo un terminal conectado": "only one terminal connected",
            "Hay": "There are",
            "fuentes de voltaje": "voltage sources",
            "en paralelo entre nodos": "in parallel between nodes",
            "Si sus valores son distintos, el sistema será singular": "If their values are different, the system will be singular",
            "Se encontraron": "Found",
            "subredes eléctricas desconectadas": "disconnected electrical subnetworks",
            "Algunos componentes no interactúan entre sí": "Some components do not interact with each other",
            "Fuentes de voltaje enfrentadas entre nodos": "Opposing voltage sources between nodes",
            "No se encontró un nodo de tierra (GND).": "No ground node (GND) was found.",
            "Agrega al menos un 'GND' conectado al circuito.": "Add at least one 'GND' connected to the circuit.",
            "Se detectaron múltiples nodos de tierra (GND).": "Multiple ground nodes (GND) were detected.",
            "Verifica que sólo exista una referencia común.": "Ensure that only a single common reference exists.",
            "No fue posible completar el chequeo eléctrico": "Unable to complete the electrical check",
        }
        translated = msg
        for es_text, en_text in translations.items():
            translated = translated.replace(es_text, en_text)
        return translated
    except Exception:
        return msg


def formatear_con_prefijo(valor, unidad="V"):
    abs_val = abs(valor)
    if abs_val == 0:
        return f"0.0000 {unidad}"
    elif abs_val < 1e-9:
        return f"{valor * 1e12:.4g} p{unidad}"
    elif abs_val < 1e-6:
        return f"{valor * 1e9:.4g} n{unidad}"
    elif abs_val < 1e-3:
        return f"{valor * 1e6:.4g} µ{unidad}"
    elif abs_val < 1:
        return f"{valor * 1e3:.4g} m{unidad}"
    elif abs_val < 1e3:
        return f"{valor:.4g} {unidad}"
    elif abs_val < 1e6:
        return f"{valor / 1e3:.4g} k{unidad}"
    elif abs_val < 1e9:
        return f"{valor / 1e6:.4g} M{unidad}"
    else:
        return f"{valor / 1e9:.4g} G{unidad}"
