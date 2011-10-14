function addEditor(selector, hide_save) {
    if (hide_save == true) {
        buttons = "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,forecolor,backcolor,styleselect,formatselect,image,|,link,mylink,unlink,|,removeformat,code,|,fullscreen"
    }
    else {
        buttons  = "save,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,forecolor,backcolor,styleselect,formatselect,image,|,link,mylink,unlink,|,removeformat,code,|,fullscreen"
    }

    // Theme options
    $(selector).tinymce({
        // Location of TinyMCE script
        script_url : '/static/tiny_mce-3.4.2/tiny_mce.js',

        // General options
        theme : "advanced",
        plugins : "safari,save,iespell,directionality,fullscreen,xhtmlxtras",

        theme_advanced_buttons1 : buttons,
        theme_advanced_buttons2 : "",
        theme_advanced_buttons3 : "",
        theme_advanced_buttons4 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        save_onsavecallback : "save",
        relative_urls : false,
        height : "480",
        content_css : "/static/css/tinymce_styles.css"
   });
};

function update_editor() {
    addEditor("#id_description");
    addEditor("#id_short_description");
    addEditor("#id_short_text");
    addEditor("#id_body");
    addEditor('#id_html');
}

function save(ed) {
    $("#" + ed.id).parents("form:first").ajaxSubmit({
        dataType: "json",
        success : function(data) {
            show_message(data["message"]);
        }
    })
}
