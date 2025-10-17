// Charts and visualization functionality

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        };
    }

    init() {
        this.renderAllCharts();
    }

    createChart(canvasId, type, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const mergedOptions = { ...this.defaultOptions, ...options };
        
        const chart = new Chart(ctx, {
            type: type,
            data: data,
            options: mergedOptions
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    renderAllCharts() {
        // Initialize charts when needed
        this.initializeExampleCharts();
    }

    initializeExampleCharts() {
        // Example distribution chart
        const distributionData = {
            labels: ['0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'],
            datasets: [{
                label: 'Distribución de Números Aleatorios',
                data: [12, 19, 8, 15, 12, 18, 11, 9, 14, 12],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        };

        this.createChart('distributionChart', 'bar', distributionData, {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        });

        // Example sequence chart
        const sequenceData = {
            labels: Array.from({length: 50}, (_, i) => i + 1),
            datasets: [{
                label: 'Secuencia de Números',
                data: Array.from({length: 50}, () => Math.random()),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        this.createChart('sequenceChart', 'line', sequenceData, {
            scales: {
                y: {
                    min: 0,
                    max: 1
                }
            }
        });
    }

    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    exportChartAsImage(canvasId, filename = 'chart.png') {
        const chart = this.charts.get(canvasId);
        if (chart) {
            const link = document.createElement('a');
            link.download = filename;
            link.href = chart.toBase64Image();
            link.click();
        }
    }

    // Method to generate chart from simulation data
    generateDistributionChart(data, canvasId) {
        const histogram = this.calculateHistogram(data, 10);
        
        const chartData = {
            labels: histogram.bins,
            datasets: [{
                label: 'Frecuencia',
                data: histogram.frequencies,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        };

        return this.createChart(canvasId, 'bar', chartData, {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frecuencia'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Rango'
                    }
                }
            }
        });
    }

    calculateHistogram(data, binsCount) {
        const min = Math.min(...data);
        const max = Math.max(...data);
        const binSize = (max - min) / binsCount;
        
        const bins = [];
        const frequencies = Array(binsCount).fill(0);
        
        for (let i = 0; i < binsCount; i++) {
            const binStart = min + i * binSize;
            const binEnd = binStart + binSize;
            bins.push(`${binStart.toFixed(2)}-${binEnd.toFixed(2)}`);
        }
        
        data.forEach(value => {
            const binIndex = Math.min(Math.floor((value - min) / binSize), binsCount - 1);
            frequencies[binIndex]++;
        });
        
        return { bins, frequencies };
    }
}

// Initialize charts when available
if (typeof Chart !== 'undefined') {
    window.chartManager = new ChartManager();
    document.addEventListener('DOMContentLoaded', () => {
        window.chartManager.init();
    });
}