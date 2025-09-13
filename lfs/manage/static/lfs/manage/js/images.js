document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.toggle-images');
    const toggleAllBtn = document.querySelector('.toggle-all');
    const deleteBtn = document.querySelector('.delete-button');
    const selectedCountEl = document.getElementById('selected-count');
    
    function updateSelectionCount() {
        const selectedCount = document.querySelectorAll('.toggle-images:checked').length;
        selectedCountEl.textContent = selectedCount;
        deleteBtn.disabled = selectedCount === 0;
    }
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionCount);
    });
    
    if (toggleAllBtn) {
        toggleAllBtn.addEventListener('click', function() {
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            checkboxes.forEach(cb => cb.checked = !allChecked);
            updateSelectionCount();
        });
    }
    
    // Preview functionality is handled by HTMX attributes
    
    updateSelectionCount();
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
});
