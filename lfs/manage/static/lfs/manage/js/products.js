class ProductManager {
    constructor() {
        this.initializeChevronRotation();
    }

    initializeChevronRotation() {
        // Handle chevron rotation for collapsible variants
        document.addEventListener('DOMContentLoaded', function() {
            const collapseElements = document.querySelectorAll('[data-bs-toggle="collapse"]');
            
            collapseElements.forEach(function(element) {
                element.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const target = document.querySelector(this.getAttribute('data-bs-target'));
                    const chevron = this.querySelector('.bi-chevron-down, .bi-chevron-up');
                    
                    if (target) {
                        if (target.classList.contains('show')) {
                            chevron.classList.remove('bi-chevron-up');
                            chevron.classList.add('bi-chevron-down');
                        } else {
                            chevron.classList.remove('bi-chevron-down');
                            chevron.classList.add('bi-chevron-up');
                        }
                    }
                });
            });
        });
    }
}

function initializeCheckboxSelectAllManagers() {
    new CheckboxSelectAllManager('.select-all-images', '.select-image');
    new CheckboxSelectAllManager('.select-all-attachments', '.select-attachment');
    new CheckboxSelectAllManager('.select-all-variants', '.select-variant');
    new CheckboxSelectAllManager('.select-all-active', '.select-active');
    new CheckboxSelectAllManager('.select-all-sku', '.select-sku');
    new CheckboxSelectAllManager('.select-all-name', '.select-name');
    new CheckboxSelectAllManager('.select-all-price', '.select-price');
    new CheckboxSelectAllManager('.select-all-available-accessories', '.select-available-accessory');
    new CheckboxSelectAllManager('.select-all-assigned-accessories', '.select-assigned-accessory');
    new CheckboxSelectAllManager('.select-all-available-related', '.select-available-related');
    new CheckboxSelectAllManager('.select-all-assigned-related', '.select-assigned-related');
    new ProductManager();
}

document.addEventListener('DOMContentLoaded', () => {
    initializeCheckboxSelectAllManagers();
});

document.addEventListener('htmx:afterSwap', () => {
    initializeCheckboxSelectAllManagers();
});