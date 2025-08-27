class SidebarSearch {
    constructor(inputSelector = 'input[type="search"]', itemSelector = '.action-item') {
        this.searchInput = document.querySelector(inputSelector);
        this.itemSelector = itemSelector;
        if (this.searchInput) {
            this.init();
        }
    }

    init() {
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    handleInput(e) {
        console.log('handleInput', e);
        const searchTerm = e.target.value.toLowerCase().trim();
        for (const item of document.querySelectorAll(this.itemSelector)) {
            const itemText = item.textContent?.toLowerCase() ?? '';
            const match = !searchTerm || itemText.includes(searchTerm);
            item.style.display = match ? '' : 'none';
            item.classList.toggle('d-block', match);
        }
    }

    handleKeydown(e) {
        if (e.key === 'Escape') {
            this.searchInput.value = '';
            this.searchInput.dispatchEvent(new Event('input'));
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    tinymce.init({
        selector: '#id_html, #id_description, #id_short_description',
        license_key: 'gpl',
        menubar: false,
        toolbar: 'undo redo bold italic blocks alignleft aligncenter alignright link image code forecolor backcolor removeformat',
        plugins: 'link image code'
    });    
});
