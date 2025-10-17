import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
import math

def calcular_estadisticos(numeros: List[float]) -> Dict[str, float]:
    """
    Calcular estadísticas descriptivas completas
    
    Args:
        numeros (List[float]): Lista de números
    
    Returns:
        Dict: Estadísticas calculadas
    """
    if not numeros:
        return {}
    
    array_np = np.array(numeros)
    n = len(numeros)
    
    # Estadísticas básicas
    media = np.mean(array_np)
    mediana = np.median(array_np)
    moda = calcular_moda(numeros)
    desviacion = np.std(array_np)
    varianza = np.var(array_np)
    
    # Medidas de posición
    minimo = np.min(array_np)
    maximo = np.max(array_np)
    rango = maximo - minimo
    q1 = np.percentile(array_np, 25)
    q3 = np.percentile(array_np, 75)
    iqr = q3 - q1
    
    # Medidas de forma
    asimetria = calcular_asimetria(array_np)
    curtosis = calcular_curtosis(array_np)
    
    return {
        'n': n,
        'media': float(media),
        'mediana': float(mediana),
        'moda': moda,
        'desviacion_estandar': float(desviacion),
        'varianza': float(varianza),
        'minimo': float(minimo),
        'maximo': float(maximo),
        'rango': float(rango),
        'primer_cuartil': float(q1),
        'tercer_cuartil': float(q3),
        'rango_intercuartil': float(iqr),
        'asimetria': float(asimetria),
        'curtosis': float(curtosis),
        'coeficiente_variacion': float(desviacion / media) if media != 0 else 0
    }

def calcular_moda(numeros: List[float]) -> List[float]:
    """
    Calcular la moda de una lista de números
    
    Args:
        numeros (List[float]): Lista de números
    
    Returns:
        List[float]: Valores de la moda
    """
    from collections import Counter
    contador = Counter(numeros)
    max_frecuencia = max(contador.values())
    modas = [num for num, freq in contador.items() if freq == max_frecuencia]
    return modas

def calcular_asimetria(numeros: np.ndarray) -> float:
    """
    Calcular coeficiente de asimetría de Fisher
    
    Args:
        numeros (np.ndarray): Array de números
    
    Returns:
        float: Coeficiente de asimetría
    """
    n = len(numeros)
    if n < 3:
        return 0.0
    
    media = np.mean(numeros)
    desviacion = np.std(numeros)
    
    if desviacion == 0:
        return 0.0
    
    suma_cubos = np.sum((numeros - media) ** 3)
    asimetria = (suma_cubos / n) / (desviacion ** 3)
    
    return asimetria

def calcular_curtosis(numeros: np.ndarray) -> float:
    """
    Calcular coeficiente de curtosis
    
    Args:
        numeros (np.ndarray): Array de números
    
    Returns:
        float: Coeficiente de curtosis
    """
    n = len(numeros)
    if n < 4:
        return 0.0
    
    media = np.mean(numeros)
    desviacion = np.std(numeros)
    
    if desviacion == 0:
        return 0.0
    
    suma_cuartos = np.sum((numeros - media) ** 4)
    curtosis = (suma_cuartos / n) / (desviacion ** 4) - 3  # Excess kurtosis
    
    return curtosis

def generar_histograma(numeros: List[float], bins: int = 10) -> Dict[str, Any]:
    """
    Generar datos para histograma
    
    Args:
        numeros (List[float]): Lista de números
        bins (int): Número de intervalos
    
    Returns:
        Dict: Datos del histograma
    """
    if not numeros:
        return {}
    
    hist, edges = np.histogram(numeros, bins=bins)
    
    return {
        'frecuencias': hist.tolist(),
        'bins_edges': edges.tolist(),
        'bins_centers': [(edges[i] + edges[i+1]) / 2 for i in range(len(edges)-1)],
        'bins_ranges': [f"{edges[i]:.3f}-{edges[i+1]:.3f}" for i in range(len(edges)-1)],
        'ancho_bin': edges[1] - edges[0]
    }

def prueba_bondad_ajuste(numeros: List[float], distribucion: str = 'uniforme') -> Dict[str, Any]:
    """
    Prueba de bondad de ajuste chi-cuadrado
    
    Args:
        numeros (List[float]): Lista de números
        distribucion (str): Distribución a probar ('uniforme', 'normal')
    
    Returns:
        Dict: Resultados de la prueba
    """
    from scipy import stats
    
    try:
        if distribucion == 'uniforme':
            # Prueba chi-cuadrado para uniformidad
            frec_obs, _ = np.histogram(numeros, bins=10)
            frec_esp = np.full_like(frec_obs, len(numeros) / 10)
            
            chi2, p_value = stats.chisquare(frec_obs, frec_esp)
            
            return {
                'estadistico_chi2': chi2,
                'p_valor': p_value,
                'distribucion': distribucion,
                'ajuste_adecuado': p_value > 0.05,
                'interpretacion': f"Los números se ajustan {'adecuadamente' if p_value > 0.05 else 'inadecuadamente'} a una distribución uniforme (p={p_value:.4f})"
            }
            
        elif distribucion == 'normal':
            # Prueba de normalidad Shapiro-Wilk
            stat, p_value = stats.shapiro(numeros)
            
            return {
                'estadistico_w': stat,
                'p_valor': p_value,
                'distribucion': distribucion,
                'ajuste_adecuado': p_value > 0.05,
                'interpretacion': f"Los números se ajustan {'adecuadamente' if p_value > 0.05 else 'inadecuadamente'} a una distribución normal (p={p_value:.4f})"
            }
            
    except ImportError:
        return {
            'error': 'Scipy no disponible para pruebas estadísticas',
            'interpretacion': 'No se pudo realizar la prueba de bondad de ajuste'
        }

def correlacion_serial(numeros: List[float], lag: int = 1) -> float:
    """
    Calcular correlación serial para un lag específico
    
    Args:
        numeros (List[float]): Lista de números
        lag (int): Lag para la correlación
    
    Returns:
        float: Coeficiente de correlación serial
    """
    if len(numeros) <= lag:
        return 0.0
    
    x = np.array(numeros[:-lag])
    y = np.array(numeros[lag:])
    
    return float(np.corrcoef(x, y)[0, 1])

def prueba_aleatoriedad(numeros: List[float]) -> Dict[str, Any]:
    """
    Prueba de aleatoriedad usando prueba de rachas
    
    Args:
        numeros (List[float]): Lista de números
    
    Returns:
        Dict: Resultados de la prueba
    """
    try:
        from statsmodels.sandbox.stats.runs import runstest_1samp
        
        # Convertir a secuencia de signos (arriba/abajo de la mediana)
        mediana = np.median(numeros)
        secuencia = [1 if x > mediana else 0 for x in numeros]
        
        # Contar rachas
        rachas = 1
        for i in range(1, len(secuencia)):
            if secuencia[i] != secuencia[i-1]:
                rachas += 1
        
        # Estadístico de rachas
        n1 = sum(secuencia)  # Número de unos
        n2 = len(secuencia) - n1  # Número de ceros
        
        media_rachas = (2 * n1 * n2) / (n1 + n2) + 1
        varianza_rachas = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
        
        if varianza_rachas == 0:
            z = 0
        else:
            z = (rachas - media_rachas) / math.sqrt(varianza_rachas)
        
        # Valor p aproximado (dos colas)
        from scipy import stats
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        return {
            'numero_rachas': rachas,
            'estadistico_z': z,
            'p_valor': p_value,
            'aleatorio': p_value > 0.05,
            'interpretacion': f"La secuencia es {'aleatoria' if p_value > 0.05 else 'no aleatoria'} (p={p_value:.4f})"
        }
        
    except ImportError:
        return {
            'error': 'Statsmodels no disponible para prueba de rachas',
            'interpretacion': 'No se pudo realizar la prueba de aleatoriedad'
        }