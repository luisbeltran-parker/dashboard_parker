import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import re

def validar_parametros_congruencial(tipo: str, parametros: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validar parámetros para generadores congruenciales
    
    Args:
        tipo (str): Tipo de generador
        parametros (Dict): Parámetros a validar
    
    Returns:
        Tuple: (es_valido, lista_errores)
    """
    errores = []
    
    # Validaciones comunes
    semilla = parametros.get('semilla')
    if semilla is None or semilla <= 0:
        errores.append("La semilla debe ser un número positivo")
    
    n = parametros.get('cantidad', parametros.get('n', 1))
    if n < 10 or n > 100000:
        errores.append("La cantidad de números debe estar entre 10 y 100,000")
    
    m = parametros.get('m')
    if m is None or m <= 0:
        errores.append("El módulo m debe ser un número positivo")
    
    # Validaciones específicas por tipo
    if tipo == 'lineal':
        a = parametros.get('a')
        c = parametros.get('c')
        
        if a is None:
            errores.append("El multiplicador 'a' es requerido")
        elif a <= 0:
            errores.append("El multiplicador 'a' debe ser positivo")
        
        if c is None:
            errores.append("El incremento 'c' es requerido")
        elif c < 0:
            errores.append("El incremento 'c' debe ser no negativo")
        
        # Validar que m sea suficientemente grande
        if m and semilla and m <= semilla:
            errores.append("El módulo m debe ser mayor que la semilla")
    
    elif tipo == 'multiplicativo':
        a = parametros.get('a')
        
        if a is None:
            errores.append("El multiplicador 'a' es requerido")
        elif a <= 0:
            errores.append("El multiplicador 'a' debe ser positivo")
        
        # Validaciones para generador multiplicativo
        if m and semilla and m <= semilla:
            errores.append("El módulo m debe ser mayor que la semilla")
    
    elif tipo == 'cuadratico':
        a = parametros.get('a')
        b = parametros.get('b')
        c_const = parametros.get('c_const')
        
        if a is None or a == 0:
            errores.append("El coeficiente cuadrático 'a' es requerido y no puede ser cero")
        
        if b is None:
            errores.append("El coeficiente lineal 'b' es requerido")
        
        if c_const is None:
            errores.append("El término constante 'c' es requerido")
    
    else:
        errores.append(f"Tipo de generador no válido: {tipo}")
    
    return len(errores) == 0, errores

def validar_archivo_subido(archivo, extensiones_permitidas: List[str] = None) -> Tuple[bool, str]:
    """
    Validar archivo subido por el usuario
    
    Args:
        archivo: Objeto archivo de Flask
        extensiones_permitidas: Lista de extensiones permitidas
    
    Returns:
        Tuple: (es_valido, mensaje_error)
    """
    if extensiones_permitidas is None:
        extensiones_permitidas = ['.csv', '.xlsx', '.xls', '.txt', '.json']
    
    if not archivo or archivo.filename == '':
        return False, "No se seleccionó ningún archivo"
    
    # Validar extensión
    if not any(archivo.filename.lower().endswith(ext) for ext in extensiones_permitidas):
        return False, f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(extensiones_permitidas)}"
    
    # Validar tamaño (16MB máximo)
    if len(archivo.read()) > 16 * 1024 * 1024:
        return False, "El archivo es demasiado grande (máximo 16MB)"
    
    # Regresar al inicio del archivo
    archivo.seek(0)
    
    return True, "Archivo válido"

def validar_dataframe(df: pd.DataFrame, columnas_requeridas: List[str] = None) -> Tuple[bool, List[str]]:
    """
    Validar estructura de DataFrame
    
    Args:
        df: DataFrame a validar
        columnas_requeridas: Columnas que deben estar presentes
    
    Returns:
        Tuple: (es_valido, lista_errores)
    """
    errores = []
    
    if df.empty:
        errores.append("El DataFrame está vacío")
        return False, errores
    
    # Validar columnas requeridas
    if columnas_requeridas:
        for col in columnas_requeridas:
            if col not in df.columns:
                errores.append(f"Columna requerida no encontrada: {col}")
    
    # Validar que haya datos numéricos
    if df.select_dtypes(include=[np.number]).empty:
        errores.append("No se encontraron columnas numéricas en el archivo")
    
    # Validar valores nulos
    if df.isnull().any().any():
        columnas_nulas = df.columns[df.isnull().any()].tolist()
        errores.append(f"Se encontraron valores nulos en las columnas: {', '.join(columnas_nulas)}")
    
    return len(errores) == 0, errores

def analizar_datos_archivo(datos) -> Dict[str, Any]:
    """
    Analizar datos del archivo subido
    
    Args:
        datos: DataFrame o datos del archivo
    
    Returns:
        Dict: Análisis de los datos
    """
    if isinstance(datos, pd.DataFrame):
        df = datos
    else:
        # Convertir a DataFrame si es necesario
        df = pd.DataFrame(datos)
    
    analisis = {
        'filas': len(df),
        'columnas': list(df.columns),
        'tipos_datos': df.dtypes.astype(str).to_dict(),
        'valores_faltantes': df.isnull().sum().to_dict(),
        'memoria_usada': df.memory_usage(deep=True).sum(),
        'estadisticas': {}
    }
    
    # Estadísticas para columnas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    if not columnas_numericas.empty:
        analisis['estadisticas'] = df[columnas_numericas].describe().to_dict()
    
    # Información de valores únicos
    analisis['valores_unicos'] = df.nunique().to_dict()
    
    return analisis

def sanitizar_nombre_archivo(nombre: str) -> str:
    """
    Sanitizar nombre de archivo para seguridad
    
    Args:
        nombre (str): Nombre original del archivo
    
    Returns:
        str: Nombre sanitizado
    """
    # Remover caracteres peligrosos
    nombre_seguro = re.sub(r'[^\w\-_.]', '', nombre)
    
    # Limitar longitud
    if len(nombre_seguro) > 255:
        nombre_seguro = nombre_seguro[:255]
    
    return nombre_seguro

def validar_rango_numerico(valor: Any, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
    """
    Validar que un valor esté en un rango específico
    
    Args:
        valor: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
    
    Returns:
        Tuple: (es_valido, mensaje_error)
    """
    try:
        num = float(valor)
        
        if min_val is not None and num < min_val:
            return False, f"El valor debe ser mayor o igual a {min_val}"
        
        if max_val is not None and num > max_val:
            return False, f"El valor debe ser menor o igual a {max_val}"
        
        return True, "Valor válido"
    
    except (ValueError, TypeError):
        return False, "El valor debe ser un número"

def generar_reporte_validacion(errores: List[str], advertencias: List[str] = None) -> Dict[str, Any]:
    """
    Generar reporte de validación estructurado
    
    Args:
        errores: Lista de errores
        advertencias: Lista de advertencias
    
    Returns:
        Dict: Reporte de validación
    """
    if advertencias is None:
        advertencias = []
    
    return {
        'valido': len(errores) == 0,
        'total_errores': len(errores),
        'total_advertencias': len(advertencias),
        'errores': errores,
        'advertencias': advertencias,
        'resumen': f"Validación {'exitosa' if len(errores) == 0 else 'fallida'} - {len(errores)} errores, {len(advertencias)} advertencias"
    }
