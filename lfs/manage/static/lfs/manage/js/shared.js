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


// Configure HTMX to include CSRF tokens automatically
document.addEventListener('htmx:configRequest', function(evt) {
    // Only add CSRF token for non-GET requests
    if (evt.detail.verb !== 'get') {
        // Try to get CSRF token from cookie first
        const csrfCookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        if (csrfCookie) {
            const csrfToken = csrfCookie.split('=')[1];
            evt.detail.headers['X-CSRFToken'] = csrfToken;
        } else {
            // Fallback to getting CSRF token from form input
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                evt.detail.headers['X-CSRFToken'] = csrfInput.value;
            }
        }
    }
});

document.addEventListener('DOMContentLoaded', function() {
    flatpickr(".dateinput, input[type='date']", {
        dateFormat: "d.m.Y",
        locale: "de",
        allowInput: true
    });

    flatpickr(".datetimeinput", {
        enableTime: true,
        dateFormat: "d.m.Y H:i",
        time_24hr: true,
        locale: "de",
        allowInput: true
    });

    tinymce.init({
        selector: '#id_html,#id_description,#id_short_description,#id_body,#id_short_text',
        license_key: 'gpl',
        menubar: false,
        toolbar: 'undo redo bold italic blocks alignleft aligncenter alignright link image code forecolor backcolor removeformat',
        plugins: 'link image code',
        file_picker_types: 'image',
        file_picker_callback: function(callback, value, meta) {
            if (meta.filetype === 'image') {
                // Store callback for modal to use
                window.tinymceImageCallback = callback;
                
                // Show Bootstrap modal
                const modal = new bootstrap.Modal(document.getElementById('imageBrowserModal'));
                modal.show();
            }
        },
        image_advtab: true,
        image_description: true,
        image_title: true
    });
});

class PopupManager {
    constructor() {
        this.initializePopovers();
    }

    initializePopovers() {
        document.querySelectorAll('[data-bs-toggle="popover"]')
            .forEach(el => new bootstrap.Popover(el));
    }
}


/**
 * CheckboxSelectAllManager class for managing select all checkbox functionality
 */
class CheckboxSelectAllManager {
    /**
     * Create a SelectAll instance
     * @param {string} selectAllSelector - CSS selector for the "select all" checkbox
     * @param {string} itemCheckboxSelector - CSS selector for the individual checkboxes
     * @param {HTMLElement} [container=document] - Container element to search within
     */
    constructor(selectAllSelector, itemCheckboxSelector, container = document) {
        this.container = container;
        this.selectAllSelector = selectAllSelector;
        this.itemCheckboxSelector = itemCheckboxSelector;
        
        this.selectAllCheckbox = this.container.querySelector(selectAllSelector);
        this.itemCheckboxes = this.container.querySelectorAll(itemCheckboxSelector);
        
        if (!this.selectAllCheckbox || this.itemCheckboxes.length === 0) {
            return;
        }
        
        this.bindEvents();
        this.updateSelectAllState();
    }
    
    bindEvents() {
        // Handle select all checkbox change
        this.selectAllCheckbox.addEventListener('change', () => {
            this.handleSelectAllChange();
        });
        
        // Handle individual checkbox changes
        this.itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateSelectAllState();
            });
        });
    }
    
    handleSelectAllChange() {
        const isChecked = this.selectAllCheckbox.checked;
        this.itemCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
    }
    
    updateSelectAllState() {
        const checkedCount = this.container.querySelectorAll(this.itemCheckboxSelector + ':checked').length;
        const totalCount = this.itemCheckboxes.length;
        
        this.selectAllCheckbox.checked = checkedCount === totalCount;
        this.selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
    }
    
    checkAll() {
        this.selectAllCheckbox.checked = true;
        this.handleSelectAllChange();
    }
    
    uncheckAll() {
        this.selectAllCheckbox.checked = false;
        this.handleSelectAllChange();
    }
}