// Featured Products Management JavaScript

// Select all functionality for featured products
document.addEventListener('DOMContentLoaded', function() {
    const selectAllFeaturedCheckbox = document.querySelector('.select-all-featured');
    const featuredCheckboxes = document.querySelectorAll('.select-featured');
    
    if (selectAllFeaturedCheckbox && featuredCheckboxes.length > 0) {
        selectAllFeaturedCheckbox.addEventListener('change', function() {
            featuredCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Update select all when individual featured checkboxes change
    featuredCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.select-featured:checked').length;
            const totalCount = featuredCheckboxes.length;
            
            if (selectAllFeaturedCheckbox) {
                selectAllFeaturedCheckbox.checked = checkedCount === totalCount;
                selectAllFeaturedCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
            }
        });
    });
});

// Select all functionality for products list
document.addEventListener('DOMContentLoaded', function() {
    const selectAllProductsCheckbox = document.querySelector('.select-all-products');
    const productCheckboxes = document.querySelectorAll('.select-product');
    
    if (selectAllProductsCheckbox) {
        selectAllProductsCheckbox.addEventListener('change', function() {
            productCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Update select all when individual product checkboxes change
    productCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.select-product:checked').length;
            const totalCount = productCheckboxes.length;
            
            if (selectAllProductsCheckbox) {
                selectAllProductsCheckbox.checked = checkedCount === totalCount;
                selectAllProductsCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
            }
        });
    });
});
