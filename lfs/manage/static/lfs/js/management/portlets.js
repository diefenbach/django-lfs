function getCSRFToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : '';
}

function initPortletSlotDnD() {
    document.querySelectorAll('.portlet-slot').forEach(function(slotEl) {
        if (slotEl.getAttribute('data-sortable-initialized')) return;
        
        console.log('Initializing portlet slot:', slotEl.dataset.slotId);
        
        Sortable.create(slotEl, {
            draggable: '.portlet-item',
            group: 'portlets',
            animation: 150,
            ghostClass: 'portlet-ghost',
            chosenClass: 'portlet-chosen',
            dragClass: 'portlet-drag',
            onStart: function(evt) {
                console.log('Drag started:', evt.item.dataset.portletId);
            },
            onEnd: function(evt) {
                const portletId = evt.item.dataset.portletId;
                const fromSlot = evt.from.dataset.slotId;
                const toSlot = evt.to.dataset.slotId;
                const newIndex = evt.newIndex;
                const csrfToken = getCSRFToken();
                
                console.log('Drag ended:', {portletId, fromSlot, toSlot, newIndex});
                
                if (!csrfToken) {
                    console.error('CSRF token not found!');
                    return;
                }
                
                if (!window.LFS_SORT_PORTLETS_URL) {
                    console.error('LFS_SORT_PORTLETS_URL not found!');
                    return;
                }
                
                htmx.ajax('POST', window.LFS_SORT_PORTLETS_URL, {
                    values: {
                        csrfmiddlewaretoken: csrfToken,
                        portlet_id: portletId,
                        from_slot: fromSlot,
                        to_slot: toSlot,
                        new_index: newIndex,
                    },
                    swap: "none"
                });
            }
        });
        slotEl.setAttribute('data-sortable-initialized', 'true');
    });
}

function initPortletsUI() {
    initPortletSlotDnD();
}

document.addEventListener('DOMContentLoaded', () => {
    initPortletsUI();
});

document.addEventListener('htmx:afterSwap', () => {
    // Re-initialize drag & drop after HTMX swaps
    initPortletSlotDnD();
});
