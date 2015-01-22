function popup(url, w, h) {
    w = window.open(url, "Preview", "height=" + h +", width=" + w +", screenX=500, screenY=150, scrollbars=yes, resizable=yes");
    w.focus();
}


function safeParseJSON(data) {
    if (typeof(data) == 'string') {
        data = $.parseJSON(data);
    }
    return data;
}


 function disable_enter_key(e) {
     var key;
     if (window.event)
          key = window.event.keyCode;
     else
          key = e.which;
     if (key == 13)
          return false;
     else
          return true;
}

function hide_ajax_loading() {
    $(".ajax-loading").hide();
}

function show_ajax_loading() {
    $(".ajax-loading").show();
}

function align_buttons(id) {
    var hl  = $(id + "-left").height();
    var hr = $(id  + "-right").height();
    var h = Math.max(hl, hr);
    $(id + "-left").height(h);
    $(id + "-right").height(h);
}

function update_positions() {
    var position = 0;
    $(".position").each(function() {
        position += 10;
        $(this).val(position);
    });
}

function setup_datepicker(){
    $("input.date-picker").datepicker({
        dateFormat: 'yy-mm-dd',
        showWeek: true,
        firstDay: 1
    });
}

function send_form_and_refresh(elem) {
    var form = elem.closest("form");
    form.ajaxSubmit({
        dataType: 'json',
        beforeSend: function(jqXHR, settings){
            var jqx = form.data('jqXHR');
            if (jqx){
                jqx.abort();
            }
            form.data('jqXHR', jqXHR);
        },
        success : function(data) {
            data = safeParseJSON(data);
            for (var html in data["html"]) {
                $(data["html"][html][0]).html(data["html"][html][1]);
            }
        }
    })
}

function sortable() {
    $('ul.sortable').sortable({
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        handle: '.handle',
        helper: 'clone',
        items: 'li',
        opacity: .6,
        revert: 250,
        tabSize: 25,
        tolerance: 'pointer',
        toleranceElement: '> div',
        stop: function(event, ui){
            var url = $(this).attr("href");
            var serialized = ui.item.closest('ul.sortable').sortable('serialize')
            $.ajax({
                url: url,
                context: document.body,
                type: "POST",
                data: {"objs": serialized},
                success: function(data) {
                    data = safeParseJSON(data);
                    $.jGrowl(data["message"], {theme: 'lfs'})
                }
           });
        }
    });
}

function _handle_tabs(tabs_id, cookie_name){
    var $htabs = $('#' + tabs_id);
    if ($htabs.length > 0){
        $htabs.tabs();
        $htabs.show();
        $htabs.on('tabsactivate', function(event, ui) {
            $.cookie(cookie_name, ui.newTab.index());
        });

        var tab_cookie = $.cookie(cookie_name);
        var index = (tab_cookie != null) ? parseInt(tab_cookie) : 0;
        $htabs.tabs("option", "active", index);
    }
}


$(function() {
    var $body = $('body');
    update_editor();
    $(".button").button();
    var message = $.cookie("message");

    if (message != null) {
        $.jGrowl(message, {theme: 'lfs'});
        $.removeCookie('message', { path: '/' });
    }

    $('ul.sf-menu').superfish({
        speed: "fast",
        delay: "200"
    });

    $body.on('click', ".popup-link", function() {
        var url = $(this).attr("href");
        popup(url, "1024", "1000");
        return false;
    });

    // General product tabs
    $('#manage-tabs').tabs();
    $('#manage-tabs').show();

    _handle_tabs('product-tabs', 'product_tab');
    _handle_tabs('category-tabs', 'category_tab');
    _handle_tabs('manufacturer-tabs', 'manufacturer_tab');

    $("#dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        width: 800,
        height: 680,
        draggable: false,
        resizable: false,
        position: { my: "center", at: "center"}
    });

    // Generic ajax save button
    $body.on('click', ".ajax-save-button", function() {
		try {
	        tinymce.triggerSave();
	    }
	    catch(err) {
			// ReferenceError due to undefined tinymce
	    }
        show_ajax_loading();

        // trigger form-save-start event when form is about to be submitted
        var form = $(this).closest("form");
        var form_id = form.get(0).id;
        var event = jQuery.Event("form-save-start");
        event.form_id = form_id;
        $body.trigger(event);

        var action = $(this).attr("name")
        form.ajaxSubmit({
            data : {"action" : action},
            dataType: 'json',
            success : function(data) {
                data = safeParseJSON(data);
                for (var html in data["html"]) {
                    $(data["html"][html][0]).html(data["html"][html][1]);
                }

                if (data["close-dialog"]) {
                    $("#delete-dialog").dialog("close");
                    $("#dialog").dialog("close");
                    $("#portlets-dialog").dialog("close");
                }

                if (data["message"]) {
                    $.jGrowl(data["message"], {theme: 'lfs'});
                }

                hide_ajax_loading();
                update_editor();
                setup_datepicker();

                // trigger form-save-end event when new HTML has already been injected into page
                var event = jQuery.Event("form-save-end");
                event.form_id = form_id;
                event.response_data = data;
                $body.trigger(event);
            }
        });
        return false;
    });

    // Generic ajax link
    $body.on('click', ".ajax-link", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            data = safeParseJSON(data);
            for (var html in data["html"])
                $(data["html"][html][0]).html(data["html"][html][1]);
            if (data["message"]) {
                $.jGrowl(data["message"], {theme: 'lfs'});
            }
            if (data["open-dialog"]) {
                $("#dialog").dialog("open");
            }
        });
        return false;
    });

    // Generic ajax input on keyup
    $body.on('keyup', '.refresh-on-keyup', function() {
        send_form_and_refresh($(this));
    });

    $body.on('change', '.refresh-on-change', function() {
        send_form_and_refresh($(this));
    });

    // Generic select all checkbox
    $body.on('click', '.select-all', function() {
        var checked = this.checked;
        var selector = ".select-" + $(this).attr("value")
        $(selector).each(function() {
            this.checked = checked;
        });
    });

    $body.on('click', '.toggle-all', function() {
        var selector = ".toggle-" + $(this).attr("data")
        $(selector).each(function() {
            this.checked = !this.checked;
        });
    });

    // Criteria
    $body.on('click', '.criterion-add-first-button', function() {
        var position = $(this).siblings(".position").val()
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $(".criteria").prepend(data);
            update_positions();
        });
        return false;
    });

    $body.on('click', '.criterion-add-button', function() {
        var criterion = $(this).parents("tr:first");
        var url = $(this).attr("href");
        $.post(url, function(data) {
            criterion.after(data);
            update_positions();
        });
        return false
    });

    $body.on('change', 'select.criterion-type', function() {
        var type = $(this).selected().val();
        var target = $(this).parents("tr:first");
        $.post("/manage/change-criterion", {"type" : type}, function(data) {
            target.replaceWith(data);
            update_positions();
        });
    });

    $body.on('click', '.criterion-delete-button', function() {
        $(this).parents("tr.criterion:first").remove();
    });

    // Portlets

    $("#portlets-dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        width: 800,
        height: 680,
        draggable: false,
        resizable: false,
        position: { my: "center", at: "center"}
    });


    $body.on('click', '.portlet-edit-button', function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#portlets-dialog").html(data);
            $("#portlets-dialog").dialog("open");
            addEditor('#id_portlet-text', true, 300);
        });
        return false;
    });

    $body.on('click', '.portlet-add-button', function() {
        $(this).parents("form:first").ajaxSubmit({
            dataType: 'json',
            success : function(data) {
                $("#portlets-dialog").html(data['html']);
                $("#portlets-dialog").dialog("open");
                addEditor('#id_portlet-text', true, 300);
        }});
        return false;
    });

    // Export #############################################################
    // Traverses though all parent categories of given clicked knot
    // (category) and call updates state (none, full, half) and checking.
    // Calls "lfs_export_category_state"
    var update_parent_categories = function(knot) {
        knot.parents("li.category").each(function() {
            // url = lfs_export_category_state category id
            var url = $(this).attr("data")
            $.post(url, function(data) {
                data = safeParseJSON(data);
                // Sets 1/2
                $(data["html"][0]).html(data["html"][1]);
                // Sets checking
                $(data["checkbox"][0]).attr("checked", data["checkbox"][1]);
            })
        });
    };

    // Deletes all states of child categories of given knot
    var update_sub_categories = function(knot) {
        knot.parent().find(".category-state").html("");
    };

    $body.on('click', '.category-ajax-link', function() {
        var url = $(this).attr("href");

        // Loads children of clicked category.
        if ($(this).hasClass("collapsed")) {
            $.post(url, function(data) {
                data = safeParseJSON(data);
                for (var html in data["html"])
                    $(data["html"][html][0]).html(data["html"][html][1]);
            });
            $(this).removeClass("collapsed");
            $(this).addClass("expanded");
        }
        // Removes children of clicked category.
        else {
            $(this).siblings("div").html("")
            $(this).removeClass("expanded");
            $(this).addClass("collapsed");
        }
        return false;
    });

    $body.on('click', '.export-category-input', function() {
        // select / deselect all child nodes
        var input = $(this);
        var parent_checked = this.checked;
        input.parent().find("input").each(function() {
            this.checked = parent_checked;
        });

        // Updates child and parent categories of clicked category
        var url = input.data("url");
        if (parent_checked == true) {
            $.post(url, {"action" : "add"}, function(data) {
                update_sub_categories(input);
                update_parent_categories(input);
            });
        }
        else {
            $.post(url, {"action" : "remove"}, function(data) {
                update_sub_categories(input);
                update_parent_categories(input);
            });
        }
    });

    $body.on('click', '.export-product-input', function() {
        // Add / Remove product
        var input = $(this);
        var url = input.data("url");
        var checked = this.checked;

        // Updates parent catgories of clicked product
        if (checked == true) {
            $.post(url, {"action" : "add"}, function(data) { update_parent_categories(input) } );
        }
        else {
            $.post(url, {"action" : "remove"}, function(data) { update_parent_categories(input) });
        }
    });

    $body.on('change', '.category-variants-options', function() {
        var url = $(this).data("url");
        var variants_option = $(this).val();
        $.post(url, { "variants_option" : variants_option });
    });

    // Required
    function toggle_required(checked) {
        if (checked) {
            $("#id_required").parents(".field").show();
        }
        else {
            $("#id_required").parents(".field").hide();
        }
    }
    toggle_required($("#id_configurable").prop("checked"));
    $("#id_configurable").click(function() {
        toggle_required(this.checked)
    });

    $("#delete-dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        draggable: false,
        resizable: false,
        position: { my: "center", at: "center"}
    });

    $body.on('click', '.delete-link', function() {
        $("#delete-dialog > form").attr("action", $(this).attr("href"));
        $("#delete-dialog > p.message").html($(this).attr("dialog_message"));
        $(".dialog-yes-button").addClass($(this).attr("dialog_yes_button_class"));
        $("#delete-dialog").dialog("open");
        return false;
    });

    $body.on('click', '.dialog-close-button', function() {
        $("#delete-dialog").dialog("close");
        return false;
    });

    $("input.button").button();

    $body.on('click', '.property-edit-mode', function() {
        var em = $.cookie("property-edit-mode");
        if (em == "true") {
            $(".property-edit-field").hide();
            $.cookie("property-edit-mode", false);
        }
        else {
            $(".property-edit-field").show();
            $.cookie("property-edit-mode", true);
        }
        return false;
    });

    setup_datepicker();

    $('ol.flat-sortable').sortable({
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        handle: '.handle',
        helper: 'clone',
        items: 'li',
        opacity: .6,
        revert: 250,
        tabSize: 25,
        tolerance: 'pointer',
        toleranceElement: '> div',
        stop: function(event, ui){
            var url = $(this).attr("href");
            serialized = $('ol.flat-sortable').sortable('serialize');
            $.ajax({
                url: url,
                context: document.body,
                type: "POST",
                data: {"serialized": serialized},
                success: function(data) {
                    data = safeParseJSON(data);
                    $.jGrowl(data["message"], {theme: 'lfs'})
                }
           });
        }
    });

    $('ol.sortable').nestedSortable({
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        handle: '.handle',
        helper: 'clone',
        items: 'li',
        opacity: .6,
        revert: 250,
        tabSize: 25,
        tolerance: 'pointer',
        toleranceElement: '> div',
        stop: function(event, ui){
            var url = $(this).attr("href");
            serialized = $('ol.sortable').nestedSortable('serialize');
            $.ajax({
                url: url,
                context: document.body,
                type: "POST",
                data: {"categories": serialized},
                success: function(data) {
                    data = safeParseJSON(data);
                    $.jGrowl(data["message"], {theme: 'lfs'})
                }
           });
        }
    });

    $body.on('click', "#insert-image", function(e) {
        var url = $("input.js-image:checked").prop("value");
        var size = $("#image-size").val();
        var klass = $("#image-class").val();

        if (size)
            url = url.replace("100x100", size);
        else
            url = url.replace(".100x100", "");

        var html = "<img src='" + url + "' />";
        if (klass){
            html = "<img class='" + klass + "' src='" + url + "' />";
        }

        insertHTML(html);
        $("#dialog").dialog("close");
        return false;
    });

    $body.on('click', '#imagebrowser .lfs-pagination a', function(){
        $.get($(this).prop('href'), function(data) {
            data = safeParseJSON(data);
            $("#dialog").html(data["html"]);
        });

        return false;
    });

    $body.on('keypress', '.disable-enter-key', disable_enter_key);
});

$(document).ajaxComplete(function() {
    $(".button").button();
});

$(document).ajaxSend(function(event, xhr, settings) {
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
    }
});
