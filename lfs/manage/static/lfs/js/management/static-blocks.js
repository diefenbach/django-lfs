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
    new SidebarSearch();
    
    // Initialize select all functionality on page load
    initializeSelectAllCheckboxes();
});

document.addEventListener('htmx:afterSwap', function(evt) {
    new SidebarSearch();
    
    // Re-initialize select all functionality after HTMX content updates
    if (evt.detail.target && evt.detail.target.querySelector && 
        (evt.detail.target.querySelector('#select-all-files') || 
         evt.detail.target.querySelector('.select-delete-files'))) {
        initializeSelectAllCheckboxes();
    }
});