document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('demo') === 'true') {
        loadDemoDataset();
    }

    const fileInput = document.getElementById('fileInput');
    const releaseFileInput = document.getElementById('releaseFileInput');

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    if (releaseFileInput) {
        releaseFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                alert(`Uploaded release file: ${e.target.files[0].name}`);
            }
        });
    }

    // Drag and drop support
    const dropzone = document.getElementById('dropzone');
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.style.borderColor = 'var(--primary-brown)';
                dropzone.style.backgroundColor = 'var(--surface-hover)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.style.borderColor = 'var(--border-color)';
                dropzone.style.backgroundColor = 'var(--surface)';
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
    }
});

let selectedFile = null;

function handleFileUpload(file) {
    selectedFile = file;
    const formData = new FormData();
    formData.append('feedback_file', file);
    
    startProcessingFlow(formData);
}

function loadDemoDataset() {
    const formData = new FormData();
    formData.append('is_demo', 'true');
    startProcessingFlow(formData);
}

function startProcessingFlow(formData) {
    document.getElementById('uploadView').style.display = 'none';
    document.getElementById('processingView').style.display = 'block';

    const steps = [
        'step-1', 'step-2', 'step-3', 'step-4', 'step-5', 'step-6', 'step-7', 'step-8'
    ];

    let currentStep = 0;
    const progressBar = document.getElementById('progressBar');

    // Make backend call in parallel
    const apiPromise = fetch('/api/upload', {
        method: 'POST',
        body: formData
    }).then(res => res.json());

    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const stepEl = document.getElementById(steps[currentStep]);
            if (stepEl) {
                stepEl.classList.add('done');
                stepEl.querySelector('span').className = 'check-icon';
                stepEl.querySelector('span').innerHTML = '✓';
            }
            currentStep++;
            const pct = Math.round((currentStep / steps.length) * 100);
            if (progressBar) progressBar.style.width = pct + '%';
        } else {
            clearInterval(interval);
            apiPromise.then(data => {
                if (data.record_count) {
                    const rcText = document.getElementById('recordCountText');
                    if (rcText) rcText.textContent = data.record_count;
                }
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 600);
            }).catch(err => {
                console.error("Upload error:", err);
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 600);
            });
        }
    }, 350);
}
