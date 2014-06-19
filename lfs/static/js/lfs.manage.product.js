/* Handle autocomplete on manufacturer field at product management page
 * Uses jquery UI autocomplete implementation
 */
$(function() {
    var $body = $('body');
    var MANUFACTURER_AUTOCOMPLETE_SETTINGS = {
         source: MANUFACTURERS_AJAX_URL,
         select: function(event, ui){
             $('#id_manufacturer').val(ui.item.value);
             $('#id_manufacturer_autocomplete').val(ui.item.label);
             return false;
         },
         focus: function(event, ui){
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
    };

    $('#id_manufacturer_autocomplete').autocomplete(MANUFACTURER_AUTOCOMPLETE_SETTINGS);
    $body.bind('form-save-start', function(evt){
        if (evt.form_id == 'product-data-form'){
            // ensure that manufacturer_id is cleared if autocomplete field is empty
            if ($('#id_manufacturer_autocomplete').val() === ''){
                $('#id_manufacturer').val('');
            }
        }
    });

    // when form is reloaded we have to reattach autocomplete
    $body.bind('form-save-end', function(evt){
        if (evt.form_id == 'product-data-form'){
            $('#id_manufacturer_autocomplete').autocomplete(MANUFACTURER_AUTOCOMPLETE_SETTINGS);
        }
    });

    $('#file_upload').fileUploadUI({
        uploadTable: $('#files'),
        multiFileRequest : true,
        buildUploadRow: function (files) {
            var fileNames = '';
            for (i = 0; i < files.length; i += 1) {
                fileNames = fileNames + files[i].name + '<br>';
            }
            var msg = $("#files").attr("msg");
            return $(
                '<tr>' +
                '<td><div style="font-weight:bold; padding-bottom:10px">' + msg + '<img src="{{ STATIC_URL }}img/ajax-loader.gif" style="padding:8px 0 0 10px" /></div>' + fileNames + '<\/td>' +
                '<\/tr>'
            );
        },
        onLoadAll: function(files) {
            var url = $("#files").attr("data");
            $.get(url, function(data) {
                data = safeParseJSON(data);
                $("#images").html(data["images"]);
                $.jGrowl(data["message"]);
            });
        }
    });

    $body.on('submit', '#imagebrowser-filter', function(){
        $(this).ajaxSubmit({success: function(data) {
                                         data = safeParseJSON(data);
                                         $("#dialog").html(data["html"]);
                                     }
                           });

        return false;
    });
});