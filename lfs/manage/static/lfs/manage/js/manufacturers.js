document.addEventListener('DOMContentLoaded', () => {
    new CheckboxSelectAllManager('.select-all-available-products', '.select-available-product');
    new CheckboxSelectAllManager('.select-all-assigned-products', '.select-assigned-product');
});


document.addEventListener('htmx:afterSwap', () => {
    new CheckboxSelectAllManager('.select-all-available-products', '.select-available-product');
    new CheckboxSelectAllManager('.select-all-assigned-products', '.select-assigned-product');
});
