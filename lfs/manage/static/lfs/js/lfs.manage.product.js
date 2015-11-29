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

    // images tab
    var image_file_upload = $('#file_upload'),
        image_upload_url = image_file_upload.prop('action');

    image_file_upload.fileupload({
        url: image_upload_url,
        dataType: 'json',
        singleFileUploads: false // add event will now receive a list of files
    }).on('fileuploadadd', function (e, data) {
            var files_table = $("#images-uploads-table");
            var fileNames = '';
            var msg = files_table.attr("msg");

            $.each(data.files, function (index, file) {
                fileNames = fileNames + file.name + '<br>';
            });
            files_table.append($(
                '<tr>' +
                '<td><div style="font-weight:bold; padding-bottom:10px">' + msg + '<img src="' + STATIC_URL + 'lfs/img/ajax-loader.gif" style="padding:8px 0 0 10px" /></div>' + fileNames + '<\/td>' +
                '<\/tr>'
            ));

            data.submit();
      }).on('fileuploaddone', function (e, data) {
            var uploads_table = $("#images-uploads-table");
            var url = uploads_table.attr("data");

            // after upload is done remove information about uploading
            uploads_table.empty();

            $.get(url, function(data) {
                data = safeParseJSON(data);
                $("#images-list").html(data["images"]);
                $.jGrowl(data["message"]);
            });
      })
    .prop('disabled', !$.support.fileInput)
    .parent().addClass($.support.fileInput ? undefined : 'disabled');

    // attachments tab
    var attachment_upload = $('#attachment_upload'),
        attachment_upload_url = attachment_upload.prop('action');

    attachment_upload.fileupload({
        url: attachment_upload_url,
        dataType: 'json',
        singleFileUploads: false // add event will now receive a list of files
    }).on('fileuploadadd', function (e, data) {
            var files_table = $("#attachment-uploads-table");
            var fileNames = '';
            var msg = files_table.attr("msg");

            $.each(data.files, function (index, file) {
                fileNames = fileNames + file.name + '<br>';
            });
            files_table.append($(
                '<tr>' +
                '<td><div style="font-weight:bold; padding-bottom:10px">' + msg + '<img src="' + STATIC_URL + 'lfs/img/ajax-loader.gif" style="padding:8px 0 0 10px" /></div>' + fileNames + '<\/td>' +
                '<\/tr>'
            ));

            data.submit();
      }).on('fileuploaddone', function (e, data) {
            var uploads_table = $("#attachment-uploads-table");
            var url = uploads_table.attr("data");

            // after upload is done remove information about uploading
            uploads_table.empty();
            $.get(url, function(data) {
                data = safeParseJSON(data);
                $("#attachments-list").html(data["html"]);
                $.jGrowl(data["message"]);
            });
      })
    .prop('disabled', !$.support.fileInput)
    .parent().addClass($.support.fileInput ? undefined : 'disabled');
});