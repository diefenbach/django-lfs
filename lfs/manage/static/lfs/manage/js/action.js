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
    // SidebarSearch removed - using HTMX backend search instead
}

document.addEventListener('DOMContentLoaded', () => {
    initActionsUI();
});

document.addEventListener('htmx:afterSwap', () => {
    // Re-initialize drag & drop after HTMX swaps
    initActionGroupDnD();
});