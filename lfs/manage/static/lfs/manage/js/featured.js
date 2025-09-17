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
    new CheckboxSelectAllManager('.select-all-featured', '.select-featured');
    new CheckboxSelectAllManager('.select-all-products', '.select-product');
    initializeSortable();
});


document.addEventListener('htmx:afterSwap', function(event) {
    new CheckboxSelectAllManager('.select-all-featured', '.select-featured');
    new CheckboxSelectAllManager('.select-all-products', '.select-product');
    // Reinitialize sortable after HTMX swap
    sortableTable = null;
    initializeSortable();
});
