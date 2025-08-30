// Voucher Groups Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize voucher management functionality
    initVoucherManagement();
});

function initVoucherManagement() {
    // Select all checkbox functionality for vouchers
    const selectAllCheckbox = document.getElementById('select-all-vouchers');
    const voucherCheckboxes = document.querySelectorAll('.voucher-checkbox');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            voucherCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Update select all checkbox when individual checkboxes change
    voucherCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.voucher-checkbox:checked').length;
            const totalCount = voucherCheckboxes.length;
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = checkedCount === totalCount;
                selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
            }
        });
    });
}

// Re-initialize after HTMX swaps
document.addEventListener('htmx:afterSwap', function(event) {
    // Re-initialize voucher management if the swapped content contains voucher elements
    if (event.detail.target.querySelector('.voucher-checkbox') || 
        event.detail.target.querySelector('#select-all-vouchers')) {
        initVoucherManagement();
    }
    
    // Update filter state after HTMX swap
    updateFilterState();
});

function updateFilterState() {
    // Ensure filter dropdowns maintain their state after HTMX updates
    const usageFilter = document.querySelector('select[name="usage_filter"]');
    if (usageFilter) {
        // The selected state should be maintained by the template
        // This function can be extended for additional filter logic if needed
    }
}
