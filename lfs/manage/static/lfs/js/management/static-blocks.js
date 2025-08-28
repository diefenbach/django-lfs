/**
 * Manages "Select All" checkbox functionality for file lists
 */
class SelectAllCheckboxManager {
    constructor(selectAllSelector = '#select-all-files', itemSelector = '.select-delete-files') {
        this.selectAllSelector = selectAllSelector;
        this.itemSelector = itemSelector;
        this.selectAllCheckbox = null;
        this.itemCheckboxes = [];
        
        this.initialize();
    }

    /**
     * Initialize the select all functionality
     */
    initialize() {
        this.selectAllCheckbox = document.querySelector(this.selectAllSelector);
        this.itemCheckboxes = document.querySelectorAll(this.itemSelector);

        if (!this.selectAllCheckbox || this.itemCheckboxes.length === 0) {
            return;
        }

        this.bindEvents();
        this.updateSelectAllState();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Remove existing listeners to prevent duplicates
        const newSelectAllCheckbox = this.selectAllCheckbox.cloneNode(true);
        this.selectAllCheckbox.parentNode.replaceChild(newSelectAllCheckbox, this.selectAllCheckbox);
        this.selectAllCheckbox = newSelectAllCheckbox;

        // Handle select all checkbox click
        this.selectAllCheckbox.addEventListener('change', (event) => {
            this.handleSelectAllChange(event.target.checked);
        });

        // Handle individual checkbox changes
        this.itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateSelectAllState();
            });
        });
    }

    /**
     * Handle select all checkbox change
     * @param {boolean} isChecked - Whether select all is checked
     */
    handleSelectAllChange(isChecked) {
        // Re-query to get current checkboxes (in case DOM changed)
        const currentItemCheckboxes = document.querySelectorAll(this.itemSelector);
        currentItemCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
    }

    /**
     * Update select all checkbox state based on individual checkboxes
     */
    updateSelectAllState() {
        if (!this.selectAllCheckbox) return;

        const currentItemCheckboxes = document.querySelectorAll(this.itemSelector);
        const checkedCount = document.querySelectorAll(`${this.itemSelector}:checked`).length;
        const totalCount = currentItemCheckboxes.length;

        if (totalCount === 0) {
            // No items - hide or disable select all
            this.selectAllCheckbox.checked = false;
            this.selectAllCheckbox.indeterminate = false;
            return;
        }

        if (checkedCount === 0) {
            // Nothing selected
            this.selectAllCheckbox.checked = false;
            this.selectAllCheckbox.indeterminate = false;
        } else if (checkedCount === totalCount) {
            // Everything selected
            this.selectAllCheckbox.checked = true;
            this.selectAllCheckbox.indeterminate = false;
        } else {
            // Partial selection
            this.selectAllCheckbox.checked = false;
            this.selectAllCheckbox.indeterminate = true;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new SidebarSearch();
    new SelectAllCheckboxManager();
});

document.addEventListener('htmx:afterSwap', function() {
    new SidebarSearch();
});