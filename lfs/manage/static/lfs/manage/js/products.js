function initializeCheckboxSelectAllManagers() {
    new CheckboxSelectAllManager('.select-all-images', '.select-image');
    new CheckboxSelectAllManager('.select-all-attachments', '.select-attachment');
    new CheckboxSelectAllManager('.select-all-variants', '.select-variant');
    new CheckboxSelectAllManager('.select-all-active', '.select-active');
    new CheckboxSelectAllManager('.select-all-sku', '.select-sku');
    new CheckboxSelectAllManager('.select-all-name', '.select-name');
    new CheckboxSelectAllManager('.select-all-price', '.select-price');
    new CheckboxSelectAllManager('.select-all-available-accessories', '.select-available-accessory');
    new CheckboxSelectAllManager('.select-all-assigned-accessories', '.select-assigned-accessory');
    new CheckboxSelectAllManager('.select-all-available-related', '.select-available-related');
    new CheckboxSelectAllManager('.select-all-assigned-related', '.select-assigned-related');
}

document.addEventListener('DOMContentLoaded', () => {
    initializeCheckboxSelectAllManagers();
});

document.addEventListener('htmx:afterSwap', () => {
    initializeCheckboxSelectAllManagers();
});