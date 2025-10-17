# Utils package initialization
from .congruenciales import *
from .estadisticos import *
from .validaciones import *

__all__ = [
    'congruencial_lineal',
    'congruencial_multiplicativo', 
    'congruencial_cuadratico',
    'calcular_estadisticos',
    'validar_parametros_congruencial',
    'generar_histograma'
]