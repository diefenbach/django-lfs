// Featured Products Management JavaScript

class CheckboxManager {
    constructor(selectAllSelector, itemSelector) {
        this.selectAllCheckbox = document.querySelector(selectAllSelector);
        this.itemCheckboxes = document.querySelectorAll(itemSelector);
        this.initialize();
    }

    initialize() {
        if (!this.selectAllCheckbox || this.itemCheckboxes.length === 0) return;

        // Set up select all checkbox
        this.selectAllCheckbox.addEventListener('change', () => {
            this.itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.selectAllCheckbox.checked;
            });
        });

        // Set up individual checkboxes
        this.itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateSelectAllState());
        });
    }

    updateSelectAllState() {
        const checkedCount = document.querySelectorAll(`${this.itemCheckboxes[0].className.split(' ').map(c => '.' + c).join('')}:checked`).length;
        const totalCount = this.itemCheckboxes.length;
        
        if (this.selectAllCheckbox) {
            this.selectAllCheckbox.checked = checkedCount === totalCount;
            this.selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
        }
    }
}


// Initialize sortable table with drag and drop functionality
let sortableTable = null;

function initializeSortable() {
    const table = document.getElementById("sortable-table");
    if (table && !sortableTable) {
        sortableTable = Sortable.create(table, {
            animation: 150,
            handle: ".handle",
            onEnd: function(evt) {
                // Get the new order of featured items
                const rows = table.querySelectorAll('tr[data-id]');
                const featuredIds = Array.from(rows).map(row => row.getAttribute('data-id'));
                
                // Send AJAX request to update positions
                const sortUrl = document.querySelector('[data-sort-url]')?.getAttribute('data-sort-url') || '/manage/sort-featured';
                fetch(sortUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        featured_ids: featuredIds
                    })
                });
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new CheckboxManager('.select-all-featured', '.select-featured');
    new CheckboxManager('.select-all-products', '.select-product');
    initializeSortable();
});


document.addEventListener('htmx:afterSwap', function(event) {
    new CheckboxManager('.select-all-featured', '.select-featured');
    new CheckboxManager('.select-all-products', '.select-product');
    // Reinitialize sortable after HTMX swap
    sortableTable = null;
    initializeSortable();
});
