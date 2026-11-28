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

To add a template for categories, set ``CATEGORY_TEMPLATES`` in your project's settings. The setting replaces
LFS's list, so copy LFS's entries from ``lfs.catalog.settings`` and add yours.

Example 1
---------

.. code-block:: python

    (0,{"file":"%s/%s" % (CAT_PRODUCT_PATH ,"default.html"),
        "image":IMAGES_PATH + " /product_default.png",
        "name" : _("Category with products"),
        }),

Which means:

0:
    The unique id of the category template.

file:
    The path of the template, as Django's template loaders find it, e.g. ``lfs/catalog/products/product_inline.html``. ``CAT_PRODUCT_PATH`` means this is a
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
        "name": _("Category with subcategories"),
        }),

Which means:

1:
    Unique id of the category template.

file:
    The path of the template, as Django's template loaders find it, e.g. ``lfs/catalog/products/product_inline.html``. ``CAT_PRODUCT_PATH`` means this is a
    template which displays the sub categories of a category.

image:
    The absolute path to the preview image (Not used anymore).

name:
    The pretty name of the template, which is displayed within the template
    select box.

Products
========

To add a template for products, set ``PRODUCT_TEMPLATES`` in your project's settings, again with LFS's entries
from ``lfs.catalog.settings`` and yours.

Example
-------

.. code-block:: python

    (0, {"file" : "%s/%s" % (PRODUCT_PATH, "product_inline.html"),
         "image" : IMAGES_PATH + "/product_default.png",
         "name" : _("Default template")
         },),

Which means:

0:
    The unique id of the product template.

file:
    The path of the template, as Django's template loaders find it, e.g. ``lfs/catalog/products/product_inline.html``.

image:
    The absolute path to the preview image (Not used anymore).

name
    The pretty name of the template, which is displayed within the template
    select box.
