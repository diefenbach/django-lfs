.. index:: Page, HTML

.. _pages_management:

=====
Pages
=====

This section describes the management interfaces of pages.

Site Actions
============

Add Page
    Adds a new page.

Delete Page
    Deletes the currently displayed page.

View Page
    Opens the page in a pop-up window to quickly check the appearance of
    the page without leaving the :term:`LMI`.

Goto Page
    Leaves the :term:`LMI` and redirects to the customer view of the current
    displayed page.

Sort Pages
==========

In order to sort pages, take the handle on besides a page within the navigation
on the left side and drag and drop it to the position you want the page to be.

Root
====

This is the root of all pages. You can add portlets to it which are inherited
from all other pages.

Tabs
====

Data
----

Title
    The title of the page. This is displayed on top of the page as well as
    within the meta title tag.

Slug
    The unique last part of the URL to the page.

Short text
    The short text of the page. This is displayed within overviews.

Text
    The main text of the page.

Active
    If this is checked the page is active. Only active pages are displayed to
    the shop users.

Position
    Pages are ordered by position. Lower numbers come first.

.. index:: pair: File; Downloadable

File
    A file which can be uploaded. If a file has been uploaded a download link
    is automatically displayed at the bottom of the page.

SEO
---

This tab is used to optimize your pages for search engines. You can enter data
for all usual HTML meta data fields. However LFS provides some reasonable default
values for all fields.

Meta title
    This is displayed within the meta title tag of the category's HTML tags. By
    default the name of the product is used.

Meta keywords
    This is displayed within the meta keywords tag of the category's HTML page.
    By default the short description of the category is used.

Meta description
    This is displayed within the meta description tag of the category's HTML
    page. By default the short description of the category is used.

.. note::

    You can use several placeholders within these fields:

    <name>
        The name of the page.

    <short-description>
        The description of the page (only within meta keywords and meta
        description field).

Portlets
--------

This tab is used to assign :term:`portlets` to the page.

Blocked parent slots
    By default portlets are inherited from the current category. To block
    portlets check the regarding slots and click on the ``Save blocked parent
    slots`` button.

Slots
  Here you can see all directly assigned portlets to the page. In order to edit
  a portlet click on row of the portlet. In order to delete a portlet click on
  the red cross beside the portlet. You can also change the position of the
  portlets by clicking on the up and down arrows beside the portlets.

Add new Portlet
    In order to add a portlet to the page select the type of portlet and click
    on ``Add portlet``.

See Also
========

* :ref:`Pages in general <pages_concepts>`
* :ref:`Portlets in general <portlets_concepts>`
