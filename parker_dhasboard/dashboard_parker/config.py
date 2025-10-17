import os
from datetime import timedelta

class Config:
    """Configuración base para la aplicación Flask"""
    
    # Clave secreta para seguridad de sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_secreta_muy_segura_para_estadistica_2024'
    
    # Configuración de uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {
        # Archivos de datos
        'csv', 'xlsx', 'xls', 'txt', 'json',
        # Archivos de código
        'py', 'ipynb', 'r', 'm',
        # Documentos
        'pdf', 'doc', 'docx', 'ppt', 'pptx',
        # Comprimidos
        'zip', 'rar', '7z'
    }
    
    # Configuración de la base de datos (SQLite por defecto)
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'dashboard_estadistica.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Configuración de algoritmos
    ALGORITMOS_CONFIG = {
        'congruencial_lineal': {
            'parametros_default': {
                'semilla': 1,
                'a': 1664525,
                'c': 1013904223,
                'm': 2**32
            },
            'descripcion': 'Generador congruencial lineal estándar'
        },
        'congruencial_multiplicativo': {
            'parametros_default': {
                'semilla': 1,
                'a': 48271,
                'm': 2**31 - 1
            },
            'descripcion': 'Generador congruencial multiplicativo'
        },
        'congruencial_cuadratico': {
            'parametros_default': {
                'semilla': 1,
                'a': 1,
                'b': 1,
                'c_const': 1,
                'm': 2**16
            },
            'descripcion': 'Generador congruencial cuadrático'
        },
        'monte_carlo': {
            'iteraciones_default': 10000,
            'nivel_confianza': 0.95
        },
        'transformada_inversa': {
            'distribuciones': ['exponencial', 'normal', 'uniforme', 'weibull']
        }
    }
    
    # Configuración de visualización
    VISUALIZATION_CONFIG = {
        'color_primario': '#2c3e50',
        'color_secundario': '#3498db',
        'color_exito': '#27ae60',
        'color_peligro': '#e74c3c',
        'color_advertencia': '#f39c12',
        'estilo_graficos': 'seaborn',
        'tamanio_fuente': 12,
        'dpi_graficos': 150,
        'formato_imagen': 'png'
    }
    
    # Límites de seguridad
    LIMITES = {
        'max_iteraciones': 1000000,
        'max_numeros_generar': 100000,
        'max_tamanio_archivo': 50 * 1024 * 1024,  # 50MB
        'max_filas_procesar': 100000,
        'timeout_simulacion': 300  # 5 minutos en segundos
    }

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""
    
    DEBUG = True
    TESTING = False
    
    # Configuración de desarrollo específica
    ALGORITMOS_CONFIG = {
        **Config.ALGORITMOS_CONFIG,
        'congruencial_lineal': {
            'parametros_default': {
                'semilla': 1,
                'a': 5,
                'c': 3,
                'm': 16
            },
            'descripcion': 'Generador congruencial lineal (valores pequeños para testing)'
        }
    }

class TestingConfig(Config):
    """Configuración para entorno de testing"""
    
    DEBUG = False
    TESTING = True
    
    # Usar base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    
    DEBUG = False
    TESTING = False
    
    # Clave secreta más segura en producción
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_temporal_desarrollo_12345'
    
    # Configuración de base de datos para producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(Config.BASEDIR, 'dashboard_estadistica.db')
    
    # Límites más estrictos en producción
    LIMITES = {
        'max_iteraciones': 100000,
        'max_numeros_generar': 50000,
        'max_tamanio_archivo': 10 * 1024 * 1024,  # 10MB
        'max_filas_procesar': 50000,
        'timeout_simulacion': 60  # 1 minuto en segundos
    }

# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Funciones de utilidad
def allowed_file(filename):
    """Verificar si la extensión del archivo está permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_upload_path(filename=''):
    """Obtener ruta completa para uploads"""
    return os.path.join(Config.UPLOAD_FOLDER, filename)

def create_upload_folder():
    """Crear directorio de uploads si no existe"""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

def get_algoritmo_config(nombre_algoritmo):
    """Obtener configuración específica de un algoritmo"""
    return Config.ALGORITMOS_CONFIG.get(nombre_algoritmo, {})

def get_parametros_default(nombre_algoritmo):
    """Obtener parámetros por defecto de un algoritmo"""
    algo_config = get_algoritmo_config(nombre_algoritmo)
    return algo_config.get('parametros_default', {})

# Inicializar directorio de uploads al importar el módulo
create_upload_folder()