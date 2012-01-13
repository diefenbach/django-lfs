========================
How to add own templates
========================

In this how-to you will learn how to add your own templates for categories and
products.

Generally
=========
The content of products and categories are rendered by templates. LFS ships
with several default templates and you can add your own.

All registered templates for categories can be selected within the ``View`` tab
of the :doc:`Category Management Interface
</user/management/catalog/categories>`. All registered templates for products
can be selected within the ``Data`` tab of the :doc:`Product Management
interface </user/management/catalog/products>`.

Please refer to the default templates in order to find out which information
are provided within the templates. You can also add your customer template tags
in order to provide more functionality.

Categories
==========

In order to add a new template for categories go to ``lfs.catalog.settings`` and
add tuple to ``CATEGORY_TEMPLATES``.

Example 1
---------

.. code-block:: python

    (0,{"file":"%s/%s" % (CAT_PRODUCT_PATH ,"default.html"),
        "image":IMAGES_PATH + " /product_default.png",
        "name" : _(u"Category with products"),
        }),

Which means:

0:
    The unique id of the category template.

file:
    The absolute path to the template. ``CAT_PRODUCT_PATH`` means this is a
    template which displays the products of a category.

image:
    The absolute path to the preview image (not used anymore).

name:
    The pretty name of the template, which is displayed within the template
    select box.

Example 2
---------

.. code-block:: python

    (1,{"file": "%s/%s" % (CAT_CATEGORY_PATH ,"default.html"),
        "image": IMAGES_PATH + "/category_square.png",
        "name": _(u"Category with subcategories"),
        }),

Which means:

1:
    Unique id of the category template.

file:
    The absolute path to the template. ``CAT_PRODUCT_PATH`` means this is a
    template which displays the sub categories of a category.

image:
    The absolute path to the preview image (Not used anymore).

name:
    The pretty name of the template, which is displayed within the template
    select box.

Products
========

In order to add a new template for products go to ``lfs.catalog.settings`` and
add tuple to ``PRODUCT_TEMPLATES``.

Example
-------

.. code-block:: python

    (0, {"file" : "%s/%s" % (PRODUCT_PATH, "product_inline.html"),
         "image" : IMAGES_PATH + "/product_default.png",
         "name" : _(u"Default template")
         },),

Which means:

0:
    The unique id of the product template.

file:
    The absolute path to the template.

image:
    The absolute path to the preview image (Not used anymore).

name
    The pretty name of the template, which is displayed within the template
    select box.
