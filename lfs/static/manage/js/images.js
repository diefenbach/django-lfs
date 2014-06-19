$(function () {
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
            window.location = url;
            return false;
            $.get(url, function(data) {
                data = safeParseJSON(data);
                $("#images").html(data["images"]);
                $.jGrowl(data["message"]);
            });
        }
    });
});