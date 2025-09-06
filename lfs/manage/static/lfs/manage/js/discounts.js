class DiscountsManager {
    constructor() {
        this.initializeSelectAll();
        this.initializePopovers();
    }

    initializeSelectAll() {
        // Select all functionality for assigned products
        const selectAllAssigned = document.querySelector('.select-all-assigned');
        const assignedCheckboxes = document.querySelectorAll('.select-assigned');
        
        if (selectAllAssigned) {
            selectAllAssigned.addEventListener('change', function() {
                assignedCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }
        
        // Select all functionality for available products
        const selectAllAvailable = document.querySelector('.select-all-available');
        const availableCheckboxes = document.querySelectorAll('.select-available');
        
        if (selectAllAvailable) {
            selectAllAvailable.addEventListener('change', function() {
                availableCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }
    }

    initializePopovers() {
        // Initialize Bootstrap popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => new DiscountsManager());
document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.id === 'products-tables') {
        new DiscountsManager();
    }
});
