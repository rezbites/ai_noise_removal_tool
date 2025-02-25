document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const uploadContainer = document.getElementById('upload-container');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const resetBtn = document.getElementById('reset-btn');
    const processBtn = document.getElementById('process-btn');
    const processingOptions = document.getElementById('processing-options');
    const customAreaControls = document.getElementById('custom-area-controls');
    const resultsSection = document.getElementById('results-section');
    const originalImage = document.getElementById('original-image');
    const processedImage = document.getElementById('processed-image');
    const loadingIndicator = document.getElementById('loading-indicator');
    const downloadBtn = document.getElementById('download-btn');
    const filterOptions = document.querySelectorAll('.filter-option');
    
    // Variables for custom area selection
    let isDrawing = false;
    let selectionRect = null;
    let startX, startY;
    let currentArea = 'full';
    let selectedFilter = 'none';
    let processedImageUrl = null;
    
    // Event listeners
    uploadContainer.addEventListener('click', () => fileInput.click());
    
    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.style.borderColor = '#4a6cf7';
    });
    
    uploadContainer.addEventListener('dragleave', () => {
        uploadContainer.style.borderColor = '#6c757d';
    });
    
    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.style.borderColor = '#6c757d';
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });
    
    resetBtn.addEventListener('click', resetUpload);
    
    processBtn.addEventListener('click', () => {
        processingOptions.style.display = 'block';
        window.scrollTo({
            top: processingOptions.offsetTop - 20,
            behavior: 'smooth'
        });
    });
    
    document.querySelectorAll('input[name="removal-area"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentArea = e.target.value;
            if (currentArea === 'custom') {
                customAreaControls.style.display = 'block';
                setupCanvasForSelection();
            } else {
                customAreaControls.style.display = 'none';
                removeSelectionCanvas();
            }
        });
    });
    
    filterOptions.forEach(option => {
        option.addEventListener('click', () => {
            filterOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
            selectedFilter = option.dataset.filter;
            applyFilter(selectedFilter);
        });
    });
    
    downloadBtn.addEventListener('click', downloadImage);
    
    // Functions
    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            uploadContainer.style.display = 'none';
            previewContainer.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }
    
    function resetUpload() {
        fileInput.value = '';
        uploadContainer.style.display = 'flex';
        previewContainer.style.display = 'none';
        processingOptions.style.display = 'none';
        resultsSection.style.display = 'none';
        removeSelectionCanvas();
    }
    
    function setupCanvasForSelection() {
        // Remove any existing canvas
        removeSelectionCanvas();
        
        // Create canvas element for selection
        const canvas = document.createElement('canvas');
        canvas.id = 'selection-canvas';
        canvas.style.position = 'absolute';
        canvas.style.top = imagePreview.offsetTop + 'px';
        canvas.style.left = imagePreview.offsetLeft + 'px';
        canvas.width = imagePreview.width;
        canvas.height = imagePreview.height;
        canvas.style.cursor = 'crosshair';
        
        previewContainer.style.position = 'relative';
        previewContainer.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        // Event listeners for canvas
        canvas.addEventListener('mousedown', (e) => {
            isDrawing = true;
            startX = e.offsetX;
            startY = e.offsetY;
            
            // Clear previous selection
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (!isDrawing) return;
            
            // Clear previous rectangle
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw new rectangle
            const width = e.offsetX - startX;
            const height = e.offsetY - startY;
            
            ctx.strokeStyle = '#4a6cf7';
            ctx.lineWidth = 2;
            ctx.strokeRect(startX, startY, width, height);
            
            // Save selection
            selectionRect = {
                x: startX,
                y: startY,
                width: width,
                height: height
            };
        });
        
        canvas.addEventListener('mouseup', () => {
            isDrawing = false;
        });
    }
    
    function removeSelectionCanvas() {
        const canvas = document.getElementById('selection-canvas');
        if (canvas) {
            canvas.remove();
        }
        selectionRect = null;
    }
    
    function processImage() {
        loadingIndicator.style.display = 'flex';
        
        // Prepare data for backend
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        formData.append('area', currentArea);
        
        if (currentArea === 'custom' && selectionRect) {
            formData.append('selectionRect', JSON.stringify(selectionRect));
        }
        
        // API call to backend
        fetch('http://localhost:5000/process_image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            
            // Display results
            originalImage.src = imagePreview.src;
            processedImage.src = data.processed_image_url;
            processedImageUrl = data.processed_image_url;
            
            resultsSection.style.display = 'block';
            window.scrollTo({
                top: resultsSection.offsetTop - 20,
                behavior: 'smooth'
            });
            
            // Set first filter as active
            filterOptions[0].classList.add('active');
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            console.error('Error:', error);
            alert('An error occurred while processing the image. Please try again.');
        });
    }
    
    function applyFilter(filter) {
        if (!processedImageUrl) return;
        
        if (filter === 'none') {
            // Show the original processed image without filter
            processedImage.src = processedImageUrl;
            return;
        }
        
        loadingIndicator.style.display = 'flex';
        
        // API call to apply filter
        fetch(`http://localhost:5000/apply_filter?image_url=${encodeURIComponent(processedImageUrl)}&filter=${filter}`)
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = 'none';
                processedImage.src = data.filtered_image_url;
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                console.error('Error:', error);
                alert('An error occurred while applying the filter. Please try again.');
            });
    }
    
    function downloadImage() {
        if (!processedImage.src) return;
        
        // Create a temporary link element
        const link = document.createElement('a');
        link.href = processedImage.src;
        link.download = 'processed_image.jpg';
        link.click();
    }
    
    // Add a mock processing function for demo purposes
    processBtn.addEventListener('click', function() {
        // Simulate backend API call with setTimeout
        loadingIndicator.style.display = 'flex';
        
        setTimeout(() => {
            // For demo, we'll just use the same image
            originalImage.src = imagePreview.src;
            processedImage.src = imagePreview.src;
            processedImageUrl = imagePreview.src;
            
            loadingIndicator.style.display = 'none';
            processingOptions.style.display = 'none';
            resultsSection.style.display = 'block';
            
            // Set first filter as active
            filterOptions[0].classList.add('active');
            
            window.scrollTo({
                top: resultsSection.offsetTop - 20,
                behavior: 'smooth'
            });
        }, 2000);
    });
});
