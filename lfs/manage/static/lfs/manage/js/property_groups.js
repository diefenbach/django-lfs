class PropertyGroupsManager {
    constructor() {
        this.initializeSortable();
    }

    initializeSelectAll() {
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
        
        if (selectAllProducts) {
            selectAllProducts.addEventListener('change', function() {
                console.log('Select all products changed:', this.checked);
                productCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }
    }

    initializeSortable() {
        // Initialize sortable for assigned properties table
        const propertiesTable = document.getElementById("sortable-properties-table");
        if (propertiesTable && typeof Sortable !== 'undefined') {
            Sortable.create(propertiesTable, {
                animation: 150,
                handle: ".handle",
                onEnd: (evt) => {
                    // Get the new order of property items
                    const rows = propertiesTable.querySelectorAll('tr[data-id]');
                    const propertyIds = Array.from(rows).map(row => row.getAttribute('data-id'));
                    
                    // Send AJAX request to update positions
                    const sortUrl = document.querySelector('[data-sort-url]')?.getAttribute('data-sort-url');
                    if (sortUrl) {
                        fetch(sortUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                            },
                            body: JSON.stringify({
                                property_ids: propertyIds
                            })
                        }).then(response => {
                            if (response.ok) {
                                console.log('PropertyGroupsManager: Properties sorted successfully');
                            } else {
                                console.error('PropertyGroupsManager: Failed to sort properties');
                            }
                        }).catch(error => {
                            console.error('PropertyGroupsManager: Error sorting properties:', error);
                        });
                    }
                }
            });
        }
    }
}

document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.id === 'products-tables' || event.target.id === 'properties-content' || event.target.id === 'products-content' || event.target.id === 'assigned-properties-list') {
        new PropertyGroupsManager();
        new PopupManager();
        new CheckboxSelectAllManager('.select-all-assigned', '.select-assigned');
        new CheckboxSelectAllManager('.select-all-products', '.select-product');
        new CheckboxSelectAllManager('.select-all-properties', '.select-property');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    new PropertyGroupsManager();
    new PopupManager();
    new CheckboxSelectAllManager('.select-all-assigned', '.select-assigned');
    new CheckboxSelectAllManager('.select-all-products', '.select-product');
    new CheckboxSelectAllManager('.select-all-properties', '.select-property');
});
