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

document.addEventListener('DOMContentLoaded', function() {
    new CheckboxManager('.select-all-featured', '.select-featured');
    new CheckboxManager('.select-all-products', '.select-product');
});


document.addEventListener('htmx:afterSwap', function(event) {
    new CheckboxManager('.select-all-featured', '.select-featured');
    new CheckboxManager('.select-all-products', '.select-product');
});
