function initActionGroupDnD() {
    document.querySelectorAll('.action-group').forEach(function(el) {
        if (el.getAttribute('data-sortable-initialized')) return;
        Sortable.create(el, {
            draggable: '.action-item',
            group: 'actions',
            onEnd: function(evt) {
                // Which ID was moved?
                const itemId = evt.item.dataset.id;

                // From which list to which list?
                const fromList = evt.from.dataset.list;
                const toList   = evt.to.dataset.list;

                // New position within the target list
                const newIndex = evt.newIndex;

                // Send to your backend (no DOM swap, just action)
                htmx.ajax('POST', window.LFS_SORT_ACTIONS_URL || '', {
                    values: {
                        csrfmiddlewaretoken: document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                        item_id: itemId,
                        from_list: fromList,
                        to_list: toList,
                        new_index: newIndex,
                    },
                    swap: "none"
                });
            }
        });
        el.setAttribute('data-sortable-initialized', 'true');
    });
}

function initActionSearch() {
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            const actionItems = document.querySelectorAll('.action-item');
            
            actionItems.forEach(function(item) {
                const itemText = item.textContent.toLowerCase();
                
                if (searchTerm === '' || itemText.includes(searchTerm)) {
                    item.style.display = '';
                    item.classList.add('d-block');
                } else {
                    item.style.display = 'none';
                    item.classList.remove('d-block');
                }
            });
        });
        // Clear search when ESC key is pressed
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.dispatchEvent(new Event('input'));
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initActionGroupDnD();
    initActionSearch();
});

document.body.addEventListener('htmx:afterSwap', function(evt) {
    initActionGroupDnD();
    initActionSearch();

    // Show modal only after swap to make it a nicer experience
    if (evt.detail.target.id === "modal-body") {
        var modalEl = document.getElementById('actionModal');
        var modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl);
        }
        if (!modalEl.classList.contains('show')) {
            modalInstance.show();
        }
    }
});