/* Handle autocomplete on manufacturer field at product management page
 * Uses jquery UI autocomplete implementation
 */
$(function() {
    var MANUFACTURER_AUTOCOMPLETE_SETTINGS = {
         source: MANUFACTURERS_AJAX_URL,
         select: function(event, ui){
             $('#id_manufacturer').val(ui.item.value);
             $('#id_manufacturer_autocomplete').val(ui.item.label);
             return false;
         },
         change: function(event, ui){
             if (ui.item === null){
                 // only accept items selected from the list
                 $('#id_manufacturer').val('');
                 $('#id_manufacturer_autocomplete').val('');
             }
             return false;
         },
         minLength: 1
    }

    $('#id_manufacturer_autocomplete').autocomplete(MANUFACTURER_AUTOCOMPLETE_SETTINGS);
    // when form is reloaded we have to reattach autocomplete
    $('body').bind('form-save-end', function(evt){
        if (evt.form_id == 'product-data-form'){
            $('#id_manufacturer_autocomplete').autocomplete(MANUFACTURER_AUTOCOMPLETE_SETTINGS);
        }
    })
})