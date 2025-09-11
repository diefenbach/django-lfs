class PropertyGroupsManager {
    constructor() {
        this.initializeSelectAll();
        this.initializePopovers();
    }

    initializeSelectAll() {
        console.log('PropertyGroupsManager: Initializing select all functionality');
        
        // Select all functionality for assigned properties
        const selectAllAssigned = document.querySelector('.select-all-assigned');
        const assignedCheckboxes = document.querySelectorAll('.select-assigned');
        
        console.log('Assigned properties:', { selectAllAssigned, assignedCount: assignedCheckboxes.length });
        
        if (selectAllAssigned) {
            selectAllAssigned.addEventListener('change', function() {
                console.log('Select all assigned changed:', this.checked);
                assignedCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }
        
        // Select all functionality for available properties
        const selectAllProperties = document.querySelector('.select-all-properties');
        const propertyCheckboxes = document.querySelectorAll('.select-property');
        
        console.log('Available properties:', { selectAllProperties, propertyCount: propertyCheckboxes.length });
        
        if (selectAllProperties) {
            selectAllProperties.addEventListener('change', function() {
                console.log('Select all properties changed:', this.checked);
                propertyCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }

        // Select all functionality for available products (products tab)
        const selectAllProducts = document.querySelector('.select-all-products');
        const productCheckboxes = document.querySelectorAll('.select-product');
        
        console.log('Available products:', { selectAllProducts, productCount: productCheckboxes.length });
        
        if (selectAllProducts) {
            selectAllProducts.addEventListener('change', function() {
                console.log('Select all products changed:', this.checked);
                productCheckboxes.forEach(checkbox => {
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

document.addEventListener('DOMContentLoaded', () => {
    console.log('PropertyGroupsManager: DOMContentLoaded - initializing');
    new PropertyGroupsManager();
});

document.addEventListener('htmx:afterSwap', (event) => {
    console.log('PropertyGroupsManager: HTMX afterSwap', event.target.id);
    if (event.target.id === 'products-tables' || event.target.id === 'properties-content' || event.target.id === 'products-content') {
        console.log('PropertyGroupsManager: Reinitializing after HTMX swap');
        new PropertyGroupsManager();
    }
});
