document.addEventListener('DOMContentLoaded', function() {
    new SidebarSearch();
});

document.addEventListener('htmx:afterSwap', function() {
    new SidebarSearch();
});