class SidebarSearch {
    constructor(inputSelector = 'input[type="search"]', itemSelector = '.action-item') {
        this.searchInput = document.querySelector(inputSelector);
        this.itemSelector = itemSelector;

        this.storageKey = 'sidebarSearchTerm_' + (this.searchInput?.dataset.searchId || this.searchInput?.id || 'default');
        if (this.searchInput) {
            this.init();
        }
    }

    init() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved !== null) {
            this.searchInput.value = saved;
            this.handleInput({target: this.searchInput});
        }
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    handleInput(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        localStorage.setItem(this.storageKey, e.target.value);
        for (const item of document.querySelectorAll(this.itemSelector)) {
            const itemText = item.textContent?.toLowerCase() ?? '';
            const match = !searchTerm || itemText.includes(searchTerm);
            item.style.display = match ? '' : 'none';
            item.classList.toggle('d-block', match);
        }
    }

    handleKeydown(e) {
        if (e.key === 'Escape') {
            this.searchInput.value = '';
            this.searchInput.dispatchEvent(new Event('input'));
        }
    }
}

// Shows the modal after content swap. This approach provides a better user experience than using Bootstrap attributes 
// directly in HTML (data-bs-toggle="modal" data-bs-target="#myModal"), as it ensures the modal is initialized with its 
// final dimensions, preventing any visible resizing after display.
document.addEventListener('htmx:afterSwap', evt => {
    const targetId = evt.detail.target?.id;
    let modalEl;
    
    // Target-based modal selection
    if (targetId === "modal-body-sm") {
        modalEl = document.getElementById('lfs-modal-sm');
    } else if (targetId === "modal-body-lg") {
        modalEl = document.getElementById('lfs-modal-lg');
    } else if (targetId === "modal-body-xl") {
        modalEl = document.getElementById('lfs-modal-xl');
    }
    
    if (modalEl) {
        let modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl);
        }
        if (!modalEl.classList.contains('show')) {
            modalInstance.show();
        }
    }
});

// Initialize select all functionality
function initializeSelectAllCheckboxes() {
    const selectAllCheckbox = document.getElementById('select-all-files');
    const fileCheckboxes = document.querySelectorAll('.select-delete-files');

    if (selectAllCheckbox && fileCheckboxes.length > 0) {
        // Remove existing listeners to prevent duplicates
        const newSelectAllCheckbox = selectAllCheckbox.cloneNode(true);
        selectAllCheckbox.parentNode.replaceChild(newSelectAllCheckbox, selectAllCheckbox);

        // Handle select all checkbox click
        newSelectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            const currentFileCheckboxes = document.querySelectorAll('.select-delete-files');
            currentFileCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
        });

        // Handle individual checkbox changes to update select all state
        fileCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectAllState();
            });
        });

        // Initialize the select all state
        updateSelectAllState();
    }
}

// Update select all checkbox state based on individual checkboxes
function updateSelectAllState() {
    const selectAllCheckbox = document.getElementById('select-all-files');
    const fileCheckboxes = document.querySelectorAll('.select-delete-files');
    
    if (!selectAllCheckbox || fileCheckboxes.length === 0) return;

    const checkedCount = document.querySelectorAll('.select-delete-files:checked').length;
    const totalCount = fileCheckboxes.length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === totalCount) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    tinymce.init({
        selector: '#id_html, #id_description, #id_short_description',
        license_key: 'gpl',
        menubar: false,
        toolbar: 'undo redo bold italic blocks alignleft aligncenter alignright link image code forecolor backcolor removeformat',
        plugins: 'link image code'
    });

    // Initialize select all functionality on page load
    initializeSelectAllCheckboxes();
});

// Re-initialize select all functionality after HTMX content updates
document.addEventListener('htmx:afterSwap', function(evt) {
    // Only re-initialize if the swapped content contains file checkboxes
    if (evt.detail.target && evt.detail.target.querySelector && 
        (evt.detail.target.querySelector('#select-all-files') || 
         evt.detail.target.querySelector('.select-delete-files'))) {
        initializeSelectAllCheckboxes();
    }
});
