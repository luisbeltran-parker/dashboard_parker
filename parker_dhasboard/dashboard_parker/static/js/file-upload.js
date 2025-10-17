// Enhanced file upload functionality

class FileUploadManager {
    constructor() {
        this.maxFileSize = 16 * 1024 * 1024; // 16MB
        this.allowedTypes = [
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'application/json'
        ];
    }

    init() {
        this.setupUploadHandlers();
        this.setupDragAndDrop();
    }

    setupUploadHandlers() {
        document.querySelectorAll('.file-upload-form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFileUpload(e);
            });
        });
    }

    setupDragAndDrop() {
        const dropZones = document.querySelectorAll('.file-upload-area');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('dragover');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('dragover');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.processFiles(files, zone);
                }
            });
        });
    }

    async handleFileUpload(e) {
        e.preventDefault();
        const form = e.target;
        const fileInput = form.querySelector('input[type="file"]');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!fileInput || !fileInput.files.length) {
            this.showMessage('Por favor selecciona un archivo', 'warning');
            return;
        }

        const files = Array.from(fileInput.files);
        const validFiles = await this.validateFiles(files);
        
        if (validFiles.length === 0) return;

        // Show loading state
        this.setButtonLoading(submitBtn, true);

        try {
            await this.uploadFiles(validFiles, form);
        } catch (error) {
            this.showMessage('Error al subir archivos: ' + error.message, 'danger');
        } finally {
            this.setButtonLoading(submitBtn, false);
        }
    }

    async validateFiles(files) {
        const validFiles = [];
        
        for (const file of files) {
            // Check file size
            if (file.size > this.maxFileSize) {
                this.showMessage(`El archivo ${file.name} es demasiado grande`, 'danger');
                continue;
            }

            // Check file type
            if (!this.isFileTypeAllowed(file)) {
                this.showMessage(`Tipo de archivo no permitido: ${file.name}`, 'danger');
                continue;
            }

            // Additional validation based on file type
            if (file.name.endsWith('.csv')) {
                if (!await this.validateCSV(file)) {
                    this.showMessage(`Archivo CSV inválido: ${file.name}`, 'danger');
                    continue;
                }
            }

            validFiles.push(file);
        }

        return validFiles;
    }

    isFileTypeAllowed(file) {
        if (this.allowedTypes.includes(file.type)) {
            return true;
        }
        
        // Check by extension for better browser compatibility
        const allowedExtensions = ['.csv', '.xlsx', '.xls', '.txt', '.json'];
        return allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    }

    async validateCSV(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const content = e.target.result;
                    // Basic CSV validation - check if it has rows and columns
                    const lines = content.split('\n').filter(line => line.trim());
                    if (lines.length < 2) {
                        resolve(false);
                        return;
                    }
                    
                    const firstLine = lines[0];
                    const columns = firstLine.split(',').length;
                    if (columns < 1) {
                        resolve(false);
                        return;
                    }
                    
                    resolve(true);
                } catch (error) {
                    resolve(false);
                }
            };
            reader.readAsText(file);
        });
    }

    async uploadFiles(files, form) {
        const formData = new FormData();
        
        files.forEach(file => {
            formData.append('files', file);
        });

        // Add additional form data
        const additionalData = new FormData(form);
        additionalData.forEach((value, key) => {
            if (key !== 'files') {
                formData.append(key, value);
            }
        });

        try {
            const response = await fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.showMessage('Archivos subidos exitosamente', 'success');
                this.handleUploadSuccess(result, files);
            } else {
                throw new Error(result.message || 'Error desconocido');
            }

        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    handleUploadSuccess(result, files) {
        // Update file list display
        this.updateFileList(files);
        
        // If there's preview data, show it
        if (result.preview) {
            this.showDataPreview(result.preview);
        }
        
        // Enable processing buttons if needed
        this.enableProcessingButtons();
    }

    updateFileList(files) {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';
        
        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'result-item';
            fileItem.innerHTML = `
                <span>${file.name}</span>
                <span class="result-value">${Utils.formatBytes(file.size)}</span>
            `;
            fileList.appendChild(fileItem);
        });
    }

    showDataPreview(previewData) {
        const previewContainer = document.getElementById('dataPreview');
        if (!previewContainer) return;

        if (Array.isArray(previewData)) {
            let html = '<table class="table"><thead><tr>';
            
            // Create header
            if (previewData.length > 0) {
                Object.keys(previewData[0]).forEach(key => {
                    html += `<th>${key}</th>`;
                });
            }
            
            html += '</tr></thead><tbody>';
            
            // Create rows
            previewData.forEach(row => {
                html += '<tr>';
                Object.values(row).forEach(value => {
                    html += `<td>${value}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            previewContainer.innerHTML = html;
        } else {
            previewContainer.textContent = JSON.stringify(previewData, null, 2);
        }
    }

    enableProcessingButtons() {
        document.querySelectorAll('.btn-process').forEach(btn => {
            btn.disabled = false;
        });
    }

    setButtonLoading(button, isLoading) {
        if (!button) return;
        
        if (isLoading) {
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<span class="loading"></span> Procesando...';
            button.disabled = true;
        } else {
            button.textContent = button.dataset.originalText || 'Subir';
            button.disabled = false;
        }
    }

    showMessage(message, type) {
        // Use the main app's alert system if available
        if (window.dashboard) {
            window.dashboard.showAlert(message, type);
        } else {
            // Fallback alert
            alert(message);
        }
    }
}

// Initialize file upload manager
document.addEventListener('DOMContentLoaded', () => {
    window.fileUploadManager = new FileUploadManager();
    window.fileUploadManager.init();
});