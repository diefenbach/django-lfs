/**
 * Enhanced hierarchical category drag and drop functionality
 * Supports both sibling and parent-child relationships
 * 
 * jQuery has been removed. All UI feedback is now handled with vanilla JS.
 * Notification is shown using a custom vanilla notification if jGrowl is not present.
 */

let draggedElement = null;
let dropZoneTimeout = null;

// Simple vanilla notification fallback
function showNotification(message) {
    // If jGrowl is available, use it
    if (typeof window.$ !== 'undefined' && typeof window.$.jGrowl !== 'undefined') {
        window.$.jGrowl(message, {theme: 'lfs'});
        return;
    }
    // Otherwise, use a simple vanilla notification
    let notif = document.createElement('div');
    notif.textContent = message;
    notif.style.position = 'fixed';
    notif.style.top = '20px';
    notif.style.right = '20px';
    notif.style.background = '#333';
    notif.style.color = '#fff';
    notif.style.padding = '12px 20px';
    notif.style.borderRadius = '6px';
    notif.style.zIndex = 9999;
    notif.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
    notif.style.fontSize = '1rem';
    notif.className = 'vanilla-notification';
    document.body.appendChild(notif);
    setTimeout(() => {
        notif.style.transition = 'opacity 0.5s';
        notif.style.opacity = 0;
        setTimeout(() => notif.remove(), 500);
    }, 2500);
}

// Initialize Sortable.js for hierarchical categories
document.addEventListener('DOMContentLoaded', function() {
    initializeCategoryManagement();
});

// Also initialize when HTMX swaps content
document.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'categories-list') {
        // Clean up existing sortable instances
        cleanupSortableInstances();
        initializeCategoryManagement();
    }
});

function cleanupSortableInstances() {
    // Destroy existing sortable instances to prevent memory leaks
    const sortableElement = document.querySelector('.hierarchical-sortable');
    if (sortableElement && sortableElement.sortableInstance) {
        sortableElement.sortableInstance.destroy();
        sortableElement.sortableInstance = null;
    }
    
    // Destroy nested sortable instances
    const childrenContainers = document.querySelectorAll('.category-children');
    childrenContainers.forEach(container => {
        if (container.sortableInstance) {
            container.sortableInstance.destroy();
            container.sortableInstance = null;
        }
    });
    
    // Clean up drop zone event listeners
    const dropZones = document.querySelectorAll('.drop-zone');
    dropZones.forEach(dropZone => {
        dropZone.classList.remove('drag-over');
        // Note: Native event listeners will be removed when elements are destroyed
    });
    
    // Clear any remaining drop zone indicators
    clearAllDropZones();
}

// Main initialization function
function initializeCategoryManagement() {
    setupDnDToggle();
    // Start in compact mode - only initialize DnD if toggle is active
    const toggle = document.getElementById('dnd-toggle');
    if (toggle && toggle.dataset.dndActive === 'true') {
        initializeEnhancedHierarchicalSortable();
    }
}

// DnD Toggle functionality
function setupDnDToggle() {
    const toggle = document.getElementById('dnd-toggle');
    const sidebar = document.querySelector('.hierarchical-categories-sidebar');
    
    if (!toggle || !sidebar) return;
    
    toggle.addEventListener('click', function() {
        const isActive = toggle.dataset.dndActive === 'true';
        const newState = !isActive;
        
        // Update toggle state
        toggle.dataset.dndActive = newState;
        const icon = toggle.querySelector('i');
        
        if (newState) {
            // Enable DnD mode
            sidebar.classList.add('dnd-mode');
            icon.className = 'bi bi-unlock-fill';
            toggle.title = 'Drag & Drop Modus deaktivieren';
            
            // Initialize sortable
            initializeEnhancedHierarchicalSortable();
        } else {
            // Disable DnD mode
            sidebar.classList.remove('dnd-mode');
            icon.className = 'bi bi-lock-fill';
            toggle.title = 'Drag & Drop Modus aktivieren';
            
            // Clean up sortable
            cleanupSortableInstances();
        }
        
        // Save state to localStorage
        localStorage.setItem('categories-dnd-mode', newState);
    });
    
    // Restore state from localStorage
    const savedState = localStorage.getItem('categories-dnd-mode');
    if (savedState === 'true') {
        toggle.click(); // This will trigger the toggle
    }
}

function initializeEnhancedHierarchicalSortable() {
    const sortableElement = document.querySelector('.hierarchical-sortable');
    if (sortableElement && !sortableElement.sortableInstance) {
        // Initialize main level sortable with enhanced options
        sortableElement.sortableInstance = new Sortable(sortableElement, {
            animation: 150,
            handle: '.drag-handle',
            group: {
                name: 'categories',
                pull: true,
                put: true
            },
            // Don't filter drop zones - we need them as drop targets
            // filter: '.category-drop-zones',
            onStart: function(evt) {
                draggedElement = evt.item;
                document.body.classList.add('dragging');
                //console.log('Drag started:', draggedElement.dataset.categoryId);
            },
            onEnd: function(evt) {
                document.body.classList.remove('dragging');
                // Only handle sort if it's not a drop zone operation
                if (!evt.to.classList.contains('drop-zone')) {
                    handleSortEnd(sortableElement);
                }
                draggedElement = null;
            }
        });
        
        // Initialize nested sortables for each category children container
        initializeEnhancedNestedSortables();
        
        // Initialize drop zones with native drag/drop events
        initializeNativeDropZones();
        
    }
}

function initializeNestedSortables() {
    // Find all category children containers and make them sortable
    const childrenContainers = document.querySelectorAll('.category-children');
    childrenContainers.forEach(container => {
        if (!container.sortableInstance) {
            container.sortableInstance = new Sortable(container, {
                animation: 150,
                handle: '.drag-handle',
                group: {
                    name: 'categories',
                    pull: true,
                    put: true
                },
                onEnd: function(evt) {
                    const sortableElement = document.querySelector('.hierarchical-sortable');
                    handleSortEnd(sortableElement);
                }
            });
        }
    });
}

function handleSortEnd(sortableElement) {
    // Handle the sort end event
    const sortUrl = sortableElement.dataset.sortUrl;
    const csrfToken = sortableElement.dataset.csrfToken;
    
    // Serialize the new order
    const serialized = serializeHierarchicalOrder(sortableElement);
    
    // Send to server
    fetch(sortUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: 'categories=' + encodeURIComponent(serialized)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showNotification(data.message);
        }
    })
    .catch(error => {
        console.error('Error sorting categories:', error);
    });
}

function serializeHierarchicalOrder(element) {
    const result = [];
    
    function processItem(item, parentId = 'root') {
        const categoryId = item.dataset.categoryId;
        result.push(`category[${categoryId}]=${parentId}`);
        
        // Process direct children only (not nested deeper)
        const childrenContainer = item.querySelector(':scope > .category-children');
        if (childrenContainer) {
            const directChildren = childrenContainer.querySelectorAll(':scope > .category-item');
            directChildren.forEach(child => {
                processItem(child, categoryId);
            });
        }
    }
    
    // Process top-level items
    const topLevelItems = element.querySelectorAll(':scope > .category-item');
    topLevelItems.forEach(item => {
        processItem(item);
    });
    
    return result.join('&');
}

// Enhanced drop zone functions
function initializeEnhancedNestedSortables() {
    // Find all category children containers and make them sortable
    const childrenContainers = document.querySelectorAll('.category-children');
    childrenContainers.forEach(container => {
        if (!container.sortableInstance) {
            container.sortableInstance = new Sortable(container, {
                animation: 150,
                handle: '.drag-handle',
                group: {
                    name: 'categories',
                    pull: true,
                    put: true
                },
                // Don't filter drop zones - we need them as drop targets
                // filter: '.category-drop-zones',
                onStart: function(evt) {
                    draggedElement = evt.item;
                    document.body.classList.add('dragging');
                },
                onEnd: function(evt) {
                    document.body.classList.remove('dragging');
                    // Only handle sort if it's not a drop zone operation
                    if (!evt.to.classList.contains('drop-zone')) {
                        const sortableElement = document.querySelector('.hierarchical-sortable');
                        handleSortEnd(sortableElement);
                    }
                    draggedElement = null;
                }
            });
        }
    });
}

// Initialize drop zones with native drag and drop
function initializeNativeDropZones() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(dropZone => {
        // Make drop zones accept drops
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
        
        dropZone.addEventListener('dragenter', function(e) {
            e.preventDefault();
            //console.log('Dragenter on drop zone:', this.dataset.dropType, this.dataset.targetId);
            if (draggedElement) {
                const targetId = this.dataset.targetId;
                const draggedId = draggedElement.dataset.categoryId;
                
                // Don't allow dropping on self
                if (targetId !== draggedId) {
                    this.classList.add('drag-over');
                    //console.log('Added drag-over class');
                }
            }
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            // Only remove if we're actually leaving the drop zone
            if (!this.contains(e.relatedTarget)) {
                this.classList.remove('drag-over');
            }
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            this.classList.remove('drag-over');
            
            if (draggedElement) {
                const dropType = this.dataset.dropType;
                const targetId = this.dataset.targetId;
                const draggedId = draggedElement.dataset.categoryId;
                
                // Don't allow dropping on self
                if (targetId !== draggedId) {
                    //console.log('Drop successful:', { dropType, targetId, draggedId });
                    handleSpecificDrop(draggedId, targetId, dropType);
                }
            }
        });
    });
}

function setupDropZones(draggedItem) {
    // Clear any existing drop zones
    clearAllDropZones();
    
    // Get all category items except the dragged one and its descendants
    const allItems = document.querySelectorAll('.category-item');
    const draggedId = draggedItem.dataset.categoryId;
    
    allItems.forEach(item => {
        const itemId = item.dataset.categoryId;
        
        // Skip the dragged item itself
        if (itemId === draggedId) return;
        
        // Skip descendants of the dragged item (prevent circular references)
        if (isDescendantOf(item, draggedItem)) return;
        
        // Enable as potential drop zone
        item.classList.add('drop-zone-available');
        
        // Ensure children containers exist for potential child drops
        ensureChildrenContainer(item);
    });
}

function isDescendantOf(potentialDescendant, ancestor) {
    // Check if potentialDescendant is a child of ancestor
    let parent = potentialDescendant.parentElement;
    while (parent) {
        if (parent === ancestor) return true;
        parent = parent.parentElement;
        // Stop at category boundaries
        if (parent && parent.classList.contains('category-item')) {
            parent = parent.parentElement;
        }
    }
    return false;
}

function ensureChildrenContainer(categoryItem) {
    // Check if the category item already has a children container
    let childrenContainer = categoryItem.querySelector(':scope > .category-children');
    
    if (!childrenContainer) {
        // Create a children container for potential drops
        childrenContainer = document.createElement('ul');
        childrenContainer.className = 'category-children drop-zone-empty';
        categoryItem.appendChild(childrenContainer);
        
        // Make the new container sortable
        childrenContainer.sortableInstance = new Sortable(childrenContainer, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            handle: '.drag-handle',
            group: {
                name: 'categories',
                pull: true,
                put: true
            },
            onStart: function(evt) {
                draggedElement = evt.item;
            },
            onEnd: function(evt) {
                clearAllDropZones();
                const sortableElement = document.querySelector('.hierarchical-sortable');
                handleSortEnd(sortableElement);
                draggedElement = null;
            }
        });
    } else if (childrenContainer.children.length === 0) {
        // Add empty drop zone class to existing empty containers
        childrenContainer.classList.add('drop-zone-empty');
    }
}

function clearAllDropZones() {
    // Remove all drop zone classes
    clearDropZoneClass('drop-zone-available');
    clearDropZoneClass('drop-zone-child');
    clearDropZoneClass('drop-zone-sibling');
    clearDropZoneClass('drop-zone-empty');
    clearDropZoneClass('drop-zone-active');
    
    // Remove empty children containers that were created for drop zones
    const emptyContainers = document.querySelectorAll('.category-children:empty');
    emptyContainers.forEach(container => {
        // Only remove if it was created as a temporary drop zone
        if (container.classList.contains('drop-zone-empty')) {
            if (container.sortableInstance) {
                container.sortableInstance.destroy();
            }
            container.remove();
        }
    });
}

function clearDropZoneClass(className) {
    const elements = document.querySelectorAll('.' + className);
    elements.forEach(el => el.classList.remove(className));
}

// Drop Zone Event Handlers are now handled by Sortable.js in initializeDropZones()

function handleSpecificDrop(draggedId, targetId, dropType) {
    const sortableElement = document.querySelector('.hierarchical-sortable');
    const sortUrl = sortableElement.dataset.sortUrl;
    const csrfToken = sortableElement.dataset.csrfToken;
    
    // Create the data based on drop type
    let parentId, position;
    
    if (dropType === 'sibling') {
        // Make it a sibling of target - same parent as target
        const targetElement = document.getElementById(`category_${targetId}`);
        const targetParent = targetElement.closest('.category-children');
        
        if (targetParent) {
            // Target has a parent, get the parent's ID
            const parentElement = targetParent.closest('.category-item');
            parentId = parentElement.dataset.categoryId;
        } else {
            // Target is top-level
            parentId = 'root';
        }
        
        // Position after target
        const targetPos = Array.from(targetElement.parentElement.children).indexOf(targetElement);
        position = (targetPos + 1) * 10;
    } else {
        // Make it a child of target
        parentId = targetId;
        position = 10; // First child
    }
    
    // Send to server
    const data = `categories=category[${draggedId}]=${parentId}`;
    
    fetch(sortUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: data
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showNotification(data.message);
        }
        // Refresh categories list via HTMX instead of full reload
        const categoriesList = document.getElementById('categories-list');
        if (categoriesList && typeof window.htmx !== 'undefined') {
            window.htmx.ajax('GET', window.location.pathname, {
                target: '#categories-list',
                select: '#categories-list'
            });
        } else {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error moving category:', error);
    });
}
