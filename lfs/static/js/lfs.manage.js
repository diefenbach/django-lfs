function popup(url, w, h) {
    w = window.open(url, "Preview", "height=" + h +", width=" + w +", screenX=500, screenY=150, scrollbars=yes, resizable=yes");
    w.focus();
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
};

function show_ajax_loading() {
    $(".ajax-loading").show();
};

function align_buttons(id) {
    var hl  = $(id + "-left").height();
    var hr = $(id  + "-right").height();
    var h = Math.max(hl, hr)
    $(id + "-left").height(h);
    $(id + "-right").height(h);
}

function update_positions() {
    var position = 0;
    $(".position").each(function() {
        position += 10;
        $(this).val(position);
    });
};

function setup_datepicker(){
    $("input.date-picker").datepicker({
        dateFormat: 'yy-mm-dd',
        showWeek: true,
        firstDay: 1
    });
}

function send_form_and_refresh(mythis) {
    mythis.parents("form:first").ajaxSubmit({
        success : function(data) {
            data = $.parseJSON(data);
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
                    data = $.parseJSON(data);
                    $.jGrowl(data["message"])
                }
           });
        }
    });
}

$(function() {
    update_editor();
    $(".button").button();
    var message = $.cookie("message");

    if (message != null) {
        $.jGrowl(message);
        $.cookie("message", null, { path: '/' });
    };

    $('ul.sf-menu').superfish({
        speed: "fast",
        delay: "200"
    });

    $(".popup-link").live("click", function() {
        var url = $(this).attr("href");
        popup(url, "1024", "1000");
        return false;
    });

    // General product tabs
    $('#manage-tabs').tabs();
    $('#manage-tabs').show();

    // Product tabs
    $('#product-tabs').tabs();
    $('#product-tabs').show();

    $('#product-tabs').bind('tabsshow', function(event, ui) {
        $.cookie("product_tab", ui.index);
    });
    var product_tab_cookie = $.cookie("product_tab");
    index = (product_tab_cookie != null) ? parseInt(product_tab_cookie) : 0;
    $('#product-tabs').tabs('select', index)

    // Category tabs
    $('#category-tabs').tabs();
    $('#category-tabs').show();
    $('#category-tabs').bind('tabsshow', function(event, ui) {
        $.cookie("category_tab", ui.index);
    });
    var category_tab_cookie = $.cookie("category_tab");
    index = (category_tab_cookie != null) ? parseInt(category_tab_cookie) : 0;
    $('#category-tabs').tabs('select', index)

    $("#dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        width: 800,
        height: 680,
        draggable: false,
        resizable: false,
        position: ["center", 200]
    });

    // Generic ajax save button
    $(".ajax-save-button").live("click", function() {
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
        $('body').trigger(event);

        var action = $(this).attr("name")
        form.ajaxSubmit({
            data : {"action" : action},
            success : function(data) {
                data = $.parseJSON(data);
                for (var html in data["html"]) {
                    $(data["html"][html][0]).html(data["html"][html][1]);
                }
                if (data["close-dialog"]) {
                    $("#delete-dialog").dialog("close");
                    $("#dialog").dialog("close");
                }
                if (data["message"]) {
                    $.jGrowl(data["message"]);
                }
                hide_ajax_loading();
                update_editor();
                setup_datepicker();

                // trigger form-save-end event when new HTML has already been injected into page
                var event = jQuery.Event("form-save-end");
                event.form_id = form_id;
                $('body').trigger(event);
            }
        })
        return false;
    });

    // Generic ajax link
    $(".ajax-link").live("click", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            data = $.parseJSON(data);
            for (var html in data["html"])
                $(data["html"][html][0]).html(data["html"][html][1]);
            if (data["message"]) {
                $.jGrowl(data["message"]);
            }
            if (data["open-dialog"]) {
                $("#dialog").dialog("open");
            }
        })
        return false;
    });

    // Generic ajax input on keyup
    $(".refresh-on-keyup").live("keyup", function() {
        send_form_and_refresh($(this));
    });

    $(".refresh-on-change").live("change", function() {
        send_form_and_refresh($(this));
    });

    // Generic select all checkbox
    $(".select-all").live("click", function() {
        var checked = this.checked;
        var selector = ".select-" + $(this).attr("value")
        $(selector).each(function() {
            this.checked = checked;
        });
    });

    $(".toggle-all").live("click", function() {
        var selector = ".toggle-" + $(this).attr("data")
        $(selector).each(function() {
            this.checked = !this.checked;
        });
    });

    // Criteria
    $(".criterion-add-first-button").live("click", function() {
        var position = $(this).siblings(".position").val()
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $(".criteria").prepend(data);
            update_positions();
        });
        return false;
    });

    $(".criterion-add-button").live("click", function() {
        var criterion = $(this).parents("tr:first");
        var url = $(this).attr("href");
        $.post(url, function(data) {
            criterion.after(data);
            update_positions();
        });
        return false
    });

    $("select.criterion-type").live("change", function() {
        var type = $(this).selected().val();
        var target = $(this).parents("tr:first");
        $.post("/manage/change-criterion", {"type" : type}, function(data) {
            target.replaceWith(data);
            update_positions();
        });
    });

    $(".criterion-delete-button").live("click", function() {
        $(this).parents("tr.criterion:first").remove();
    });

    // Portlets
    $(".portlet-edit-button").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#dialog").html(data);
            $("#dialog").dialog("open");
            addEditor('#id_portlet-text', true, 300);
        });
        return false;
    });

    $(".portlet-add-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                $("#dialog").html(data);
                $("#dialog").dialog("open");
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
                data = $.parseJSON(data);
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

    $(".category-ajax-link").live("click", function() {
        var url = $(this).attr("href");

        // Loads children of clicked category.
        if ($(this).hasClass("collapsed")) {
            $.post(url, function(data) {
                data = $.parseJSON(data);
                for (var html in data["html"])
                    $(data["html"][html][0]).html(data["html"][html][1]);
            })
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

    $(".export-category-input").live("click", function() {

        // select / deselect all child nodes
        var input = $(this);
        var parent_checked = this.checked;
        $(this).parent().find("input").each(function() { this.checked = parent_checked; })

        // Updates child and parent categories of clicked category
        var url = $(this).attr("data");
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

    $(".export-product-input").live("click", function() {
        // Add / Remove product
        var input = $(this);
        var url = $(this).attr("data");
        var checked = this.checked;

        // Updates parent catgories of clicked product
        if (checked == true) {
            $.post(url, {"action" : "add"}, function(data) { update_parent_categories(input) } );
        }
        else {
            $.post(url, {"action" : "remove"}, function(data) { update_parent_categories(input) });
        }
    });

    $(".category-variants-options").live("change", function() {
        var url = $(this).attr("data");
        var variants_option = $(this).val();
        $.post(url, { "variants_option" : variants_option });
    });

    // No results
    var toggle_no_results = function(checked) {
        if (checked) {
            $("#id_display_no_results").parents(".field").show();
        }
        else {
            $("#id_display_no_results").parents(".field").hide();
        }
    }
    toggle_no_results($("#id_filterable").attr("checked"));
    $("#id_filterable").click(function() {
        toggle_no_results(this.checked)
    });

    // Required
    var toggle_required = function(checked) {
        if (checked) {
            $("#id_required").parents(".field").show();
        }
        else {
            $("#id_required").parents(".field").hide();
        }
    }
    toggle_required($("#id_configurable").attr("checked"));
    $("#id_configurable").click(function() {
        toggle_required(this.checked)
    });

    $("#delete-dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        draggable: false,
        resizable: false,
        position: ["center", 200]
    });

    $(".delete-link").live("click", function() {
        $("#delete-dialog > form").attr("action", $(this).attr("href"));
        $("#delete-dialog > p.message").html($(this).attr("dialog_message"));
        $(".dialog-yes-button").addClass($(this).attr("dialog_yes_button_class"));
        $("#delete-dialog").dialog("open");
        return false;
    });

    $(".dialog-close-button").live("click", function() {
        $("#delete-dialog").dialog("close");
        return false;
    });

    $("input.button").button();

    $(".property-edit-mode").live("click", function() {
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
    })

    setup_datepicker();

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
                    data = $.parseJSON(data);
                    $.jGrowl(data["message"])
                }
           });
        }
    });

    $("#insert-image").live("click", function(e) {
        var url = $("input.image:checked").attr("value");
        var size = $("#image-size").val();
        var klass = $("#image-class").val();

        if (size)
            url = url.replace("100x100", size);
        else
            url = url.replace(".100x100", "");

        if (klass)
            html = "<img class='" + klass + "' src='" + url + "' />"
        else
            html = "<img src='" + url + "' />"

        insertHTML(html);
        $("#dialog").dialog("close");
        return false;
    })
})

$(document).ajaxComplete(function() {
    $(".button").button();
})

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
