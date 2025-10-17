// scripts.js - Funcionalidades adicionales para el dashboard

class SimulationManager {
    constructor() {
        this.simulations = new Map();
        this.currentSimulation = null;
    }

    // Métodos congruenciales
    simulateCongruential(method, params) {
        const simulationId = `congruential_${Date.now()}`;
        
        const simulation = {
            id: simulationId,
            type: 'congruential',
            method: method,
            params: params,
            results: null,
            timestamp: new Date(),
            status: 'running'
        };

        this.simulations.set(simulationId, simulation);
        this.currentSimulation = simulationId;

        // Simular procesamiento (en una app real, esto llamaría al backend)
        return this.processCongruentialSimulation(simulation);
    }

    processCongruentialSimulation(simulation) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const { method, params } = simulation;
                let numbers = [];

                // Simular generación de números según el método
                switch (method) {
                    case 'lineal':
                        numbers = this.generateLinearCongruential(params);
                        break;
                    case 'multiplicativo':
                        numbers = this.generateMultiplicativeCongruential(params);
                        break;
                    case 'cuadratico':
                        numbers = this.generateQuadraticCongruential(params);
                        break;
                }

                const results = {
                    numbers: numbers,
                    statistics: this.calculateStatistics(numbers),
                    charts: this.generateChartData(numbers),
                    exportData: this.prepareExportData(numbers, simulation)
                };

                simulation.results = results;
                simulation.status = 'completed';

                resolve(simulation);
            }, 1500); // Simular delay de procesamiento
        });
    }

    generateLinearCongruential(params) {
        const { semilla, a, c, m, cantidad } = params;
        const numbers = [];
        let x = semilla;

        for (let i = 0; i < cantidad; i++) {
            x = (a * x + c) % m;
            numbers.push(x / m);
        }

        return numbers;
    }

    generateMultiplicativeCongruential(params) {
        const { semilla, a, m, cantidad } = params;
        const numbers = [];
        let x = semilla;

        for (let i = 0; i < cantidad; i++) {
            x = (a * x) % m;
            numbers.push(x / m);
        }

        return numbers;
    }

    generateQuadraticCongruential(params) {
        const { semilla, a, b, c_const, m, cantidad } = params;
        const numbers = [];
        let x = semilla;

        for (let i = 0; i < cantidad; i++) {
            x = (a * x * x + b * x + c_const) % m;
            numbers.push(x / m);
        }

        return numbers;
    }

    calculateStatistics(numbers) {
        const n = numbers.length;
        const mean = numbers.reduce((a, b) => a + b, 0) / n;
        const variance = numbers.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / n;
        const stdDev = Math.sqrt(variance);
        const sorted = [...numbers].sort((a, b) => a - b);
        const median = sorted[Math.floor(n / 2)];

        return {
            mean: mean,
            median: median,
            variance: variance,
            standardDeviation: stdDev,
            min: Math.min(...numbers),
            max: Math.max(...numbers),
            range: Math.max(...numbers) - Math.min(...numbers)
        };
    }

    generateChartData(numbers) {
        // Generar datos para histograma
        const histogram = this.createHistogram(numbers, 10);
        
        // Generar datos para secuencia
        const sequence = numbers.slice(0, 50).map((num, index) => ({
            x: index,
            y: num
        }));

        return {
            histogram: histogram,
            sequence: sequence
        };
    }

    createHistogram(numbers, bins) {
        const min = Math.min(...numbers);
        const max = Math.max(...numbers);
        const binSize = (max - min) / bins;
        
        const histogram = Array(bins).fill(0);
        const labels = [];

        for (let i = 0; i < bins; i++) {
            const binStart = min + i * binSize;
            const binEnd = binStart + binSize;
            labels.push(`${binStart.toFixed(3)}-${binEnd.toFixed(3)}`);
        }

        numbers.forEach(number => {
            const binIndex = Math.min(Math.floor((number - min) / binSize), bins - 1);
            histogram[binIndex]++;
        });

        return {
            labels: labels,
            data: histogram
        };
    }

    prepareExportData(numbers, simulation) {
        const csvContent = [
            'Index,Value,Method,Timestamp',
            ...numbers.map((num, index) => 
                `${index + 1},${num},${simulation.method},${simulation.timestamp.toISOString()}`
            )
        ].join('\n');

        return {
            csv: csvContent,
            json: JSON.stringify({
                simulation: simulation,
                numbers: numbers,
                statistics: this.calculateStatistics(numbers)
            }, null, 2)
        };
    }

    // Métodos de Monte Carlo
    simulateMonteCarlo(type, params) {
        const simulationId = `montecarlo_${Date.now()}`;
        
        const simulation = {
            id: simulationId,
            type: 'montecarlo',
            method: type,
            params: params,
            results: null,
            timestamp: new Date(),
            status: 'running'
        };

        this.simulations.set(simulationId, simulation);
        this.currentSimulation = simulationId;

        return this.processMonteCarloSimulation(simulation);
    }

    processMonteCarloSimulation(simulation) {
        return new Promise((resolve) => {
            setTimeout(() => {
                let results = {};

                switch (simulation.method) {
                    case 'integracion':
                        results = this.monteCarloIntegration(simulation.params);
                        break;
                    case 'pi':
                        results = this.monteCarloPi(simulation.params);
                        break;
                    case 'simulacion':
                        results = this.monteCarloProcessSimulation(simulation.params);
                        break;
                }

                simulation.results = results;
                simulation.status = 'completed';

                resolve(simulation);
            }, 2000);
        });
    }

    monteCarloIntegration(params) {
        const { funcion, limite_inf, limite_sup, n_puntos } = params;
        
        // Evaluar función (simplificado)
        const f = x => {
            try {
                return eval(funcion.replace(/x/g, `(${x})`));
            } catch (e) {
                return x * x; // Fallback a x²
            }
        };

        let sum = 0;
        const points = [];

        for (let i = 0; i < n_puntos; i++) {
            const x = Math.random() * (limite_sup - limite_inf) + limite_inf;
            const y = f(x);
            sum += y;
            points.push({ x, y });
        }

        const integral = (limite_sup - limite_inf) * sum / n_puntos;

        return {
            integral: integral,
            points: points.slice(0, 1000), // Limitar para visualización
            theoretical: this.calculateTheoreticalIntegral(funcion, limite_inf, limite_sup)
        };
    }

    monteCarloPi(params) {
        const { n_puntos_pi } = params;
        let insideCircle = 0;
        const points = [];

        for (let i = 0; i < n_puntos_pi; i++) {
            const x = Math.random() * 2 - 1;
            const y = Math.random() * 2 - 1;
            const inside = x * x + y * y <= 1;
            
            if (inside) insideCircle++;
            points.push({ x, y, inside });
        }

        const piEstimate = 4 * insideCircle / n_puntos_pi;
        const error = Math.abs(Math.PI - piEstimate);

        return {
            piEstimate: piEstimate,
            error: error,
            percentageError: (error / Math.PI) * 100,
            points: points.slice(0, 500) // Limitar para visualización
        };
    }

    calculateTheoreticalIntegral(funcion, a, b) {
        // Cálculo teórico simplificado para funciones comunes
        const func = funcion.toLowerCase();
        
        if (func.includes('x**2') || func.includes('x^2')) {
            return (b**3 - a**3) / 3;
        } else if (func.includes('x')) {
            return (b**2 - a**2) / 2;
        } else {
            return (b - a) * eval(funcion); // Para constantes
        }
    }

    // Utilidades
    exportSimulation(simulationId, format = 'csv') {
        const simulation = this.simulations.get(simulationId);
        if (!simulation || !simulation.results) {
            throw new Error('Simulación no encontrada o sin resultados');
        }

        const data = simulation.results.exportData[format];
        const filename = `simulation_${simulationId}.${format}`;

        this.downloadFile(data, filename, format === 'csv' ? 'text/csv' : 'application/json');
    }

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    getSimulationHistory() {
        return Array.from(this.simulations.values())
            .sort((a, b) => b.timestamp - a.timestamp);
    }

    clearSimulation(simulationId) {
        this.simulations.delete(simulationId);
        if (this.currentSimulation === simulationId) {
            this.currentSimulation = null;
        }
    }
}

// Funciones de utilidad globales
const SimulationUtils = {
    // Formatear números
    formatNumber: (num, decimals = 4) => {
        return Number(num).toFixed(decimals);
    },

    // Generar colores para gráficos
    generateColors: (count) => {
        const colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ];
        return colors.slice(0, count);
    },

    // Validar parámetros
    validateParameters: (params, rules) => {
        const errors = [];
        
        for (const [key, rule] of Object.entries(rules)) {
            const value = params[key];
            
            if (rule.required && (value === undefined || value === null || value === '')) {
                errors.push(`El parámetro ${key} es requerido`);
                continue;
            }
            
            if (value !== undefined && value !== null) {
                if (rule.type === 'number') {
                    if (isNaN(value)) {
                        errors.push(`El parámetro ${key} debe ser un número`);
                    } else {
                        if (rule.min !== undefined && value < rule.min) {
                            errors.push(`El parámetro ${key} debe ser mayor o igual a ${rule.min}`);
                        }
                        if (rule.max !== undefined && value > rule.max) {
                            errors.push(`El parámetro ${key} debe ser menor o igual a ${rule.max}`);
                        }
                    }
                }
                
                if (rule.type === 'integer' && !Number.isInteger(Number(value))) {
                    errors.push(`El parámetro ${key} debe ser un número entero`);
                }
            }
        }
        
        return errors;
    },

    // Debounce para optimizar
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Crear instancia global del manager de simulaciones
    window.simulationManager = new SimulationManager();
    
    // Configurar tooltips si existen
    if (typeof tippy !== 'undefined') {
        tippy('[data-tippy-content]', {
            placement: 'top',
            animation: 'scale',
            duration: [200, 150]
        });
    }

    // Configurar eventos globales
    setupGlobalEvents();
});

function setupGlobalEvents() {
    // Exportar resultados
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-export]')) {
            const format = e.target.dataset.format || 'csv';
            const simulationId = e.target.dataset.simulation;
            
            if (simulationId && window.simulationManager) {
                try {
                    window.simulationManager.exportSimulation(simulationId, format);
                    if (window.dashboard) {
                        window.dashboard.showAlert(`Resultados exportados en formato ${format.toUpperCase()}`, 'success');
                    }
                } catch (error) {
                    if (window.dashboard) {
                        window.dashboard.showAlert(`Error al exportar: ${error.message}`, 'danger');
                    }
                }
            }
        }
    });

    // Copiar al portapapeles
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-copy]')) {
            const text = e.target.dataset.copyText || e.target.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                if (window.dashboard) {
                    window.dashboard.showAlert('Texto copiado al portapapeles', 'success');
                }
            }).catch(() => {
                if (window.dashboard) {
                    window.dashboard.showAlert('Error al copiar al portapapeles', 'danger');
                }
            });
        }
    });
}

// Exportar para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SimulationManager, SimulationUtils };
}