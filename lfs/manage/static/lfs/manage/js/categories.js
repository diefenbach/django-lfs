// Funktion zum Ein-/Ausklappen von Kategorien
function toggleCategory(categoryId) {
    const toggleBtn = document.querySelector(`.toggle-btn[data-category-id="${categoryId}"]`);
    const categoryLi = document.getElementById(`category_${categoryId}`);

    if (!toggleBtn || !categoryLi) {
        return;
    }

    // Finde die nächste UL-Ebene
    const childUl = categoryLi.querySelector('ul');

    if (childUl) {
        const isExpanded = toggleBtn.classList.contains('expanded');

        const icon = toggleBtn.querySelector('i');

        if (isExpanded) {
            // Einklappen
            toggleBtn.classList.remove('expanded');
            toggleBtn.classList.add('collapsed');
            if (icon) {
                icon.className = 'bi bi-chevron-right';
            }
            childUl.classList.add('collapsed');
            childUl.classList.remove('expanded');
        } else {
            // Ausklappen
            toggleBtn.classList.remove('collapsed');
            toggleBtn.classList.add('expanded');
            if (icon) {
                icon.className = 'bi bi-chevron-down';
            }
            childUl.classList.add('expanded');
            childUl.classList.remove('collapsed');
        }
    }
}

// Drag & Drop Toggle State
let dndEnabled = true;

// Drag & Drop sperren/aktivieren
function toggleDnD() {
    const toggleBtn = document.getElementById('toggle-dnd');
    if (!toggleBtn) return;

    dndEnabled = !dndEnabled;
    const icon = toggleBtn.querySelector('i');

    if (dndEnabled) {
        // Aktiviere Drag & Drop
        icon.className = 'bi bi-unlock';
        toggleBtn.title = 'Drag & drop aktiv';
        // Re-initialisiere Sortable für alle Listen
        initSortable('level-1', 'nested-list');
        document.querySelectorAll('.level-2, .level-3, .level-4').forEach(list => {
            if (list.id) {
                initSortable(list.id, 'nested-list');
            }
        });
    } else {
        // Deaktiviere Drag & Drop
        icon.className = 'bi bi-lock';
        toggleBtn.title = 'Drag & drop gesperrt';
        // Zerstöre alle Sortable-Instanzen
        document.querySelectorAll('.level-1, .level-2, .level-3, .level-4').forEach(list => {
            if (list.sortable) {
                list.sortable.destroy();
                list.sortable = null;
            }
        });
    }
}

// Alle Kategorien ausklappen
function expandAllCategories() {
    // Setze alle Toggle-Buttons auf expanded
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('collapsed');
        btn.classList.add('expanded');
        const icon = btn.querySelector('i');
        if (icon) {
            icon.className = 'bi bi-chevron-down';
        }
    });

    // Zeige alle UL-Elemente
    document.querySelectorAll('.level-2, .level-3, .level-4').forEach(ul => {
        ul.classList.remove('collapsed');
        ul.classList.add('expanded');
    });
}

// Alle Kategorien einklappen
function collapseAllCategories() {
    // Setze alle Toggle-Buttons auf collapsed
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('expanded');
        btn.classList.add('collapsed');
        const icon = btn.querySelector('i');
        if (icon) {
            icon.className = 'bi bi-chevron-right';
        }
    });

    // Verstecke alle UL-Elemente
    document.querySelectorAll('.level-2, .level-3, .level-4').forEach(ul => {
        ul.classList.remove('expanded');
        ul.classList.add('collapsed');
    });
}

// Event-Handler für Toggle-Buttons
function initToggleButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('toggle-btn') || e.target.closest('.toggle-btn')) {
            e.preventDefault();
            e.stopPropagation();
            const toggleBtn = e.target.closest('.toggle-btn');
            if (toggleBtn) {
                const categoryId = toggleBtn.getAttribute('data-category-id');
                if (categoryId) {
                    toggleCategory(categoryId);
                }
            }
        }
    });

    // Verhindere Drag beim Klick auf Toggle-Button
    document.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('toggle-btn') || e.target.closest('.toggle-btn')) {
            e.stopPropagation();
        }
    });
}

// Event-Handler für Sidebar-Buttons
function initSidebarButtons() {
    // Toggle DnD Button
    const toggleDndBtn = document.getElementById('toggle-dnd');
    if (toggleDndBtn) {
        toggleDndBtn.addEventListener('click', toggleDnD);
    }

    // Expand All Button
    const expandAllBtn = document.getElementById('expand-all');
    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', expandAllCategories);
    }

    // Collapse All Button
    const collapseAllBtn = document.getElementById('collapse-all');
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', collapseAllCategories);
    }
}

// Funktion zum Sammeln der Kategorie-Hierarchie
function collectCategoryData() {
    const data = [];

    // Sammle alle LI-Elemente mit data-category-id
    document.querySelectorAll('li[data-category-id]').forEach(li => {
        const categoryId = li.getAttribute('data-category-id');
        const level = parseInt(li.getAttribute('data-level')) || 0;

        // Finde den Parent basierend auf der UL-Hierarchie
        let parentId = 'root';
        let parentUl = li.closest('ul');

        // Gehe nach oben in der Hierarchie
        while (parentUl) {
            const parentLi = parentUl.closest('li[data-category-id]');
            if (parentLi) {
                parentId = parentLi.getAttribute('data-category-id');
                break;
            }
            parentUl = parentUl.parentElement.closest('ul');
        }

        data.push(`category[${categoryId}]=${parentId}`);
    });

    return data.join('&');
}

// Funktion zum Senden der Daten an den Server
function saveCategoryStructure() {
    const categoriesList = document.getElementById('categories-list');
    if (!categoriesList) {
        return;
    }

    const sortUrl = categoriesList.querySelector('ul')?.getAttribute('data-sort-url');
    const csrfToken = categoriesList.querySelector('ul')?.getAttribute('data-csrf-token');

    if (!sortUrl) {
        return;
    }

    const categoryData = collectCategoryData();

    // Erstelle FormData für den POST-Request
    const formData = new FormData();
    formData.append('categories', categoryData);

    fetch(sortUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Server response verarbeitet
    })
    .catch(error => {
        // Fehler beim Speichern
    });
}

// Funktion zum Initialisieren von Sortable für eine Ebene
function initSortable(levelId, groupName, handleSelector = '.drag-handle') {
    const element = document.getElementById(levelId);
    if (!element) {
        return;
    }

    // Check if Sortable is already initialized
    if (element.sortable) {
        element.sortable.destroy();
    }

    const sortable = new Sortable(element, {
        animation: 150,
        ghostClass: 'ghost',
        chosenClass: 'chosen',
        handle: handleSelector,
        group: groupName,

        // Event-Handler für Sortier-Änderungen
        onEnd: function(evt) {
            // Nach dem Sortieren automatisch die Struktur speichern
            setTimeout(saveCategoryStructure, 500); // Kleine Verzögerung für bessere UX
        },

        onStart: function(evt) {
            // Drag gestartet
        }
    });

    // Store reference to sortable instance
    element.sortable = sortable;
}

// Wait for DOM to be ready
function initializeWhenReady() {
    // Initialisiere Toggle-Buttons
    initToggleButtons();

    // Initialisiere Sidebar-Buttons
    initSidebarButtons();

    // Initialisiere alle Ebenen
    initSortable('level-1', 'nested-list');

    // Initialisiere alle Unterlisten
    document.querySelectorAll('.level-2').forEach((list, index) => {
        list.id = list.id || `level-2-${index}`;
        initSortable(list.id, 'nested-list');
    });

    document.querySelectorAll('.level-3').forEach((list, index) => {
        list.id = list.id || `level-3-${index}`;
        initSortable(list.id, 'nested-list');
    });

    document.querySelectorAll('.level-4').forEach((list, index) => {
        list.id = list.id || `level-4-${index}`;
        initSortable(list.id, 'nested-list');
    });
}

// Only initialize once
let initialized = false;

function initializeOnce() {
    if (initialized) {
        return;
    }
    initialized = true;
    initializeWhenReady();
}

// Try different ways to ensure DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeOnce);
} else {
    // DOM is already ready
    initializeOnce();
}

document.addEventListener('DOMContentLoaded', () => {
    new CheckboxSelectAllManager('.select-all-available', '.select-available');
    new CheckboxSelectAllManager('.select-all-assigned', '.select-assigned');
});

document.addEventListener('htmx:afterSwap', () => {
    new CheckboxSelectAllManager('.select-all-available', '.select-available');
    new CheckboxSelectAllManager('.select-all-assigned', '.select-assigned');
});