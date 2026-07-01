"""
Configuración de constantes para instrumentos de medición.

Este módulo centraliza los valores de las resistencias internas de los
instrumentos virtuales utilizados en la simulación. Al separar estas
constantes en un único archivo, se garantiza la coherencia de los valores
utilizados a lo largo de la aplicación y se facilita su ajuste o
documentación.

- ``R_INT_V`` especifica la resistencia interna del voltímetro. Un valor
  suficientemente alto minimiza la perturbación del circuito durante las
  mediciones de tensión.
- ``R_INT_A`` especifica la resistencia interna del amperímetro. Un valor
  muy bajo limita la caída de tensión al medir corrientes.
- ``R_TEST_OHM`` se utiliza como resistencia de referencia para el
  ohmímetro durante el cálculo de resistencias entre nodos.

Todos los valores están en ohmios (Ω).
"""

# Resistencia interna del voltímetro (alta para minimizar la carga).
R_INT_V: float = 1e12

# Resistencia interna del amperímetro (baja para medir corriente sin
# introducir una caída de tensión apreciable). Debe ser lo más pequeña
# posible sin comprometer la estabilidad numérica del solver.
R_INT_A: float = 1e-9

# Resistencia de prueba utilizada por el ohmímetro. Este valor se
# emplea durante la simulación de medición de resistencia para
# determinar la corriente circulante al aplicar una fuente de tensión
# conocida. Un valor intermedio evita la degeneración a circuito abierto
# o cortocircuito ideal.
R_TEST_OHM: float = 1e3