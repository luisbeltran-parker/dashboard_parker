// Main JavaScript file for the dashboard

class DashboardApp {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        this.loadDashboardStats();
    }

    setupEventListeners() {
        // Theme switcher
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Tab navigation
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });

        // File upload handling
        this.setupFileUpload();
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update theme toggle button text
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.textContent = theme === 'light' ? '🌙 Dark' : '☀️ Light';
        }
    }

    switchTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab content
        const targetContent = document.getElementById(`${tabName}-tab`);
        const targetTab = document.querySelector(`[data-tab="${tabName}"]`);

        if (targetContent && targetTab) {
            targetContent.classList.add('active');
            targetTab.classList.add('active');
        }
    }

    setupFileUpload() {
        const fileInputs = document.querySelectorAll('.file-input');
        const uploadAreas = document.querySelectorAll('.file-upload-area');

        fileInputs.forEach((input, index) => {
            const area = uploadAreas[index];
            if (!area) return;

            // Click on area triggers file input
            area.addEventListener('click', () => {
                input.click();
            });

            // Drag and drop functionality
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                if (e.dataTransfer.files.length) {
                    input.files = e.dataTransfer.files;
                    this.updateFileLabel(area, e.dataTransfer.files[0]);
                }
            });

            // File selection via input
            input.addEventListener('change', () => {
                if (input.files.length) {
                    this.updateFileLabel(area, input.files[0]);
                }
            });
        });
    }

    updateFileLabel(area, file) {
        const label = area.querySelector('.file-label');
        if (label) {
            label.textContent = file.name;
            label.classList.add('text-success');
        }
    }

    async handleFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Show loading state
        if (submitBtn) {
            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<span class="loading"></span> Procesando...';
            submitBtn.disabled = true;
        }

        try {
            // Simulate processing delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Here you would typically handle the form submission
            console.log('Form submitted:', form.id);
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showAlert('Error al procesar el formulario', 'danger');
        } finally {
            // Restore button state
            if (submitBtn) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} fade-in`;
        alertDiv.textContent = message;

        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);

        // Remove alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    loadDashboardStats() {
        // Simulate loading statistics
        setTimeout(() => {
            const stats = {
                algorithms: 8,
                simulations: 1247,
                filesProcessed: 89,
                accuracy: 98.2
            };

            this.updateStatsDisplay(stats);
        }, 1000);
    }

    updateStatsDisplay(stats) {
        Object.keys(stats).forEach(stat => {
            const element = document.getElementById(`stat-${stat}`);
            if (element) {
                this.animateValue(element, 0, stats[stat], 1000);
            }
        });
    }

    animateValue(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = stat === 'accuracy' ? value.toFixed(1) + '%' : value;
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Utility method to format numbers
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    // Method to download results
    downloadResults(data, filename, type = 'text/csv') {
        const blob = new Blob([data], { type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardApp();
});

// Utility functions
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
};