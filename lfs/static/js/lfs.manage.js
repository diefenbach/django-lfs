tinyMCE.init({
    mode: "none",
    theme : "advanced",
    height : "400",
    tab_focus : ":prev,:next",
    button_tile_map : true,
    plugins : "safari, fullscreen",
    convert_urls : false,
    forced_root_block : "",
    theme_advanced_buttons1 : "bold, italic, underline, |, justifyleft," +
                              "justifycenter, justifyright, justifyfull, |," +
                              "bullist,numlist, |, outdent, indent, |, image, |, undo," +
                              "redo, |, code, link, unlink, styleselect, formatselect, |," +
                              "removeformat, fullscreen",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",
    theme_advanced_buttons4: "",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    content_css : "/media/tinymce_styles.css"
})

function mark_selected() {
    $("ul.manage-categories a").each(function() {
        $(this).css("font-weight", "normal");
    });

    $("ul.manage-categories input:checked").each(function() {
        $(this).parents("li:gt(0)").each(function() {
            $(this).children("a:first").css("font-weight", "bold");
        });
    });
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

    $('#manage-tabs > ul').tabs({ cookie: { expires: 30 } });

    $("#dialog").dialog({
        autoOpen: false,
        closeOnEscape: true,
        modal: true,
        width: 800,
        height: 600,
        overlay: {
            opacity: 0.7,
            background: "black"
        }
    });

    // Generic ajax save button
    $(".ajax-save-button").livequery("click", function() {
        var action = $(this).attr("name")
        tinyMCE.execCommand('mceRemoveControl', false, 'id_text');
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success : function(data) {
                data = JSON.parse(data);
                for (var html in data["html"])
                    $(data["html"][html][0]).html(data["html"][html][1]);
                tinyMCE.execCommand('mceAddControl', true, 'id_text');
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    // Generic ajax save button
    $(".ajax-save-button-2").livequery("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                data = JSON.parse(data);
                for (var html in data["html"])
                    $(data["html"][html][0]).html(data["html"][html][1]);

                if (data["message"]) {
                    $.jGrowl(data["message"]);
                }
            }
        })
        return false;
    });

    // Generic ajax link
    $(".ajax-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            data = JSON.parse(data);
            for (var html in data["html"])
                $(data["html"][html][0]).html(data["html"][html][1]);

            if (data["message"]) {
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    // Criteria
    $(".edit-price-criteria-button").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#dialog").html(data);
            $("#dialog").dialog("open");
        })
        return false;
    });

    $(".criterion-add-first-button").livequery("click", function() {
        var position = $(this).siblings(".position").val()
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $(".criteria").prepend(data);
            update_positions();
        });
        return false;
    });

    $(".criterion-add-button").livequery("click", function() {
        var criterion = $(this).parents("tr:first");
        var url = $(this).attr("href");
        $.post(url, function(data) {
            criterion.after(data);
            update_positions();
        });
        return false
    });

    $("select.criterion-type").livequery("change", function() {
        var type = $(this).selected().val();
        var target = $(this).parents("tr:first");
        $.post("/manage/change-criterion", {"type" : type}, function(data) {
            target.replaceWith(data);
            update_positions();
        });
    });

    $(".criterion-save-button").livequery("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                data = JSON.parse(data);
                $("#criteria").html(data["criteria"]);
                $.jGrowl(data["message"]);
                // $(':input', "form").bind("change", function() { setConfirmUnload(false); });
            }
        })
        return false;
    });

    $(".price-criterion-save-button").livequery("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                data = JSON.parse(data);
                $("#prices").html(data["prices"]);
                $("#price-criteria").html(data["criteria"]);
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    $(".criterion-delete-button").livequery("click", function() {
        $(this).parents("tr.criterion:first").remove();
    });

    // General
    $(".delete-all").livequery("click", function() {
        var checked = this.checked;
        $(".delete").each(function() {
            this.checked = checked;
        });
    });

    $(".select-all-1").livequery("click", function() {
        var checked = this.checked;
        $(".select-1").each(function() {
            this.checked = checked;
        });
    });

    $(".select-all-2").livequery("click", function() {
        var checked = this.checked;
        $(".select-2").each(function() {
            this.checked = checked;
        });
    });

    $("ul.menu").sortable({
        items : ">li",
        axis: "y",
        update : function(evt, el) {
            var id = $(this).attr("id");
            var categories = $(this).sortable("toArray", {});
            $.post("/shops/manage/update-category/" + id, {"categories" : categories}, function(data) {
                $.jGrowl("Categories has been updated.");
            });
        }
    });

    // Categories / Products
    $(".category-products-page-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#products-inline").html(data)
        });
        return false;
    });

    $(".category-products-add-button").livequery("click", function() {
        $("#category-products-add-form").ajaxSubmit({
            success: function(data) {
                var data = JSON.parse(data);
                $("#products-inline").html(data["products"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".category-products-remove-button").livequery("click", function() {
        $("#category-products-remove-form").ajaxSubmit({
            success: function(data) {
                $("#products-inline").html(data);
                $.jGrowl("Produkte wurden von Kategorie entfernt.");
            }
        });
        return false;
    });

    $(".category-products-filter-input").livequery("keyup", function() {
        $("#category-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".category-products-categories-filter").livequery("change", function() {
        $("#category-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".category-selected-products-filter-input").livequery("keyup", function() {
        $("#category-selected-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selected-products").html(data);
            }
        });
    });

    $(".category-products-categories-filter-2").livequery("change", function() {
        $("#category-selected-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selected-products").html(data);
            }
        });
    });

    // Categories / SEO
    $(".category-seo-button").livequery("click", function() {
        $("#category-seo-form").ajaxSubmit({
            success: function(data) {
                data = JSON.parse(data);
                $("#seo").html(data["seo"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Products (Overview)
    $(".products-name-filter").livequery("keyup", function() {
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

    $(".products-reset-link").livequery("click", function() {
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
    $("#selectable-products-filter-input").livequery("keyup", function() {
        $("#selectable-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selectable-products").html(data);
            }
        });
    });

    $(".selectable-products-category-filter").livequery("change", function() {
        $("#selectable-products-filter-form").ajaxSubmit({
            "success": function(data) {
                $("#selectable-products").html(data);
            }
        });
    });

    $(".selectable-products-page-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#selectable-products").html(data)
        });
        return false;
    });

    $(".selectable-products-reset-link").livequery("click", function() {
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
    $(".upload-file:last").livequery("change", function() {
        var name = $(this).attr("name");
        var number = parseInt(name.split("_")[1])
        number += 1;
        $(this).parent().after("<div><input type='file' class='upload-file' name='file_" + number + "' /></div>");
    });

    $("#product-images-save-button").livequery("click", function() {
        $("#product-images-form").ajaxSubmit({
            target : "#images"
        });
        return false;
    });

    $(".product-images-update-button").livequery("click", function() {
        var action = $(this).attr("name")
        $("#product-images-update-form").ajaxSubmit({
            data : {"action" : action},
            success : function(data) {
                var data = JSON.parse(data)
                $("#images").html(data["images"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Product / Data
    $("#product-data-save-button").livequery("click", function() {
        tinyMCE.execCommand('mceRemoveControl', false, 'id_short_description');
        tinyMCE.execCommand('mceRemoveControl', false, 'id_description');
        $("#product-data-form").ajaxSubmit({
            "success": function(data) {
                data = JSON.parse(data)
                $("#data").html(data["form"]);
                $("#selectable-products").html(data["selectable_products"]);
                tinyMCE.execCommand('mceAddControl', true, 'id_description');
                tinyMCE.execCommand('mceAddControl', true, 'id_short_description');
                $.jGrowl(data["message"])
            }
        });
        return false;
    })

    // Product / Categories
    $(".product-categories-save-button").livequery("click", function() {
        $("#product-categories-save-form").ajaxSubmit({
            success: function(data) {
                var data = JSON.parse(data)
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Mark parent categories with selected children categories
    $(".product-categories-save-button").livequery("click", function() {
        mark_selected()
    })

    // Show selected categories - expands all categories which have a selected
    // sub category.
    $(".show-selected").livequery("click", function() {

        $("a:eq(0)", "#manage-product-categories-control").click()

        $("ul.manage-categories input:checked").parents("ul.manage-categories:hidden").each(function() {
            $(this).show()
        });

        $("ul.manage-categories input:checked").parents("li.expandable:gt(0)").each(function() {
            $(this).removeClass("expandable");
            $(this).addClass("collapsable");
        });

        $("ul.manage-categories input:checked").parents("li:gt(0)").children(".hitarea").each(function() {
            $(this).removeClass("expandable-hitarea");
            $(this).addClass("collapsable-hitarea");
        });

        return false;
    })

    // Shows current category in category manage tree (manage category)
    $(".show-current").livequery("click", function() {

        $("a:eq(0)", "#manage-categories-categories-control").click()

        var category = $("#manage-tabs").attr("data")
        $(category).parents("ul.menu:hidden").each(function() {
            $(this).show()
        });

        $(category).parents("li.expandable").each(function() {
            $(this).removeClass("expandable");
            $(this).addClass("collapsable");
        });

        $(category).parents("li.lastExpandable").each(function() {
            $(this).addClass("lastCollapsable");
            $(this).removeClass("lastExpandable");
        });

        $(category).parents("li").children(".hitarea").each(function() {
            $(this).removeClass("expandable-hitarea");
            $(this).addClass("collapsable-hitarea");
        });

        return false;
    })

    // Product / Variants
    $(".property-add-button").livequery("click", function() {
        $("#property-add-form").ajaxSubmit({
            success: function(data) {
                $("#variants").html(data);
            }
        });
        return false;
    });

    $(".variants-add-button").livequery("click", function() {
        $(".variants-add-form").ajaxSubmit({
            success: function(data) {
                data = JSON.parse(data);
                $("#variants").html(data["properties"]);
                $("#selectable-products").html(data["selectable_products"]);
            }
        });
        return false;
    })

    $(".variants-update-button").livequery("click", function() {
        var action = $(this).attr("name")
        $("#variants-form").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = JSON.parse(data)
                $("#variants").html(data["properties"]);
                $("#selectable-products").html(data["selectable_products"]);
            }
        })
        return false;
    });

    $(".option-add-button").livequery("click", function() {
        var form = $(this).parents("form:first");
        form.ajaxSubmit({
            "success": function(data) {
                $("#variants").html(data);
            }
        });
        return false;
    })

    $(".property-change-button").livequery("click", function() {
        var href = $(this).attr("href")
        $.post(href, function(data) {
            $("#variants").html(data);
        });
        return false;
    })

    // Product / Accessories
    $("#add-accessories-button").livequery("click", function() {
        $("#add-accessories-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data);
                $("#accessories-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".accessories-update-button").livequery("click", function() {
        var action = $(this).attr("name");
        $("#accessories-update-form").ajaxSubmit({
            data : {"action" : action},
            success : function(data) {
                var data = JSON.parse(data);
                $("#accessories-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".accessories-page-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#accessories-inline").html(data)
        });
        return false;
    });

    $(".filter-accessories-input").livequery("keyup", function() {
        $("#filter-accessories-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                $("#accessories-inline").html(data);
            }
        });
    });

    $(".accessories-categories-filter").livequery("change", function() {
        $("#filter-accessories-form").ajaxSubmit({
            "target": "#accessories-inline"
        });
    });

    $("#accessories-amount").livequery("change", function() {
        $("#filter-accessories-form").ajaxSubmit({
            "target": "#accessories-inline"
        });
    });

    // Product / Related Products
    $("#add-related-products-button").livequery("click", function() {
        $("#add-related-products-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data)
                $("#related-products-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $("#remove-related-products-button").livequery("click", function() {
        $("#remove-related-products-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data);
                $("#related-products-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".related-products-update-button").livequery("click", function() {
        $("#related-products-update-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data);
                $("#related-products-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    $(".related-products-page-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#related-products-inline").html(data)
        });
        return false;
    });

    $(".filter-related-products-input").livequery("keyup", function() {
        $("#filter-related-products-form").ajaxSubmit({
            target: "#related-products-inline"
        });
        return false;
    });

    $(".related-products-categories-filter").livequery("change", function() {
        $("#filter-related-products-form").ajaxSubmit({
            "success": function(data) {
                $("#related-products-inline").html(data);
            }
        });
    });

    // Select products
    $("input.select-1").livequery("click", function(e) {
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
    $(".seo-save-button").livequery("click", function() {
        $("#product-seo-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                var data = JSON.parse(data)
                $("#seo-inline").html(data["seo_inline"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Shipping/Payment Price
    $(".price-button").livequery("click", function() {
        var action = $(this).attr("name");
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = JSON.parse(data)
                $("#prices").html(data["prices"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Product / Dimension
    $(".product-stock-button").livequery("click", function() {
        $("#product-stock-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                var data = JSON.parse(data);
                $("#stock").html(data["html"]);
                DateTimeShortcuts.init();
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // PropertyGroup
    $("#add-property-button").livequery("click", function() {
        $("#add-property-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data)
                $("#properties").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".property-group-update-button").livequery("click", function() {
        var action = $(this).attr("name");
        $("#property-group-update-form").ajaxSubmit({
            data : {"action" : action},
            success : function(data) {
                var data = JSON.parse(data);
                $("#properties").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // PropertyGroup / Products
    $("#add-products-button").livequery("click", function() {
        $("#add-products-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data);
                $("#products-inline").html(data["products_inline"]);
                $("#product-values").html(data["product_values_inline"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".products-update-button").livequery("click", function() {
        $("#products-update-form").ajaxSubmit({
            success : function(data) {
                var data = JSON.parse(data);
                $("#products-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".products-page-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#products-inline").html(data)
        });
        return false;
    });

    $(".filter-products-input").livequery("keyup", function() {
        $("#filter-products-form").ajaxSubmit({
            "type": "post",
            "success": function(data) {
                $("#products-inline").html(data);
            }
        });
    });

    $(".products-categories-filter").livequery("change", function() {
        $("#filter-products-form").ajaxSubmit({
            "target": "#products-inline"
        });
    });

    // PropertyGroup / Product Property Values
    $("#update-product-values-button").livequery("click", function() {
        $("#update-product-values-form").ajaxSubmit({
            success : function(data) {
                var data = JSON.parse(data);
                $("#product-values").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    // Shop Property Options
    $(".shop-property-add-option-button").livequery("click", function() {
        var action = $(this).attr("name");
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = JSON.parse(data)
                $("#options").html(data["options"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Shop Property Steps
    $(".shop-property-add-step-button").livequery("click", function() {
        var action = $(this).attr("name");
        $(this).parents("form:first").ajaxSubmit({
            data : {"action" : action},
            success: function(data) {
                data = JSON.parse(data)
                $("#steps").html(data["steps"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    $(".shop-property-save-step-button").livequery("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success: function(data) {
                data = JSON.parse(data)
                $("#steps").html(data["steps"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    $(".shop-property-save-step-type-button").livequery("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success: function(data) {
                data = JSON.parse(data)
                $("#steps").html(data["steps"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    // Static blocks
    var confirmation;
    $(".confirmation-link-no").livequery("click", function() {
        $(this).parent().replaceWith(confirmation);
        return false;
    });

    $(".confirmation-link").livequery("click", function() {
        confirmation = $(this);
        var url = $(this).attr("href");
        var data = $(this).attr("data");
        var cls = $(this).attr("class");
        $(this).replaceWith("<span><span class='" + cls + "'>" + data + "</span> <a href='" + url + "'>Yes</a> <a class='confirmation-link-no' href=''>No</a></span>");
        return false;
    });

    // Portlets
    $(".portlet-edit-button").livequery("click", function() {
        tinyMCE.execCommand('mceRemoveControl', false, 'id_portlet-text');
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#dialog").html(data);
            $("#dialog").dialog("open");
            tinyMCE.execCommand('mceAddControl', true, 'id_portlet-text');
        });
        return false;
    });

    $(".portlet-add-button").livequery("click", function() {
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                $("#dialog").html(data);
                $("#dialog").dialog("open");
                tinyMCE.execCommand('mceAddControl', true, 'id_portlet-text');
        }});
        return false;
    });

    $(".ajax-portlet-save-button").livequery("click", function() {
        tinyMCE.execCommand('mceRemoveControl', false, 'id_portlet-text');
        $(this).parents("form:first").ajaxSubmit({
            success : function(data) {
                $("#dialog").dialog("close");
                data = JSON.parse(data);
                $("#portlets").html(data["html"])
                $.jGrowl(data["message"]);
            }
        })
        return false;
    });

    // Marketing / Topseller
    $("#add-topseller-button").livequery("click", function() {
        $("#add-topseller-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data)
                $("#topseller-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    })

    $(".topseller-update-button").livequery("click", function() {
        var action = $(this).attr("name");
        $("#topseller-update-form").ajaxSubmit({
            data : {"action" : action},
            "success": function(data) {
                var data = JSON.parse(data);
                $("#topseller-inline").html(data["html"]);
                $.jGrowl(data["message"]);
            }
        });
        return false;
    });

    $(".topseller-page-link").livequery("click", function() {
        var url = $(this).attr("href");
        $.get(url, function(data) {
            $("#topseller-inline").html(data)
        });
        return false;
    });

    $(".filter-topseller-input").livequery("keyup", function() {
        $("#filter-topseller-form").ajaxSubmit({
            target: "#topseller-inline"
        });
        return false;
    });

    $(".topseller-categories-filter").livequery("change", function() {
        $("#filter-topseller-form").ajaxSubmit({
            "success": function(data) {
                $("#topseller-inline").html(data);
            }
        });
    });

    // Shop
    $("#shop-default-values-button").livequery("click", function() {
        $("#shop-default-values-form").ajaxSubmit({
            "success": function(data) {
                var data = JSON.parse(data)
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
                data = JSON.parse(data);
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
        $(".category-ajax-link").livequery("click", function() {
            var url = $(this).attr("href");

            // Loads children of clicked category.
            if ($(this).hasClass("collapsed")) {
                $.post(url, function(data) {
                    data = JSON.parse(data);
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

        $(".export-category-input").livequery("click", function() {

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

        $(".export-product-input").livequery("click", function() {
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

    $(".category-variants-options").livequery("change", function() {
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

})
