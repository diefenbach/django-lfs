class TinyMCEImageBrowserModal {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 1;
        this.selectedImage = null;
        this.searchQuery = '';
        this.availableSizes = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadImages();
    }
    
    bindEvents() {
        document.getElementById('searchBtn').addEventListener('click', () => this.search());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
        document.getElementById('insertBtn').addEventListener('click', () => this.insertImage());
        document.getElementById('sizeSelect').addEventListener('change', () => this.updateInsertButton());
        
        // Reset when modal is shown
        document.getElementById('imageBrowserModal').addEventListener('show.bs.modal', () => {
            this.reset();
        });
    }
    
    reset() {
        this.selectedImage = null;
        this.searchQuery = '';
        document.getElementById('searchInput').value = '';
        document.getElementById('insertBtn').disabled = true;
        document.querySelectorAll('.image-card').forEach(c => c.classList.remove('selected'));
    }
    
    async loadImages(page = 1) {
        this.currentPage = page;
        const container = document.getElementById('imageContainer');
        container.innerHTML = '<div class="loading"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        try {
            const params = new URLSearchParams({
                page: page,
                q: this.searchQuery
            });
            
            const response = await fetch(`${window.TINYMCE_IMAGE_BROWSER_API_URL}?${params}`);
            const data = await response.json();
            
            this.renderImages(data.images);
            this.renderPagination(data.pagination);
            this.updateSizeOptions(data.images);
        } catch (error) {
            console.error('Error loading images:', error);
            container.innerHTML = '<div class="no-images"><i class="bi bi-exclamation-triangle"></i><br>Error loading images</div>';
        }
    }
    
    renderImages(images) {
        const container = document.getElementById('imageContainer');
        
        if (images.length === 0) {
            container.innerHTML = '<div class="no-images"><i class="bi bi-images"></i><br>No images found</div>';
            return;
        }
        
        container.innerHTML = images.map(image => `
            <div class="card image-card" data-image-url="${image.value}" data-image-title="${image.text}">
                <img src="${image.thumb}" alt="${image.alt}" class="image-thumb">
                <div class="card-body p-2">
                    <h6 class="card-title small mb-0" title="${image.text}">${image.text}</h6>
                </div>
            </div>
        `).join('');
        
        // Bind click events
        container.querySelectorAll('.image-card').forEach(card => {
            card.addEventListener('click', () => this.selectImage(card));
        });
    }
    
    renderPagination(pagination) {
        const container = document.getElementById('pagination');
        this.totalPages = pagination.total_pages;
        
        if (pagination.total_pages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<nav><ul class="pagination">';
        
        // Previous button
        if (pagination.has_previous) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.current_page - 1}">Previous</a></li>`;
        }
        
        // Page numbers
        const startPage = Math.max(1, pagination.current_page - 2);
        const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const active = i === pagination.current_page ? 'active' : '';
            html += `<li class="page-item ${active}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
        
        // Next button
        if (pagination.has_next) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.current_page + 1}">Next</a></li>`;
        }
        
        html += '</ul></nav>';
        container.innerHTML = html;
        
        // Bind pagination events
        container.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(link.dataset.page);
                this.loadImages(page);
            });
        });
    }
    
    updateSizeOptions(images) {
        const sizeSelect = document.getElementById('sizeSelect');
        
        if (images.length > 0 && images[0].sizes) {
            this.availableSizes = images[0].sizes;
            sizeSelect.innerHTML = images[0].sizes.map(size => 
                `<option value="${size.value}">${size.label}</option>`
            ).join('');
        }
    }
    
    selectImage(card) {
        // Remove previous selection
        document.querySelectorAll('.image-card').forEach(c => c.classList.remove('selected'));
        
        // Select current card
        card.classList.add('selected');
        this.selectedImage = {
            url: card.dataset.imageUrl,
            title: card.dataset.imageTitle
        };
        
        this.updateInsertButton();
    }
    
    updateInsertButton() {
        const insertBtn = document.getElementById('insertBtn');
        insertBtn.disabled = !this.selectedImage;
    }
    
    search() {
        this.searchQuery = document.getElementById('searchInput').value;
        this.loadImages(1);
    }
    
    insertImage() {
        if (!this.selectedImage) return;
        
        const size = document.getElementById('sizeSelect').value;
        let finalUrl = this.selectedImage.url;
        
        // Apply size if selected
        if (size) {
            const urlParts = finalUrl.split('.');
            const extension = urlParts.pop();
            finalUrl = urlParts.join('.') + '.' + size + '.' + extension;
        }
        
        // Call TinyMCE callback
        if (window.tinymceImageCallback) {
            window.tinymceImageCallback(finalUrl, {
                title: this.selectedImage.title,
                alt: this.selectedImage.title
            });
        }
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('imageBrowserModal'));
        modal.hide();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TinyMCEImageBrowserModal();
});
