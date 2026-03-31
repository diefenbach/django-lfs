document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.id === 'products-tables') {
        new PopupManager();
        new CheckboxSelectAllManager('.select-all-available', '.select-available');
        new CheckboxSelectAllManager('.select-all-assigned', '.select-assigned');        
    }
});

document.addEventListener('DOMContentLoaded', () => {
    new PopupManager();
    new CheckboxSelectAllManager('.select-all-available', '.select-available');
    new CheckboxSelectAllManager('.select-all-assigned', '.select-assigned');
});