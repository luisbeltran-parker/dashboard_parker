import numpy as np
from typing import List, Dict, Any

def congruencial_lineal(semilla: int, a: int, c: int, m: int, n: int) -> List[float]:
    """
    Generador congruencial lineal
    
    Args:
        semilla (int): Valor inicial X₀
        a (int): Multiplicador
        c (int): Incremento
        m (int): Módulo
        n (int): Cantidad de números a generar
    
    Returns:
        List[float]: Lista de números pseudoaleatorios en [0,1)
    """
    numeros = []
    x = semilla
    
    for _ in range(n):
        x = (a * x + c) % m
        numeros.append(x / m)  # Normalizar a [0,1)
    
    return numeros

def congruencial_multiplicativo(semilla: int, a: int, m: int, n: int) -> List[float]:
    """
    Generador congruencial multiplicativo
    
    Args:
        semilla (int): Valor inicial X₀
        a (int): Multiplicador
        m (int): Módulo
        n (int): Cantidad de números a generar
    
    Returns:
        List[float]: Lista de números pseudoaleatorios en [0,1)
    """
    numeros = []
    x = semilla
    
    for _ in range(n):
        x = (a * x) % m
        numeros.append(x / m)
    
    return numeros

def congruencial_cuadratico(semilla: int, a: int, b: int, c: int, m: int, n: int) -> List[float]:
    """
    Generador congruencial cuadrático
    
    Args:
        semilla (int): Valor inicial X₀
        a (int): Coeficiente cuadrático
        b (int): Coeficiente lineal
        c (int): Término constante
        m (int): Módulo
        n (int): Cantidad de números a generar
    
    Returns:
        List[float]: Lista de números pseudoaleatorios en [0,1)
    """
    numeros = []
    x = semilla
    
    for _ in range(n):
        x = (a * x**2 + b * x + c) % m
        numeros.append(x / m)
    
    return numeros

def mixed_congruential(semilla: int, a: int, c: int, m: int, n: int) -> List[float]:
    """
    Generador congruencial mixto (combinación lineal y multiplicativo)
    
    Args:
        semilla (int): Valor inicial X₀
        a (int): Multiplicador
        c (int): Incremento
        m (int): Módulo
        n (int): Cantidad de números a generar
    
    Returns:
        List[float]: Lista de números pseudoaleatorios en [0,1)
    """
    return congruencial_lineal(semilla, a, c, m, n)

def lehmer_generator(semilla: int, a: int, m: int, n: int) -> List[float]:
    """
    Generador de Lehmer (variante del congruencial multiplicativo)
    
    Args:
        semilla (int): Valor inicial X₀
        a (int): Multiplicador
        m (int): Módulo
        n (int): Cantidad de números a generar
    
    Returns:
        List[float]: Lista de números pseudoaleatorios en [0,1)
    """
    return congruencial_multiplicativo(semilla, a, m, n)

def generar_lote_congruencial(tipo: str, parametros: Dict[str, Any], n_lotes: int = 5) -> Dict[str, Any]:
    """
    Generar múltiples lotes de números para análisis
    
    Args:
        tipo (str): Tipo de generador ('lineal', 'multiplicativo', 'cuadratico')
        parametros (Dict): Parámetros del generador
        n_lotes (int): Número de lotes a generar
    
    Returns:
        Dict: Resultados con estadísticas por lote
    """
    resultados = {
        'lotes': [],
        'estadisticas_por_lote': [],
        'estadisticas_globales': {}
    }
    
    for i in range(n_lotes):
        if tipo == 'lineal':
            numeros = congruencial_lineal(
                parametros.get('semilla') + i,  # Cambiar semilla por lote
                parametros.get('a'),
                parametros.get('c'),
                parametros.get('m'),
                parametros.get('n', 100)
            )
        elif tipo == 'multiplicativo':
            numeros = congruencial_multiplicativo(
                parametros.get('semilla') + i,
                parametros.get('a'),
                parametros.get('m'),
                parametros.get('n', 100)
            )
        elif tipo == 'cuadratico':
            numeros = congruencial_cuadratico(
                parametros.get('semilla') + i,
                parametros.get('a'),
                parametros.get('b'),
                parametros.get('c_const'),
                parametros.get('m'),
                parametros.get('n', 100)
            )
        else:
            raise ValueError(f"Tipo de generador no válido: {tipo}")
        
        # Calcular estadísticas del lote
        stats = calcular_estadisticos_basicos(numeros)
        
        resultados['lotes'].append(numeros)
        resultados['estadisticas_por_lote'].append(stats)
    
    # Calcular estadísticas globales
    todos_numeros = [num for lote in resultados['lotes'] for num in lote]
    resultados['estadisticas_globales'] = calcular_estadisticos_basicos(todos_numeros)
    
    return resultados

def calcular_estadisticos_basicos(numeros: List[float]) -> Dict[str, float]:
    """
    Calcular estadísticas básicas para un conjunto de números
    
    Args:
        numeros (List[float]): Lista de números
    
    Returns:
        Dict: Estadísticas calculadas
    """
    if not numeros:
        return {}
    
    array_np = np.array(numeros)
    
    return {
        'media': float(np.mean(array_np)),
        'mediana': float(np.median(array_np)),
        'desviacion_estandar': float(np.std(array_np)),
        'varianza': float(np.var(array_np)),
        'minimo': float(np.min(array_np)),
        'maximo': float(np.max(array_np)),
        'rango': float(np.max(array_np) - np.min(array_np)),
        'primer_cuartil': float(np.percentile(array_np, 25)),
        'tercer_cuartil': float(np.percentile(array_np, 75))
    }

def prueba_uniformidad(numeros: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    """
    Prueba de uniformidad usando prueba de Kolmogorov-Smirnov
    
    Args:
        numeros (List[float]): Lista de números a probar
        alpha (float): Nivel de significancia
    
    Returns:
        Dict: Resultados de la prueba
    """
    from scipy import stats
    
    try:
        # Prueba de Kolmogorov-Smirnov
        d_stat, p_value = stats.kstest(numeros, 'uniform')
        
        return {
            'estadistico_d': d_stat,
            'p_valor': p_value,
            'uniforme': p_value > alpha,
            'nivel_significancia': alpha,
            'interpretacion': f"Los números son {'uniformemente distribuidos' if p_value > alpha else 'no uniformemente distribuidos'} (p={p_value:.4f})"
        }
    except ImportError:
        # Fallback si scipy no está disponible
        return {
            'error': 'Scipy no disponible para pruebas estadísticas',
            'interpretacion': 'No se pudo realizar la prueba de uniformidad'
        }