document.addEventListener('DOMContentLoaded', function() {
    new CheckboxSelectAllManager('#select-all-files', '.select-delete-files');
});

document.addEventListener('htmx:afterSwap', function() {
    new CheckboxSelectAllManager('#select-all-files', '.select-delete-files');
});
