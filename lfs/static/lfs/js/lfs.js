// popup #################################################################
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

// Update checkout
var update_checkout = function() {
    var data = $(".checkout-form").ajaxSubmit({
        url : $(".checkout-form").attr("data"),
        "success" : function(data) {
            var data = safeParseJSON(data);
            $("#cart-inline").html(data["cart"]);
            $("#shipping-inline").html(data["shipping"]);
            $("#payment-inline").html(data["payment"]);
        }
    });
};

// TODO: use .data('...') instead of attr('data')
// TODO: limit number of handlers, preferrably split into separate .js files and use django's staticfiles
$(function() {
    // Delay plugin taken from ###############################################
    // http://ihatecode.blogspot.com/2008/04/jquery-time-delay-event-binding-plugin.html
    var $body = $('body');

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
        };

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
        $.removeCookie('message', { path: '/' });
    }

    // Rating #################################################################
    $(".rate").click(function() {
        var $this = $(this);
        $(".rate").each(function() {
            $(this).removeClass("current-rating")
        });

        $this.addClass("current-rating");

        $("#id_score").val($this.attr("data"));
        return false;
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

    $("a.product-image").fancybox({loop: false});

    // ----- REPORTED TO BE WORKING IN RECENT jQuery VERSIONS WITHOUT THIS HACK ------
    //    // Hack to make the change event on radio buttons for IE working
    //    // http://stackoverflow.com/questions/208471/getting-jquery-to-recognise-change-in-ie
    //    if ($.browser.msie) {
    //        $body.on('click', 'input.variant', function() {
    //            this.blur();
    //            this.focus();
    //        });
    //    }

    $body.on('change', 'input.variant', function() {
        var url = $(this).parents("table.product-variants").attr("data");
        var variant_id = $(this).attr("value");

        $("#product-form").ajaxSubmit({
            url : url,
            data : {"variant_id" : variant_id},
            success : function(data) {
                var data = safeParseJSON(data);
                $("#product-inline").html(data["product"]);
                $.jGrowl(data["message"], {theme: 'lfs'});

                // Re-bind fancybox
                $("a.product-image").fancybox({loop: false});
            }
        });
    });

    $body.on('change', 'select.property', function() {
        $("#product-form").ajaxSubmit({
            url : $("#product-form").attr("data"),
            success : function(data) {
                var data = safeParseJSON(data);
                $("#product-inline").html(data["product"]);
                $.jGrowl(data["message"], {theme: 'lfs'});

                // Re-bind fancybox
                $("a.product-image").fancybox({loop: false});
            }
        });
    });

    $(".product-quantity").attr("autocomplete", "off");

    $body.on('keyup', '.product-quantity', function() {
        var url = $("#packing-url").attr("data");
        if (url) {
            $("#product-form").ajaxSubmit({
                url : url,
                success : function(data) {
                    var data = safeParseJSON(data);
                    $(".packing-result").html(data["html"]);
                }
            });
        }
    });

    $body.on('change', 'select.cp-property', function() {
        $("#product-form").ajaxSubmit({
            url : $("#cp-url").attr("data"),
            success : function(data) {
                var data = safeParseJSON(data);
                $(".standard-price-value").html(data["price"]);
                $(".for-sale-price-value").html(data["for-sale-price"]);
                $(".for-sale-standard-price-value").html(data["for-sale-standard-price"]);
                $(".packing-result").html(data["packing-result"]);
                $.jGrowl(data["message"], {theme: 'lfs'});

                // Re-bind fancybox
                $("a.product-image").fancybox({loop: false});
            }
        });
    });

    // Cart ###################################################################
    $body.on('click', '.add-accessory-link', function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $("#cart-items").html(data);
        });
        $body.trigger({
              type:"cart-updated"
            });
        return false;
    });

    $body.on('click', '.delete-cart-item', function() {
        var url = $(this).attr("href");
        $.post(url, function(data) {
            $("#cart-inline").html(data);
            $body.trigger({
              type:"cart-updated"
            });
        });

        return false;
    });

    // TODO: Optimize
    $body.on('change', '.cart-amount', function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = safeParseJSON(data);
                $("#cart-inline").html(data["html"]);
                $body.trigger({
                  type:"cart-updated"
                });
                if (data["message"])
                    $.jGrowl(data["message"]);
            }
        })
    });

    $body.on('change', '.cart-country', function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = safeParseJSON(data);
                $("#cart-inline").html(data["html"]);
                $body.trigger({
                  type:"cart-updated"
                });
            }
        })
    });

    $body.on('change', '.cart-shipping-method', function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = safeParseJSON(data);
                $("#cart-inline").html(data["html"]);
            }
        })
    });

    $body.on('change', '.cart-payment-method', function() {
        $("#cart-form").ajaxSubmit({
            "type" : "post",
            "success" : function(data) {
                var data = safeParseJSON(data);
                $("#cart-inline").html(data["html"]);
                $body.trigger({
                  type:"cart-updated"
                });
            }
        })
    });

    // Search ##################################################################
    $body.on('blur', '#search-input', function(e) {
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
                var url = $("#search-input").data("url");
                $.get(url, {"q" : q}, function(data) {
                    data = safeParseJSON(data);
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
    var $shipping_table = $('.shipping-address');
    var $invoice_table = $('.invoice-address');
    var $no_shipping = $("#id_no_shipping");
    var $no_invoice = $("#id_no_invoice");

    if ($no_shipping.length > 0){  // there is an option to mark shipping address same as invoice address
        if ($no_shipping.prop('checked')) {
            $shipping_table.hide();
        }
        else {
            $shipping_table.show();
        }

        $body.on('click', '#id_no_shipping', function() {
            var table = $('.shipping-address');
            if ($('#id_no_shipping').prop('checked')) {
                table.hide();
            }
            else {
                table.show();
            }
            var data = $(".checkout-form").ajaxSubmit({
                url : $(".checkout-form").attr("data"),
                "success" : function(data) {
                    var data = safeParseJSON(data);
                    $("#cart-inline").html(data["cart"]);
                    $("#shipping-inline").html(data["shipping"]);
                }
            });
        });
    }
    else {  // there is an option to mark invoice address same as shipping address
        if ($no_invoice.prop('checked')) {
            $invoice_table.hide();
        }
        else {
            $invoice_table.show();
        }

        $body.on('click', '#id_no_invoice', function() {
            var table = $('.invoice-address');
            if ($('#id_no_invoice').prop('checked')) {
                table.hide();
            }
            else {
                table.show();
            }
            var data = $(".checkout-form").ajaxSubmit({
                url : $(".checkout-form").attr("data"),
                "success" : function(data) {
                    var data = safeParseJSON(data);
                    $("#cart-inline").html(data["cart"]);
                    $("#shipping-inline").html(data["shipping"]);
                }
            });
        });
    }

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

    $body.on('click', '.payment-methods', function() {
        if ($(".payment-method-type-1:checked").val() != null) {
            $("#bank-account").show();
        }
        else {
            $("#bank-account").hide();
        }
        if ($(".payment-method-type-2:checked").val() != null) {
            $('#credit-card').show();
        }
        else {
            $('#credit-card').hide();
        }
    });

    var update_invoice_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("invoice"),
            "success" : function(data) {
                var data = safeParseJSON(data);
                $("#invoice-address-inline").html(data["invoice_address"]);
            }
        });
    };

    var save_invoice_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("invoice"),
            "success" : function(data) {
            }
        });
    };

    var update_shipping_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("shipping"),
            "success" : function(data) {
                var data = safeParseJSON(data);
                $("#shipping-address-inline").html(data["shipping_address"]);
            }
        });
    };

    var save_shipping_address = function() {
        var data = $(".postal-address").ajaxSubmit({
            url : $(".postal-address").attr("shipping"),
            "success" : function(data) {
            }
        });
    };

    $body.on('change', '#id_invoice-firstname,#id_invoice-lastname,#id_invoice-line1,#id_invoice-line2,#id_invoice-city,#id_invoice-state,#id_invoice-code', function() {
    	save_invoice_address();
    });

    $body.on('click', '.update-checkout', function() {
        update_checkout();
    });

    $body.on('change', '#id_invoice-country', function() {
    	update_invoice_address();
        update_checkout();
    });

    $body.on('change', '#id_shipping-country', function() {
    	update_shipping_address();
        update_checkout();
    });

    $body.on('change', '#id_shipping-firstname,#id_shipping-lastname,#id_shipping-line1,#id_shipping-line2,#id_shipping-city,#id_shipping-state,#id_shipping-code', function() {
    	save_shipping_address();
    });


    var update_html = function(data) {
        data = safeParseJSON(data);
        for (var html in data["html"])
            $(data["html"][html][0]).html(data["html"][html][1]);

        if (data["message"]) {
            $.jGrowl(data["message"], {theme: 'lfs'});
        }
    };

    $body.on('change', '#voucher', function() {
        var url = $(this).attr("data");
        var voucher = $(this).attr("value");
        $.post(url, { "voucher" : voucher }, function(data) {
            update_html(data);
        });
    });

    $body.on('change', ".property-checkbox", function() {
        var url = $(this).attr("url");
        document.location=url;
    });
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
