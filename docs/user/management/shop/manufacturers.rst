=============
Manufacturers
=============

This section describes the management interface for manufacturers.

Site Actions
============

Add Manufacturer
    Adds a new manufacturer.

Delete Manufacturer
    Deletes the current displayed manufacturer.

View Manufacturer
    Opens the Manufacturer in a pop-up window to quickly check the appearance of
    the Manufacturer without leaving the :term:`LMI`.

Goto Manufacturer
    Leaves the :term:`LMI` and goes to manufacturer view.

Tabs
====

Data
----

Name
    The name of the manufacturer

Slug
    The unique last part of the manufacturer's URL.

Short description
    The simplified description of the manufacturer. Displayed on the list of all
    manufacturers (/manufacturers).

Description
    The detailed description of the manufacturer. This is displayed on the detail
    view of the manufacturer.

Image
    Logo of the manufacturer.

View
----

Active formats
    If this check box is activated several formats for this manufacturer can be
    overwritten. Otherwise the formats are inherited from the shop.

Product cols / Product rows
    Amount of columns and rows which are used to display the products of the
    manufacturer. The amount of products which are displayed calculates by
    cols * rows. If there are more products than that
    the products are automatically paginated.

    .. note::

        This is only available if ``Active Formats`` is True.

SEO
---

This tab is used to optimize your pages for search engines. You can enter data
for all meta data fields. However LFS provides some reasonable default values
for all fields.

Meta title
    This is displayed within the meta title tag of the manufacturer's HTML tags. By
    default the name of the manufacturer is used.

Meta keywords
    This is displayed within the meta keywords tag of the manufacturer's HTML page.
    By default the short description of the manufacturer is used.

Meta description
    This is displayed within the meta description tag of the manufacturer's HTML
    page. By default the short description of the manufacturer is used.

.. note::

    You can use several placeholders within these fields:

    <name>
        The name of the manufacturer.

    <short-description>
        The short description of the manufacturer (only within meta keywords and
        meta description field).


Products
--------

In order to assign products to the manufacturer, select the check boxes of the
corresponding products within the section ``Selectable Products`` and click on
``Add To Manufacturer``.


Products Tree
-------------

Within this tab you can assign categories and products to the manufacturer.

To assign all products of a category to the manufacturer just check it. If you
want just a sub category or single products of it, click on the category to
expand the children.
