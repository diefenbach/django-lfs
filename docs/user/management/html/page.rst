.. index:: Page, HTML

.. _pages_management:

=====
Pages
=====

This section describes the management interface for pages (``HTML / Pages``), e.g. imprint, terms and
conditions, or about us.

On the left are all pages (searchable by title), on the right the selected page with its tabs.

.. image:: /images/manage_page_data.png
   :alt: The Data tab of a page

Site Actions
============

Add Page
    Adds a page.

Delete Page
    Deletes the selected page, after a confirmation.

View Page
    Opens the page in the shop.

.. note::

    The shop lists pages by their position. The position is not part of the management interface in 1.0; change
    it in Django's admin (``/admin/``, ``Page / Pages``).

Root
====

The first entry of the list, ``Root``, is the root of all pages. It has only the ``Portlets`` tab: its portlets
are inherited by all pages.

Tabs
====

Data
----

Active
    Only active pages are displayed in the shop.

Title
    The title of the page, displayed on top of the page and in the title tag.

Slug
    The unique last part of the page's URL.

Exclude from navigation
    If checked, the page is not listed in the overview of all pages and in the pages portlet.

Short text
    A short text of the page, displayed in overviews.

Text
    The main text of the page.

.. index:: pair: File; Downloadable

File
    A file for download. If a file has been uploaded, the page shows a download link below the text.

Click ``Save data`` to save the changes.

SEO
---

This tab is used to optimize the page for search engines. Click ``Save SEO`` to save the changes.

Meta title
    Displayed in the title tag of the page. The default is ``<title>``, the title of the page.

Meta description
    Displayed in the meta description tag of the page.

Meta keywords
    Displayed in the meta keywords tag of the page.

.. note::

    You can use these placeholders in the fields:

    <title>
        The title of the page.

    <short-text>
        The short text of the page (only in meta keywords and meta description).

Portlets
--------

This tab is used to assign :term:`portlets` to the page.

Blocked parent slots
    By default a page inherits the portlets of the root. To block them, check the slots and click ``Save blocked
    parent slots``.

Slots
    Lists the portlets assigned directly to the page, per slot. Click the pencil to edit a portlet and the trash
    can to delete it. Drag a portlet to change its position or to move it to the other slot.

Add portlet
    Select the ``Portlet Type`` and click ``Add portlet``.

See Also
========

* :ref:`Pages in general <pages_concepts>`
* :ref:`Portlets in general <portlets_concepts>`
