document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#fileInput');
    const uploadText = document.querySelector('.upload-text');
    const uploadForm = document.querySelector('form');
    const submitBtn = document.querySelector('.btn-upload');

    // Drag & Drop Effects
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.classList.add('drag-over');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('drag-over');
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFiles(files);
    }

    // Input Change Effect
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const fileName = files[0].name;
            uploadText.innerHTML = `<i class="fa fa-check-circle" style="color: #4ade80;"></i> Selected: <strong>${fileName}</strong>`;
            submitBtn.innerHTML = 'Upload File';
            submitBtn.style.opacity = '1';
        }
    }

    // Form Submit Animation
    uploadForm.addEventListener('submit', (e) => {
        if (fileInput.files.length === 0) {
            e.preventDefault();
            alert('Please select a file first!');
            return;
        }
        submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Uploading...';
    });

    // Delete Confirmation
    const deleteLinks = document.querySelectorAll('.btn-delete');
    deleteLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const href = link.getAttribute('href');

            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#000000',
                cancelButtonColor: '#ef4444',
                confirmButtonText: 'Yes, delete it!',
                background: '#ffffff',
                color: '#0f172a'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = href;
                }
            });
        });
    });
});
