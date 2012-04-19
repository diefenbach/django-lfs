var editor;

function addEditor(selector, hide_save, height) {
    if (hide_save == true) {
        buttons = "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,forecolor,backcolor,styleselect,formatselect,image,media,|,link,mylink,unlink,|,removeformat,code,|,fullscreen"
    }
    else {
        buttons  = "save,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,forecolor,backcolor,styleselect,formatselect,image,media,|,link,mylink,unlink,|,removeformat,code,|,fullscreen"
    }

    if (!height) {
        height = "480";
    }

    // Theme options
    $(selector).tinymce({
        // Location of TinyMCE script
        script_url : '/static/tiny_mce-3.5b3/tiny_mce.js',

        // General options
        theme : "advanced",
        plugins : "safari,save,iespell,directionality,fullscreen,xhtmlxtras,media",

        theme_advanced_buttons1 : buttons,
        theme_advanced_buttons2 : "",
        theme_advanced_buttons3 : "",
        theme_advanced_buttons4 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        save_onsavecallback : "save",
        relative_urls : false,
        verify_html : false,
        height : height,
        content_css : "/static/css/tinymce_styles.css",
        setup : function(ed) {
            ed.addButton('image', {
                onclick : function(e) {
                    imagebrowser(e, ed);
                }
            });

        }

   });
};

function update_editor() {
    addEditor("#id_description");
    addEditor("#id_short_description");
    addEditor("#id_short_text");
    addEditor("#id_body");
    addEditor('#id_html');
    addEditor('#id_note');
}

function save(ed) {
    $("#" + ed.id).parents("form:first").ajaxSubmit({
        dataType: "json",
        success : function(data) {
            show_message(data["message"]);
        }
    })
}

function imagebrowser(e, ed) {
    editor = ed;
    node = editor.selection.getNode();
    url = node.src || "";
    title = node.title || "";
    klass = node.className || ""
    var id = $("#obj-id").attr("data");
    $.get(LFS_MANAGE_IMAGEBROWSER_URL + "?url=" + url + "&title=" + title + "&class=" + klass, function(data) {
        data = $.parseJSON(data);
        $("#dialog").html(data["html"]);
    });

    $("#dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        width: 800,
        height: 500,
        draggable: false,
        resizable: false,
        position: ["center", "center"]
    });

    $("#dialog").dialog("open");
}

function insertHTML(html) {
    editor.selection.setContent(html);
}
