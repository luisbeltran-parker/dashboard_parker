import os
from dotenv import load_dotenv

# Cargar variables del archivo .env PRIMERO
load_dotenv()

# ESTABLECER MODO DESARROLLO POR DEFECTO
os.environ.setdefault('FLASK_ENV', 'development')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
import json

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file

# Importar configuración
from config import config

app = Flask(__name__)

# Configurar la aplicación según el entorno
env = os.environ.get('FLASK_ENV', 'development')
print(f"🔧 Ejecutando en modo: {env}")

app.config.from_object(config[env])

# Importar utils después de configurar Flask
from utils.congruenciales import *
from utils.estadisticos import *
from utils.validaciones import *

# Variables globales para almacenar resultados
resultados_simulacion = {}

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/metodos-congruenciales', methods=['GET', 'POST'])
def metodos_congruenciales():
    """Página para métodos congruenciales con upload de archivos"""
    
    if request.method == 'POST':
        try:
            # Procesar formulario de parámetros
            if 'calcular' in request.form:
                metodo = request.form.get('metodo')
                semilla = int(request.form.get('semilla'))
                cantidad = int(request.form.get('cantidad'))
                
                if metodo == 'lineal':
                    a = int(request.form.get('a'))
                    c = int(request.form.get('c'))
                    m = int(request.form.get('m'))
                    numeros = congruencial_lineal(semilla, a, c, m, cantidad)
                    
                elif metodo == 'multiplicativo':
                    a = int(request.form.get('a'))
                    m = int(request.form.get('m'))
                    numeros = congruencial_multiplicativo(semilla, a, m, cantidad)
                    
                elif metodo == 'cuadratico':
                    a = int(request.form.get('a'))
                    b = int(request.form.get('b'))
                    c_const = int(request.form.get('c_const'))
                    m = int(request.form.get('m'))
                    numeros = congruencial_cuadratico(semilla, a, b, c_const, m, cantidad)
                
                # Generar gráficos
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Histograma
                ax1.hist(numeros, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                ax1.set_title('Distribución de Números Generados')
                ax1.set_xlabel('Valor')
                ax1.set_ylabel('Frecuencia')
                
                # Secuencia de números
                ax2.plot(range(len(numeros)), numeros, 'o-', alpha=0.7)
                ax2.set_title('Secuencia de Números Generados')
                ax2.set_xlabel('Iteración')
                ax2.set_ylabel('Valor')
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                # Convertir gráfico a base64
                img = io.BytesIO()
                plt.savefig(img, format='png', dpi=150)
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                plt.close()
                
                # Estadísticas descriptivas
                stats = {
                    'media': np.mean(numeros),
                    'desviacion': np.std(numeros),
                    'minimo': np.min(numeros),
                    'maximo': np.max(numeros),
                    'varianza': np.var(numeros)
                }
                
                return render_template('metodos_congruenciales.html',
                                    numeros=numeros,
                                    plot_url=plot_url,
                                    stats=stats,
                                    metodo=metodo)
            
            # Procesar archivo subido
            elif 'subir_archivo' in request.files:
                archivo = request.files['subir_archivo']
                if archivo and archivo.filename != '':
                    # Validar extensión
                    if not archivo.filename.endswith(('.csv', '.xlsx', '.txt')):
                        flash('Formato de archivo no válido. Use CSV, Excel o TXT.', 'error')
                        return redirect(url_for('metodos_congruenciales'))
                    
                    # Guardar archivo
                    filename = f"congruencial_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(filepath)
                    
                    # Procesar según extensión
                    try:
                        if filename.endswith('.csv'):
                            datos = pd.read_csv(filepath)
                        elif filename.endswith('.xlsx'):
                            datos = pd.read_excel(filepath)
                        else:
                            datos = pd.read_csv(filepath, delimiter='\t')
                        
                        # Analizar datos del archivo
                        analisis_archivo = analizar_datos_archivo(datos)
                        
                        flash('Archivo procesado correctamente', 'success')
                        return render_template('metodos_congruenciales.html',
                                            datos_archivo=datos.head(10).to_dict('records'),
                                            analisis_archivo=analisis_archivo,
                                            filename=filename)
                    
                    except Exception as e:
                        flash(f'Error al leer el archivo: {str(e)}', 'error')
                        return redirect(url_for('metodos_congruenciales'))
        
        except Exception as e:
            flash(f'Error en el procesamiento: {str(e)}', 'error')
            return redirect(url_for('metodos_congruenciales'))
    
    return render_template('metodos_congruenciales.html')

@app.route('/procesar-archivo-congruencial', methods=['POST'])
def procesar_archivo_congruencial():
    """Procesar archivo subido para métodos congruenciales"""
    try:
        filename = request.form.get('filename')
        metodo = request.form.get('metodo_archivo')
        
        if not filename:
            flash('No se especificó archivo', 'error')
            return redirect(url_for('metodos_congruenciales'))
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Cargar y procesar datos
        if filename.endswith('.csv'):
            datos = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            datos = pd.read_excel(filepath)
        else:
            datos = pd.read_csv(filepath, delimiter='\t')
        
        # Aquí implementarías la lógica específica para procesar
        # los datos del archivo con el método congruencial seleccionado
        resultados = procesar_datos_congruencial(datos, metodo)
        
        # Guardar resultados globalmente
        resultados_simulacion['congruencial'] = resultados
        
        return render_template('resultados.html',
                             resultados=resultados,
                             tipo='congruencial',
                             metodo=metodo)
                             
    except Exception as e:
        flash(f'Error al procesar archivo: {str(e)}', 'error')
        return redirect(url_for('metodos_congruenciales'))

@app.route('/monte-carlo')
def monte_carlo():
    """Métodos de Monte Carlo"""
    return render_template('monte_carlo.html')

@app.route('/transformada-inversa')
def transformada_inversa():
    """Método de transformada inversa"""
    return render_template('transformada_inversa.html')

@app.route('/aceptacion-rechazo')
def aceptacion_rechazo():
    """Método de aceptación y rechazo"""
    return render_template('aceptacion_rechazo.html')

@app.route('/box-muller')
def box_muller():
    """Transformada de Box-Muller"""
    # Por ahora redirigimos a transformada inversa
    return redirect(url_for('transformada_inversa'))

@app.route('/subir-trabajo', methods=['GET', 'POST'])
def subir_trabajo():
    """Página para subir trabajos completos"""
    
    if request.method == 'POST':
        try:
            archivo = request.files['archivo_trabajo']
            descripcion = request.form.get('descripcion')
            tipo_trabajo = request.form.get('tipo_trabajo')
            
            if archivo and archivo.filename != '':
                # Validar tipo de archivo
                extensiones_permitidas = ['.py', '.ipynb', '.pdf', '.docx', '.zip']
                if not any(archivo.filename.endswith(ext) for ext in extensiones_permitidas):
                    flash('Tipo de archivo no permitido', 'error')
                    return redirect(url_for('subir_trabajo'))
                
                # Guardar archivo
                filename = f"trabajo_{tipo_trabajo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                archivo.save(filepath)
                
                # Registrar en base de datos (aquí podrías usar SQLite)
                registro = {
                    'filename': filename,
                    'descripcion': descripcion,
                    'tipo_trabajo': tipo_trabajo,
                    'fecha_subida': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'tamaño': os.path.getsize(filepath)
                }
                
                flash('Trabajo subido exitosamente', 'success')
                return render_template('upload.html', registro=registro)
        
        except Exception as e:
            flash(f'Error al subir archivo: {str(e)}', 'error')
    
    return render_template('upload.html')

@app.route('/descargar-plantilla/<tipo>')
def descargar_plantilla(tipo):
    """Descargar plantillas para trabajos"""
    plantillas = {
        'congruencial': 'plantilla_congruencial.py',
        'montecarlo': 'plantilla_monte_carlo.py',
        'transformada': 'plantilla_transformada.py'
    }
    
    if tipo in plantillas:
        # Crear contenido de plantilla básica
        if tipo == 'congruencial':
            contenido = '''# Plantilla para Métodos Congruenciales

def congruencial_lineal(semilla, a, c, m, n):
    """
    Generador congruencial lineal
    
    Args:
        semilla (int): Valor inicial
        a (int): Multiplicador
        c (int): Incremento
        m (int): Módulo
        n (int): Cantidad de números
    
    Returns:
        list: Números pseudoaleatorios
    """
    numeros = []
    x = semilla
    
    for _ in range(n):
        x = (a * x + c) % m
        numeros.append(x / m)  # Normalizar a [0,1)
    
    return numeros

# Ejemplo de uso
if __name__ == "__main__":
    # Parámetros ejemplo
    semilla = 1
    a = 5
    c = 3
    m = 16
    n = 20
    
    numeros = congruencial_lineal(semilla, a, c, m, n)
    print("Números generados:", numeros)
'''
        elif tipo == 'montecarlo':
            contenido = '''# Plantilla para Método Monte Carlo

import random
import math

def monte_carlo_pi(n_puntos):
    """
    Estimación de π usando Monte Carlo
    
    Args:
        n_puntos (int): Número de puntos a generar
    
    Returns:
        float: Estimación de π
    """
    dentro_circulo = 0
    
    for _ in range(n_puntos):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        
        if x**2 + y**2 <= 1:
            dentro_circulo += 1
    
    return 4 * dentro_circulo / n_puntos

# Ejemplo de uso
if __name__ == "__main__":
    n_puntos = 10000
    pi_estimado = monte_carlo_pi(n_puntos)
    print(f"π estimado con {n_puntos} puntos: {pi_estimado}")
    print(f"Error: {abs(math.pi - pi_estimado)}")
'''
        else:  # transformada
            contenido = '''# Plantilla para Transformada Inversa

import math
import random

def transformada_inversa_exponencial(lambda_param, n):
    """
    Generar variables exponenciales usando transformada inversa
    
    Args:
        lambda_param (float): Parámetro de tasa
        n (int): Número de variables a generar
    
    Returns:
        list: Variables exponenciales
    """
    variables = []
    
    for _ in range(n):
        u = random.random()
        x = -math.log(1 - u) / lambda_param
        variables.append(x)
    
    return variables

# Ejemplo de uso
if __name__ == "__main__":
    lambda_param = 0.5
    n = 20
    variables = transformada_inversa_exponencial(lambda_param, n)
    print("Variables exponenciales:", variables)
'''
        
        # Crear respuesta de descarga
        output = io.BytesIO()
        output.write(contenido.encode('utf-8'))
        output.seek(0)
        
        return send_file(output,
                       mimetype='text/python',
                       as_attachment=True,
                       download_name=f'plantilla_{tipo}.py')
    
    flash('Plantilla no encontrada', 'error')
    return redirect(url_for('index'))

@app.route('/api/generar-numeros', methods=['POST'])
def api_generar_numeros():
    """API para generar números aleatorios"""
    try:
        data = request.get_json()
        metodo = data.get('metodo')
        parametros = data.get('parametros', {})
        
        if metodo == 'lineal':
            numeros = congruencial_lineal(
                parametros.get('semilla', 1),
                parametros.get('a', 5),
                parametros.get('c', 3),
                parametros.get('m', 16),
                parametros.get('n', 10)
            )
        elif metodo == 'multiplicativo':
            numeros = congruencial_multiplicativo(
                parametros.get('semilla', 1),
                parametros.get('a', 5),
                parametros.get('m', 16),
                parametros.get('n', 10)
            )
        else:
            return jsonify({'error': 'Método no válido'}), 400
        
        return jsonify({
            'numeros': numeros,
            'estadisticas': {
                'media': float(np.mean(numeros)),
                'desviacion': float(np.std(numeros)),
                'min': float(np.min(numeros)),
                'max': float(np.max(numeros))
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/exportar-resultados/<tipo>')
def exportar_resultados(tipo):
    """Exportar resultados a CSV"""
    try:
        if tipo in resultados_simulacion:
            resultados = resultados_simulacion[tipo]
            
            # Crear DataFrame con datos de ejemplo
            datos_ejemplo = [
                {'iteracion': i, 'valor': np.random.random(), 'metodo': tipo}
                for i in range(100)
            ]
            df = pd.DataFrame(datos_ejemplo)
            
            # Generar archivo
            output = io.BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            filename = f"resultados_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return send_file(output,
                           mimetype='text/csv',
                           as_attachment=True,
                           download_name=filename)
        else:
            flash('No hay resultados para exportar', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/documentacion')
def documentacion():
    """Documentación de los algoritmos"""
    algoritmos = {
        'congruencial_lineal': {
            'descripcion': 'Generador de números pseudoaleatorios usando el método congruencial lineal',
            'formula': 'Xₙ₊₁ = (a * Xₙ + c) mod m',
            'parametros': ['semilla', 'a', 'c', 'm'],
            'aplicacion': 'Simulación básica, juegos, pruebas iniciales'
        },
        'congruencial_multiplicativo': {
            'descripcion': 'Versión del congruencial sin constante aditiva',
            'formula': 'Xₙ₊₁ = (a * Xₙ) mod m',
            'parametros': ['semilla', 'a', 'm'],
            'aplicacion': 'Cuando se requiere mayor eficiencia'
        },
        'monte_carlo': {
            'descripcion': 'Método estadístico para aproximar valores mediante simulación',
            'aplicacion': 'Integración numérica, finanzas, física'
        },
        'transformada_inversa': {
            'descripcion': 'Método para generar variables aleatorias de distribuciones continuas',
            'aplicacion': 'Simulación de procesos, modelado estadístico'
        }
    }
    
    return render_template('documentacion.html', algoritmos=algoritmos)

@app.route('/acerca')
def acerca():
    """Página acerca de"""
    return render_template('acerca.html')

# Funciones auxiliares
def analizar_datos_archivo(datos):
    """Analizar datos del archivo subido"""
    if isinstance(datos, pd.DataFrame):
        df = datos
    else:
        df = pd.DataFrame(datos)
    
    analisis = {
        'filas': len(df),
        'columnas': list(df.columns),
        'tipos_datos': df.dtypes.astype(str).to_dict(),
        'valores_faltantes': df.isnull().sum().to_dict(),
        'memoria_usada': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
    }
    
    # Estadísticas para columnas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    if not columnas_numericas.empty:
        analisis['estadisticas'] = df[columnas_numericas].describe().to_dict()
    
    return analisis

def procesar_datos_congruencial(datos, metodo):
    """Procesar datos para métodos congruenciales"""
    # Implementar lógica específica según el método y datos
    resultados = {
        'datos_originales': datos.head().to_dict('records') if isinstance(datos, pd.DataFrame) else datos[:5],
        'metodo_aplicado': metodo,
        'resultados': 'Procesamiento completado exitosamente',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estadisticas': {
            'total_registros': len(datos) if hasattr(datos, '__len__') else 'N/A',
            'columnas_procesadas': list(datos.columns) if isinstance(datos, pd.DataFrame) else ['columna_1']
        }
    }
    return resultados

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard de Estadística Computacional...")
    print(f"📊 Modo: {env}")
    print(f"🔧 Debug: {app.config['DEBUG']}")
    print(f"🌐 URL: http://localhost:5000")
    
    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)