var editor;

function addEditor(selector, hide_save, height) {
    if (hide_save == true) {
        buttons = "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,forecolor,backcolor,styleselect,formatselect,imagebrowser,customimage,|,link,mylink,unlink,|,removeformat,htmlview,|,fullscreen"
    }
    else {
        buttons  = "save,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,forecolor,backcolor,styleselect,formatselect,imagebrowser,customimage,|,link,mylink,unlink,|,removeformat,htmlview,|,fullscreen"
    }

    if (!height) {
        height = "480";
    }

    // Theme options
    $(selector).tinymce({
        // Location of TinyMCE script
        script_url : STATIC_URL + 'tiny_mce-3.5.8/tiny_mce.js',

        // General options
        theme : "advanced",
        plugins : "advimage,safari,save,iespell,directionality,fullscreen,xhtmlxtras,media",

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
        content_css : STATIC_URL + "css/tinymce_styles.css",
        setup : function(ed) {
            ed.addButton('customimage', {
                title: 'Bild einfügen',
                image: STATIC_URL + 'lfs/icons/tinymce_image_icon.png', 
                onclick: function() {
                    const node = ed.selection.getNode();
                    const currentSrc = node && node.nodeName === 'IMG' ? node.src : '';
                    const currentTitle = node && node.nodeName === 'IMG' ? node.title : '';
                    const currentClass = node && node.nodeName === 'IMG' ? node.className : '';
            
                    const formHtml = `
                        <label>Bild-URL:<br><input type="text" id="img-url" style="width:100%" value="${currentSrc}"></label><br><br>
                        <label>Titel (optional):<br><input type="text" id="img-title" style="width:100%" value="${currentTitle}"></label><br><br>
                        <label>CSS-Klasse (optional):<br><input type="text" id="img-class" style="width:100%" value="${currentClass}"></label><br><br>
                        <div style="text-align:center;">
                            <img id="img-preview" src="${currentSrc}" style="max-width:100%; max-height:200px; display:${currentSrc ? 'block' : 'none'};">
                        </div>
                    `;
            
                    $("#dialog").html(formHtml);
            
                    // Live-Vorschau
                    $("#img-url").on("input", function () {
                        const val = $(this).val();
                        if (val) {
                            $("#img-preview").attr("src", val).show();
                        } else {
                            $("#img-preview").hide();
                        }
                    });
            
                    $("#dialog").dialog({
                        modal: true,
                        width: 600,
                        title: "Bild einfügen",
                        buttons: {
                            "Einfügen": function () {
                                const src = $("#img-url").val();
                                const title = $("#img-title").val();
                                const klass = $("#img-class").val();
                                if (src) {
                                    const imgHtml = `<img src="${src}" title="${title}" class="${klass}">`;
                                    ed.selection.setContent(imgHtml);
                                }
                                $(this).dialog("close");
                            },
                            "Abbrechen": function () {
                                $(this).dialog("close");
                            }
                        }
                    }).dialog("open");
                }
            });            
            ed.addButton('htmlview', {
                title: 'HTML anzeigen',
                image: STATIC_URL + 'lfs/icons/tinymce_html_icon.png',
                onclick: function() {
                    const html = ed.getContent({ format: 'html' });
        
                    $("#dialog").html(
                        '<textarea id="html-source-view" style="width:100%; height:400px;">' +
                        $('<div>').text(html).html() +
                        '</textarea>'
                    );
        
                    $("#dialog").dialog({
                        modal: true,
                        width: 800,
                        height: 500,
                        title: "HTML-Quelltext",
                        buttons: {
                            "Einfügen": function() {
                                const newHtml = $("#html-source-view").val();
                                ed.setContent(newHtml);
                                $(this).dialog("close");
                            },
                            "Abbrechen": function() {
                                $(this).dialog("close");
                            }
                        }
                    }).dialog("open");
                }
            });            
            ed.addButton('imagebrowser', {
                // TODO: use gettext
                title : 'Image browser',
                image : STATIC_URL + 'lfs/icons/tinymce_imagebrowser_icon.gif',
                onclick : function(e) {
                    imagebrowser(e, ed);
                    e.preventDefault();
                    return false;
                }
            });
        }
   });
}

function update_editor() {
    /* for each field first detach tinymce and then attach again */
    var TINYMCE_FIELD_IDS = [{id: "#id_description", hide_save: false, height: null},
                             {id: "#id_short_description", hide_save: false, height: '200'},
                             {id: "#id_short_text", hide_save: false, height: '200'},
                             {id: "#id_body", hide_save: false, height: null},
                             {id: "#id_html", hide_save: false, height: null},
                             {id: "#id_note", hide_save: false, height: '100'}];
    $.each(TINYMCE_FIELD_IDS, function(idx, item){
        if (typeof(tinyMCE) != 'undefined'){
            var obj = $(item['id']);
            if (obj.length > 0){
                obj.tinymce().remove();
            }
        }
        addEditor(item['id'], item['hide_save'], item['height']);
    });
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
        data = safeParseJSON(data);
        $("#dialog").html(data["html"]);
    });

    $("#dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        width: 800,
        height: 500,
        draggable: false,
        resizable: false
    });

    $("#dialog").dialog("open");
}

function insertHTML(html) {
    editor.selection.setContent(html);
}
