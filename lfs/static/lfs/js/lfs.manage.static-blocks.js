$(function () {
    // static blocks files tab
    var file_upload = $('#file_upload'),
        upload_url = file_upload.prop('action');

    file_upload.fileupload({
        url: upload_url,
        dataType: 'json',
        singleFileUploads: false // add event will now receive a list of files
    }).on('fileuploadadd', function (e, data) {
            var files_table = $("#files-uploads-table");
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
            var uploads_table = $("#files-uploads-table");
            var url = uploads_table.attr("data");

            // after upload is done remove information about uploading
            uploads_table.empty();
            $.get(url, function(data) {
                data = safeParseJSON(data);
                $("#files-list").html(data["html"]);
                $.jGrowl(data["message"]);
            });
      })
    .prop('disabled', !$.support.fileInput)
    .parent().addClass($.support.fileInput ? undefined : 'disabled');
    });