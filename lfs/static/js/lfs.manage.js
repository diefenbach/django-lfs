function popup(url, w, h) {
    w = window.open(url, "Preview", "height=" + h +", width=" + w +", screenX=500, screenY=150, scrollbars=yes, resizable=yes");
    w.focus();
}

function disable_enter_key(e) {
     var key;
     if(window.event)
          key = window.event.keyCode;
     else
          key = e.which;
     if(key == 13)
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

$(function() {
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

    // Product tabs
    $('#product-tabs').tabs();
    $('#product-tabs').bind('tabsshow', function(event, ui) {
        $.cookie("product_tab", ui.index);
    });
    var product_tab_cookie = $.cookie("product_tab");
    index = (product_tab_cookie != null) ? parseInt(product_tab_cookie) : 0;
    $('#product-tabs').tabs('select', index)

    // Category tabs
    $('#category-tabs').tabs();
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
        position: ["center", 200],
    });

    $("#product-name-filter").live("keyup", function(evt) {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                data = $.parseJSON(data);
                for (var html in data["html"])
                    $(data["html"][html][0]).html(data["html"][html][1]);

                if (data["message"]) {
                    $.jGrowl(data["message"]);
                }
            }
        })
        return false;
    });

    // Generic ajax save button
    $(".ajax-save-button").live("click", function() {
        show_ajax_loading();
        var action = $(this).attr("name")
        $(this).parents("form:first").ajaxSubmit({
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
        })
        return false;
    });

    // Criteria
    $(".edit-price-criteria-button").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#dialog").html(data);
            $("#dialog").dialog("open");
        })
        return false;
    });

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

    $(".criterion-save-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                data = $.parseJSON(data);
                $("#criteria").html(data["criteria"]);
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    $(".price-criterion-save-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                data = $.parseJSON(data);
                $("#prices").html(data["prices"]);
                $("#price-criteria").html(data["criteria"]);
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    $(".criterion-delete-button").live("click", function() {
        $(this).parents("tr.criterion:first").remove();
    });

    // General
    $(".select-all").live("click", function() {
        var checked = this.checked;
        var selector = ".select-" + $(this).attr("value")
        $(selector).each(function() {
            this.checked = checked;
        });
    });

    // Categories / Products
    $(".category-products-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#products-inline").html(data)
        });
        return false;
    });

    $(".category-products-filter-input").live("keyup", function() {
        $("#category-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".category-products-amount").live("change", function() {
        $("#category-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".category-products-categories-filter").live("change", function() {
        $("#category-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".category-selected-products-filter-input").live("keyup", function() {
        $("#category-selected-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selected-products").html(data);
            }
        });
    });

    $(".category-products-categories-filter-2").live("change", function() {
        $("#category-selected-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selected-products").html(data);
            }
        });
    });

    // Categories / SEO
    $(".category-seo-button").live("click", function() {
        $("#category-seo-form").ajaxSubmit({
            success: function(data) {
                data = $.parseJSON(data);
                $("#seo").html(data["seo"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Products (Overview)
    $(".products-name-filter").live("keyup", function() {
        var form = $(this).parents("form:first");

        try { clearTimeout(timeout); } catch(e) {}

        timeout = setTimeout(function() {
            form.ajaxSubmit({
                "success": function(data) {
                    $("#products-inline").html(data);
                }
            });
        }, 500);
    });

    $(".products-reset-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#products-inline").html(data);
            $(".products-name-filter").val("")
            $(".products-category-filter option:selected").attr("selected", false)
            $(".products-category-filter option:first").attr("selected", true)
        });
        return false;
    });

    // Product / Selectable Products
    $("#selectable-products-filter-input").live("keyup", function() {
        $("#selectable-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selectable-products").html(data);
            }
        });
    });

    $(".selectable-products-category-filter").live("change", function() {
        $("#selectable-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selectable-products").html(data);
            }
        });
    });

    $(".selectable-products-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#selectable-products").html(data)
        });
        return false;
    });

    $(".selectable-products-reset-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#selectable-products-filter-input").val("");
            $(".selectable-products-category-filter option:selected").attr("selected", false)
            $(".selectable-products-category-filter option:first").attr("selected", true)
            $("#selectable-products").html(data)
        });
        return false;
    });

    // Product / Images
    $(".upload-file:last").live("change", function() {
        var name = $(this).attr("name");
        var number = parseInt(name.split("_")[1])
        number += 1;
        $(this).parent().after("<div><input type='file' class='upload-file' name='file_" + number + "' /></div>");
    });

    $("#product-images-save-button").live("click", function() {
        $("#product-images-form").ajaxSubmit({
            target : "#images"
        });
        return false;
    });

    $(".product-images-update-button").live("click", function() {
        var action = $(this).attr("name")
        $("#product-images-update-form").ajaxSubmit({
            data : {"action" : action},
            success : function(data) {
                var data = $.parseJSON(data)
                $("#images").html(data["images"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Product / Data
    $("#product-data-save-button").live("click", function() {
        tinymce.triggerSave();
        $("#product-data-form").ajaxSubmit({
            "success": function(data) {
                data = $.parseJSON(data)
                $("#data").html(data["form"]);
                $("#selectable-products").html(data["selectable_products"]);
                $.jGrowl(data["message"])
            }
        });
        return false;
    })

    // Product / Categories
    $(".product-categories-save-button").live("click", function() {
        $("#product-categories-save-form").ajaxSubmit({
            success: function(data) {
                var data = $.parseJSON(data)
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Product / Accessories
    $(".accessories-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#accessories-inline").html(data)
        });
        return false;
    });

    $(".filter-accessories-input").live("keyup", function() {
        $("#filter-accessories-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                $("#accessories-inline").html(data);
            }
        });
    });

    $(".accessories-categories-filter").live("change", function() {
        $("#filter-accessories-form").ajaxSubmit({
            "target": "#accessories-inline",
            "success": function(data) {
                $("#accessories-inline").html(data);
            }
        });
    });

    $("#accessories-amount").live("change", function() {
        $("#filter-accessories-form").ajaxSubmit({
            "target": "#accessories-inline",
            "success": function(data) {
            }
        });
    });

    // Product / Related Products
    $(".related-products-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#related-products-inline").html(data)
        });
        return false;
    });

    $(".filter-related-products-input").live("keyup", function() {
        $("#filter-related-products-form").ajaxSubmit({
            target: "#related-products-inline"
        });
        return false;
    });

    $(".related-products-categories-filter").live("change", function() {
        $("#filter-related-products-form").ajaxSubmit({
            "success": function(data) {
                $("#related-products-inline").html(data);
            }
        });
    });

    $("#related-products-amount").live("change", function() {
        $("#filter-related-products-form").ajaxSubmit({
            "target": "#related-products-inline"
        });
    });

    // Select products
    $("input.select-1").live("click", function(e) {
        if ($(this).is(":checked")) {
            $(this).parents("tr:first").addClass("marked");

            if (e.shiftKey) {
                var tr = $(this).parents("tr:first");
                tr.prevAll("tr").each(function() {
                    if ($(this).hasClass("marked")) {
                        return false;
                    }
                    $(this).addClass("marked");
                    $(this).find("input.select-1").attr("checked", true);
                })
            }

        }
        else {
            $(this).parents("tr:first").removeClass("marked");

            if (e.shiftKey) {
                var tr = $(this).parents("tr:first");
                tr.prevAll("tr").each(function() {
                    if ($(this).hasClass("marked") == false) {
                        return false;
                    }
                    $(this).removeClass("marked");
                    $(this).find("input.select-1").attr("checked", false);
                })
            }
        }
    });

    // Product / SEO
    $(".seo-save-button").live("click", function() {
        $("#product-seo-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                var data = $.parseJSON(data)
                $("#seo-inline").html(data["seo_inline"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Shipping/Payment Price
    $(".price-button").live("click", function() {
        var action = $(this).attr("name");
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = $.parseJSON(data)
                $("#prices").html(data["prices"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Product / Dimension
    $(".product-stock-button").live("click", function() {
        $("#product-stock-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                var data = $.parseJSON(data);
                $("#stock").html(data["html"]);
                DateTimeShortcuts.init();
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // PropertyGroup
    // PropertyGroup / Products
    $(".products-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#products-inline").html(data)
        });
        return false;
    });

    $(".filter-products-input").live("keyup", function() {
        $("#filter-products-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".products-categories-filter").live("change", function() {
        $("#filter-products-form").ajaxSubmit({
            "target": "#products-inline"
        });
    });

    // PropertyGroup / Product Property Values
    // Shop Property Options
    $(".shop-property-add-option-button").live("click", function() {
        var action = $(this).attr("name");
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = $.parseJSON(data)
                $("#options").html(data["options"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Shop Property Steps
    $(".shop-property-add-step-button").live("click", function() {
        var action = $(this).attr("name");
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = $.parseJSON(data)
                $("#steps").html(data["steps"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    $(".shop-property-save-step-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success: function(data) {
                data = $.parseJSON(data)
                $("#steps").html(data["steps"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    $(".shop-property-save-step-type-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success: function(data) {
                data = $.parseJSON(data)
                $("#steps").html(data["steps"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Static blocks
    var confirmation;
    $(".confirmation-link-no").live("click", function() {
        $(this).parent().replaceWith(confirmation);
        return false;
    });

    $(".confirmation-link").live("click", function() {
        confirmation = $(this);
        var url = $(this).attr("href");
        var data = $(this).attr("data");
        var cls = $(this).attr("class");
        $(this).replaceWith("<span><span class='" + cls + "'>" + data + "</span> <a href='" + url + "'>Yes</a> <a class='confirmation-link-no' href=''>No</a></span>");
        return false;
    });

    // Portlets
    $(".portlet-edit-button").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#dialog").html(data);
            $("#dialog").dialog("open");
            $(".button").button();
        });
        return false;
    });

    $(".portlet-add-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                $("#dialog").html(data);
                $("#dialog").dialog("open");
                $(".button").button();
        }});
        return false;
    });

    $(".ajax-portlet-save-button").live("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                $("#dialog").dialog("close");
                data = $.parseJSON(data);
                $("#portlets").html(data["html"])
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    // Marketing / Topseller
    $(".topseller-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#topseller-inline").html(data)
        });
        return false;
    });

    $(".filter-topseller-input").live("keyup", function() {
        $("#filter-topseller-form").ajaxSubmit({
            target: "#topseller-inline"
        });
        return false;
    });

    $(".topseller-categories-filter").live("change", function() {
        $("#filter-topseller-form").ajaxSubmit({
            "success": function(data) {
                $("#topseller-inline").html(data);
            }
        });
    });

    $("#topseller-amount").live("change", function() {
        $("#filter-topseller-form").ajaxSubmit({
            "target": "#topseller-inline"
        });
    });

    // Marketing / Featured
    $(".featured-page-link").live("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#featured-inline").html(data)
        });
        return false;
    });

    $(".filter-featured-input").live("keyup", function() {
        $("#filter-featured-form").ajaxSubmit({
            target: "#featured-inline"
        });
        return false;
    });

    $(".featured-categories-filter").live("change", function() {
        $("#filter-featured-form").ajaxSubmit({
            "success": function(data) {
                $("#featured-inline").html(data);
            }
        });
    });

    $("#featured-amount").live("change", function() {
        $("#filter-featured-form").ajaxSubmit({
            "target": "#featured-inline"
        });
    });

    // Shop
    $("#shop-default-values-button").live("click", function() {
        $("#shop-default-values-form").ajaxSubmit({
            "success": function(data) {
                var data = $.parseJSON(data)
                $("#default-values").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

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

    $(function() {
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
    });

    $(".category-variants-options").live("change", function() {
        var url = $(this).attr("data");
        var variants_option = $(this).val();
        $.post(url, { "variants_option" : variants_option });
    });

    // Product / Properties Form

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
        position: ["center", 200],
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