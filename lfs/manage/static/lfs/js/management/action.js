function getCSRFToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : '';
}

function initActionGroupDnD() {
    document.querySelectorAll('.action-group').forEach(function(el) {
        if (el.getAttribute('data-sortable-initialized')) return;
        Sortable.create(el, {
            draggable: '.action-item',
            group: 'actions',
            onEnd: function(evt) {
                const itemId = evt.item.dataset.id;
                const fromList = evt.from.dataset.list;
                const toList   = evt.to.dataset.list;
                const newIndex = evt.newIndex;
                const csrfToken = getCSRFToken();
                if (!csrfToken) {
                    console.error('CSRF token not found!');
                    return;
                }
                htmx.ajax('POST', window.LFS_SORT_ACTIONS_URL || '', {
                    values: {
                        csrfmiddlewaretoken: csrfToken,
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

function initActionsUI() {
    initActionGroupDnD();
    new SidebarSearch();
}

document.addEventListener('DOMContentLoaded', () => {
    initActionsUI();
});

// Shows the modal after content swap. This approach provides a better user experience than using Bootstrap attributes 
// directly in HTML (data-bs-toggle="modal" data-bs-target="#myModal"), as it ensures the modal is initialized with its 
// final dimensions, preventing any visible resizing after display.
document.body.addEventListener('htmx:afterSwap', evt => {
    // Modal-Handling
    if (evt.detail.target && evt.detail.target.id === "modal-body") {
        const modalEl = document.getElementById('actionModal');
        let modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl);
        }
        if (!modalEl.classList.contains('show')) {
            modalInstance.show();
        }
    }
});