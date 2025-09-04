// Shows the modal after content swap. This approach provides a better user experience than using Bootstrap attributes 
// directly in HTML (data-bs-toggle="modal" data-bs-target="#myModal"), as it ensures the modal is initialized with its 
// final dimensions, preventing any visible resizing after display.
document.addEventListener('htmx:afterSwap', evt => {
    const targetId = evt.detail.target?.id;
    let modalEl;
    
    // Target-based modal selection
    if (targetId === "modal-body-sm") {
        modalEl = document.getElementById('lfs-modal-sm');
    } else if (targetId === "modal-body-lg") {
        modalEl = document.getElementById('lfs-modal-lg');
    } else if (targetId === "modal-body-xl") {
        modalEl = document.getElementById('lfs-modal-xl');
    }
    
    if (modalEl) {
        let modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl);
        }
        if (!modalEl.classList.contains('show')) {
            modalInstance.show();
        }
    }
});



document.addEventListener('DOMContentLoaded', function() {
    flatpickr(".dateinput", {
        dateFormat: "d.m.Y",
        locale: "de",
        allowInput: true
    });

    flatpickr(".datetimeinput", {
        enableTime: true,
        dateFormat: "d.m.Y H:i",
        time_24hr: true,
        locale: "de",
        allowInput: true
    });

    tinymce.init({
        selector: '#id_html, #id_description, #id_short_description,#id_body,#id_short_text',
        license_key: 'gpl',
        menubar: false,
        toolbar: 'undo redo bold italic blocks alignleft aligncenter alignright link image code forecolor backcolor removeformat',
        plugins: 'link image code'
    });
});
