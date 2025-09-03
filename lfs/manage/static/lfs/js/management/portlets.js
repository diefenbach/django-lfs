class PortletManager {
    constructor() {
        this.init();
    }

    init() {
        this.initPortletSlotDnD();
    }


    getCSRFToken() {
        const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return tokenInput ? tokenInput.value : '';
    }

    updateSlotEmptyState(slotEl) {
        const hasPortlets = slotEl.querySelector('.portlet-item') !== null;
        const emptyInfo = slotEl.querySelector('.portlet-empty-info');
        
        if (hasPortlets) {
            slotEl.classList.remove('portlet-slot-empty');
            if (emptyInfo) {
                emptyInfo.classList.add('d-none');
                emptyInfo.classList.remove('d-flex');
            }
        } else {
            slotEl.classList.add('portlet-slot-empty');
            if (emptyInfo) {
                emptyInfo.classList.remove('d-none');
                emptyInfo.classList.add('d-flex');
            }
        }
    }

    initPortletSlotDnD() {
        document.querySelectorAll('.portlet-slot').forEach((slotEl) => {
            if (slotEl.getAttribute('data-sortable-initialized')) return;
            
            console.log('Initializing portlet slot:', slotEl.dataset.list);
            
            // Initial state
            this.updateSlotEmptyState(slotEl);
            
            Sortable.create(slotEl, {
                draggable: '.portlet-item',
                group: 'portlets',
                animation: 150,
                ghostClass: 'portlet-ghost',
                chosenClass: 'portlet-chosen',
                dragClass: 'portlet-drag',
                emptyInsertThreshold: 5,
                onStart: (evt) => {
                    console.log('Drag started:', evt.item.dataset.id);
                },
                onChange: (evt) => {
                    // Update empty state when items are added/removed
                    this.updateSlotEmptyState(evt.to);
                    if (evt.from !== evt.to) {
                        this.updateSlotEmptyState(evt.from);
                    }
                },
                onEnd: (evt) => {
                    this.handleDragEnd(evt);
                }
            });
            slotEl.setAttribute('data-sortable-initialized', 'true');
        });
    }

    handleDragEnd(evt) {
        const portletId = evt.item.dataset.id;
        const toSlot = evt.to.dataset.list;
        const newIndex = evt.newIndex;
        const csrfToken = this.getCSRFToken();
        
        console.log('Drag ended:', {portletId, toSlot, newIndex});
        
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
                to_slot: toSlot,
                new_index: newIndex,
            },
            swap: "none"
        });
    }
}

// Initialize portlet manager
const portletManager = new PortletManager();

document.addEventListener('DOMContentLoaded', () => {
    portletManager.init();
});

document.addEventListener('htmx:afterSwap', () => {
    portletManager.init();
});
