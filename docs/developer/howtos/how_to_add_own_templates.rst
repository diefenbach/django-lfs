How to add own templates
========================

In this tutorial you will learn how to add own templates for categories and
products.

Generally
---------

All registered templates for categories can be found within the view tab of 
the category management view:

.. image:: /images/category_templates.*

All registered templates for products can be found within the data tab of 
the product management view:

.. image:: /images/product_templates.*

Categories
----------

In order to add a new template for categories go to lfs.catalog.settings and
add tuple to CATEGORY_TEMPLATES.

Example 1
^^^^^^^^^

.. code-block:: python

    (0,{"file":"%s/%s" % (CAT_PRODUCT_PATH ,"default.html"),
        "image":IMAGES_PATH + " /product_default.png",
        "name" : _(u"Category with products"),
        }),

which means:

0:
    The unique id of the category template

file:
    The absolute path to the template (CAT_PRODUCT_PATH means this is a template which displays the products of a category)

image:
    The absolute path to the preview image (this is used beside the template select box and shouldn't be larger then 100x100)

name:
    The pretty name of the template (this is displayed within the template select box)

Example 2
^^^^^^^^^

.. code-block:: python

    (1,{"file": "%s/%s" % (CAT_CATEGORY_PATH ,"default.html"),
        "image": IMAGES_PATH + "/category_square.png",
        "name": _(u"Category with subcategories"),
        }),

which means:

1:
    Unique id of the category template

file:
    The absolute path to the template (CAT_PRODUCT_PATH means this is a template which displays the sub categories of a category)

image:
    The absolute path to the preview image (this is used beside the template select box and shouldn't be larger then 100x100)

name:
    The tretty name of the template (this is displayed within the template select box)

Products
--------

In order to add a new template for products go to lfs.catalog.settings and
add tuple to PRODUCT_TEMPLATES.

Example
^^^^^^^

.. code-block:: python

    (0, {"file" : "%s/%s" % (PRODUCT_PATH, "product_inline.html"),
         "image" : IMAGES_PATH + "/product_default.png",
         "name" : _(u"Default template")
         },),

which means:

0:
    The unique id of the product template

file:
    The absolute path to the template

image:
    The absolute path to the preview image (this is used beside the template select box and shouldn't be larger then 100x100)

name
    The pretty name of the template (this is displayed within the template select box)
