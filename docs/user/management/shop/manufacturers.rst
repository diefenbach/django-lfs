.. index:: Manufacturer

.. _manufacturers_management:

=============
Manufacturers
=============

This section describes the management interface for manufacturers (``Shop / Manufacturers``).

On the left are all manufacturers (searchable by name), on the right the selected manufacturer with its tabs.

Site Actions
============

Add Manufacturer
    Opens a dialog to add a manufacturer with its ``Name`` and ``Slug``.

Delete Manufacturer
    Deletes the selected manufacturer, after a confirmation. Its products stay; they just have no manufacturer
    any more.

View Manufacturer
    Opens the manufacturer's page in the shop.

Tabs
====

Data
----

Name
    The name of the manufacturer.

Slug
    The unique last part of the manufacturer's URL.

Short description
    A short description, displayed in the list of all manufacturers.

Description
    The detailed description, displayed on the manufacturer's page.

Image
    The logo of the manufacturer.

Click ``Save Manufacturer Data`` to save the changes.

Products
--------

This tab assigns products to the manufacturer; the ``Manufacturer`` field on the :ref:`Data tab of a product
<products_management_data>` does the same.

Add products
    In the section ``Products`` (searchable by name, filtered by category) select the products and click
    ``Add to Manufacturer``.

Remove products
    In the section ``Assigned Products`` select the products and click ``Remove from Manufacturer``.

SEO
---

This tab is used to optimize the manufacturer's page for search engines. Click ``Save SEO Settings`` to save the
changes.

Meta title
    Displayed in the title tag of the manufacturer's page. The default is ``<name>``, the name of the manufacturer.

Meta description
    Displayed in the meta description tag of the manufacturer's page.

Meta keywords
    Displayed in the meta keywords tag of the manufacturer's page.

.. note::

    You can use these placeholders in the fields:

    <name>
        The name of the manufacturer.

    <short-description>
        The short description of the manufacturer (only in meta keywords and meta description).

Portlets
--------

This tab is used to assign :term:`portlets` to the manufacturer's page. Click the pencil to edit a portlet and the
trash can to delete it; drag a portlet to change its position or to move it to the other slot. To add a portlet,
select the ``Portlet Type`` and click ``Add portlet``.
