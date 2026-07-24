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

function scrollActiveProductIntoView() {
    const active = document.getElementById('active-product');
    if (!active) return;

    let container = active.parentElement;
    while (container) {
        const overflowY = getComputedStyle(container).overflowY;
        if (overflowY === 'auto' || overflowY === 'scroll') break;
        container = container.parentElement;
    }
    if (!container) return;

    const containerRect = container.getBoundingClientRect();
    const activeRect = active.getBoundingClientRect();
    container.scrollTop += (activeRect.top - containerRect.top)
        - (container.clientHeight / 2) + (activeRect.height / 2);
}

document.addEventListener('DOMContentLoaded', () => {
    initializeCheckboxSelectAllManagers();
    scrollActiveProductIntoView();
});

document.addEventListener('htmx:afterSwap', () => {
    initializeCheckboxSelectAllManagers();
    scrollActiveProductIntoView();
});