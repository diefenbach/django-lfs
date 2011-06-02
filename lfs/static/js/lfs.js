// popup #################################################################
function popup(url, w, h) {
    w = window.open(url, "Preview", "height=" + h +", width=" + w +", screenX=500, screenY=150, scrollbars=yes, resizable=yes");
    w.focus();
}

// Update checkout
var update_checkout = function() {
    var data = $(".checkout-form").ajaxSubmit({
        url : $(".checkout-form").attr("data"),
        "success" : function(data) {
            var data = $.parseJSON(data);
            $("#cart-inline").html(data["cart"]);
            $("#shipping-inline").html(data["shipping"]);
            $("#payment-inline").html(data["payment"]);
        }
    });
}

$(function() {
    // Delay plugin taken from ###############################################
    // http://ihatecode.blogspot.com/2008/04/jquery-time-delay-event-binding-plugin.html

   $.fn.delay = function(options) {
        var timer;
        var delayImpl = function(eventObj) {
            if (timer != null) {
                clearTimeout(timer);
            }
            var newFn = function() {
                options.fn(eventObj);
            };
            timer = setTimeout(newFn, options.delay);
        }

        return this.each(function() {
            var obj = $(this);
            obj.bind(options.event, function(eventObj) {
                 delayImpl(eventObj);
            });
        });
    };
    
    // Message ################################################################

    var message = $.cookie("message");

    if (message != null) {
        $.jGrowl(message);
        $.cookie("message", null, { path: '/' });
    };

    // Rating #################################################################
    $(".rate").click(function() {
        $(".rate").each(function() {
            $(this).removeClass("current-rating")
        });

        $(this).addClass("current-rating");

        $("#id_score").val($(this).attr("data"));
    });

    // General ################################################################
    // $().ajaxSend(function(r,s){
    //     $("#spinner").show()
    // });
    //
    // $().ajaxStop(function(r,s){
    //     $("#spinner").hide()
    // });

    // Product ################################################################

    $("a.product-image").lightBox({
        "txtImage" : "Image",
        "txtOf" : " of "
    });

    // Hack to make the change event on radio buttons for IE working
    // http://stackoverflow.com/questions/208471/getting-jquery-to-recognise-change-in-ie
    if ($.browser.msie) {
        $("input.variant").live("click", function() {
            this.blur();
            this.focus();
        });
    };

    $("input.variant").live("change", function() {
        var url = $(this).parents("table.product-variants").attr("data");
        var variant_id = $(this).attr("value");
        $("#product-form").ajaxSubmit({
            url : url,
            data : {"variant_id" : variant_id},
            success : function(data) {
                var data = $.parseJSON(data);
                $("#product-inline").html(data["product"]);
                $.jGrowl(data["message"]);

                // Re-bind lightbox
                $("a.product-image").lightBox({
                    "txtImage" : "Image",
                    "txtOf" : " of "
                });
            }
        });
    });

    $("select.property").live("change", function() {
        $("#product-form").ajaxSubmit({
            url : $("#product-form").attr("data"),
            success : function(data) {
                var data = $.parseJSON(data);
                $("#product-inline").html(data["product"]);
                $.jGrowl(data["message"]);

                // Re-bind lightbox
                $("a.product-image").lightBox({
                    "txtImage" : "Image",
                    "txtOf" : " of "
                });
            }
        });
    });

    $(".product-quantity").attr("autocomplete", "off");

    $(".product-quantity").live("keyup", function() {
        var url = $("#packing-url").attr("data")
        if (url) {
            $("#product-form").ajaxSubmit({
                url : url,
                success : function(data) {
                    var data = $.parseJSON(data);
                    $(".packing-result").html(data["html"]);
                }
            });
        }
    });

    $("select.cp-property").live("change", function() {
        $("#product-form").ajaxSubmit({
            url : $("#cp-url").attr("data"),
            success : function(data) {
                var data = $.parseJSON(data);
                $(".standard-price-value").html(data["price"]);
                $(".for-sale-price-value").html(data["for-sale-price"]);
                $(".for-sale-standard-price-value").html(data["for-sale-standard-price"]);
                // $.jGrowl(data["message"]);

                // Re-bind lightbox
                $("a.product-image").lightBox({
                    "txtImage" : "Image",
                    "txtOf" : " of "
                });
            }
        });
    });

    // Cart ###################################################################
    $(".add-accessory-link").live("click", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $("#cart-items").html(data);
        });
        return false;
    });

    $(".delete-cart-item").live("click", function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $("#cart-inline").html(data);
        });
        return false;
    });

    // TODO: Optimize
    $(".cart-amount").live("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#cart-inline").html(data["html"]);
                if (data["message"])
                    $.jGrowl(data["message"]);
            }
        })
    });

    $(".cart-country").live("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#cart-inline").html(data["html"]);
            }
        })
    });

    $(".cart-shipping-method").live("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#cart-inline").html(data["html"]);
            }
        })
    });

    $(".cart-payment-method").live("change", function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#cart-inline").html(data["html"]);
            }
        })
    });

    // Search ##################################################################
    $("#search-input").live("blur", function(e) {
        window.setTimeout(function() {
            $("#livesearch-result").hide();
        }, 200);
    });

    $("#search-input").delay({
        delay: 400,
        event: "keyup",
        fn: function(e) {
            if (e.keyCode == 27) {
                $("#livesearch-result").hide();
            }
            else {
                var q = $("#search-input").attr("value");
                var url = $("#search-input").attr("data");
                $.get(url, {"q" : q}, function(data) {
                    data = $.parseJSON(data);
                    if (data["state"] == "success") {
                        $("#livesearch-result").html(data["products"]);
                        $("#livesearch-result").slideDown("fast");
                    }
                    else {
                        $("#livesearch-result").html();
                        $("#livesearch-result").hide();
                    }
                })
            }
        }
    });

    // Checkout ##################################################################
    var table = $('.shipping-address');
    if ($("#id_no_shipping:checked").val() != null) {
        table.hide();
    }
    else {
        table.show();
    }

    $("#id_no_shipping").live("click", function() {
        var table = $('.shipping-address');
        if ($("#id_no_shipping:checked").val() != null) {
            table.slideUp("fast");
        }
        else {
            table.slideDown("fast");
        }
        var data = $(".checkout-form").ajaxSubmit({
            url : $(".checkout-form").attr("data"),
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#cart-inline").html(data["cart"]);
                $("#shipping-inline").html(data["shipping"]);
            }
        });
    })

    if ($(".payment-method-type-2:checked").val() != null) {
        $("#credit-card").show();
    }
    else {
        $("#credit-card").hide();
    }

    if ($(".payment-method-type-1:checked").val() != null) {
        $("#bank-account").show();
    }
    else {
        $("#bank-account").hide();
    }

    $(".payment-methods").live("click", function() {
        if ($(".payment-method-type-1:checked").val() != null) {
            $("#bank-account").slideDown("fast");
        }
        else {
            $("#bank-account").slideUp("fast");
        }
        if ($(".payment-method-type-2:checked").val() != null) {
            $('#credit-card').slideDown("fast");
        }
        else {
            $('#credit-card').slideUp("fast");
        }
    })

    var update_invoice_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("invoice"),
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#invoice-address-inline").html(data["invoice_address"]);
            }
        });
    }

    var save_invoice_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("invoice"),
            "success" : function(data) {
            }
        });
    }

    var update_shipping_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("shipping"),
            "success" : function(data) {
                var data = $.parseJSON(data);
                $("#shipping-address-inline").html(data["shipping_address"]);
            }
        });
    }

    var save_shipping_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("shipping"),
            "success" : function(data) {
            }
        });
    }

    $("#id_invoice-firstname,#id_invoice-lastname,#id_invoice-line1,#id_invoice-line2,#id_invoice-city,#id_invoice-state,#id_invoice-cpde").live("change", function() {
    	save_invoice_address();
    });

    $(".update-checkout").live("click", function() {
        update_checkout();
    });

    $("#id_invoice-country").live("change", function() {
    	update_invoice_address();
        update_checkout();
    });

    $("#id_shipping-country").live("change", function() {
    	update_shipping_address();
        update_checkout();
    });

    $("#id_shipping-firstname,#id_shipping-lastname,#id_shipping-line1,#id_shipping-line2,#id_shipping-city,#id_shipping-state,#id_shipping-cpde").live("change", function() {
    	save_shipping_address();
    });


    var update_html = function(data) {
        data = $.parseJSON(data);
        for (var html in data["html"])
            $(data["html"][html][0]).html(data["html"][html][1]);

        if (data["message"]) {
            $.jGrowl(data["message"]);
        }
    }

    $("#voucher").live("change", function() {
        var url = $(this).attr("data");
        var voucher = $(this).attr("value");
        $.post(url, { "voucher" : voucher }, function(data) {
            update_html(data);
        });
    });
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