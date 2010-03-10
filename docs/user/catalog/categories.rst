.. index:: Category, Static Block

==========
Categories
==========

Overview
========
* Categories are used to structure products.

* Every category can have either one or no parent category. In this way the
  category tree is built. If the category has no parent category it is a
  so-called top level category.

* Every category can have an arbitrary amount of products.

* A category can either display its sub categories or its products. This is up
  to the selected template.

* A category can have portlets. By default the portlets are inherited to the
  sub categories resp. to the assigned products but they can be blocked per
  :term:`slot`.

* A category can have a static block which are displayed on top of the
  category.

Tabs
====

In this section we will go through all tabs and fields of the category
management interface.

Data
----

This tab contains the core date of the category.

Name
    The name of the category. This is displayed on several places: Within
    overview pages on top of the category page and within the meta-title tag.

Slug
    The last part of the category's URL.

Parent
    The parent category

Position
    The ordinal position of the category within the parent category. Lower
    number come first.

Short description
    A short description of the category. This is displayed within overview
    pages.

Description
    The detailed description of the category. This is displayed on the detail
    page of the category.

Exclude from navigation
    If activated the category is excluded from the navigation portlet.

Image
    The image of the category. This can be displayed within overview pages and
    the detailed page.

.. index:: Static Block

Static block
    An static html block which is assigned to the category. This is displayed
    on top of detail page.

View
----

This tab contains all data which are responsible on how the content is
displayed.

.. index:: Template

Category template
    The selected template of the category. A category can have several
    templates. The selected templates decides what is displayed (sub templates,
    products) and how this information is structured.

Show all products (only available when a product template is selected)
    If activated also products of sub categories will be displayed for that
    category. Otherwise only the direct products are displayed.

.. index:: Formats

Active formats
    if activated you can overwrite the formats. If not activated formats are
    inherited from the parent object. This may be a parent category or the
    shop itself.

Category cols (only available if active formats is True and a category template is selected)
    Amount of columns which are used to display the sub categories. Always all
    direct categories of the category are displayed.

Product cols / Product rows  (only available if active formats is True and a product template is selected)
    Amount of columns and rows which are used to display the products of the category.
    The amount of products which are displayed calculates by cols * rows. If there
    are more products than that the products are automatically paginated.

Products
--------

This tab is used to assign/remove products to the category.

**Filter**

In order to make it easier to find and select several products you can filter
them. This is true for assignable and assigned products. Just put the product
name into the appropriate text box or/and select a certain category.

**Add products**

You can see available products to assign on top of the page. Select the checkboxes
beside all products you want to assign and click on ``Add to category``

**Remove products**

You can see all already assigned products within the ``Selected products`` section.
Select the checkboxes beside the products you want to remove and click on ``Remove
from category``.

SEO
---

This tab is used to optimize your pages for search engines. You can enter data
for all meta data fields. However LFS provides some reasonable default values
for all fields.

Meta title
    This is displayed within the meta title tag of the category's HTML tags. By
    default the name of the product is used.

Meta keywords
    This is displayed within the meta keywords tag of the category's HTML page.
    By default the short description of the category is used.

Meta description
    This is displayed within the meta description tag of the category's HTML
    page. By default the short description of the category is used.

You can use several placeholders within the above mentioned fields:

    **<name>**

    The name of the product.

    **<short-description>**

    The short description of the product (only within meta
    keywords/description-field).

Portlets
--------

The tab is used to assign :term:`portlets` to the category.

**Overview**

By default portlets are inherited from the parent, which is the parent category
or the shop.

**Block portlets**

Portlets can be blocked by :term:`slots`. To block portlets activate the appropriate
checkbox within the ``Blocked parent slots`` section and click on the ``Save
blocked parent slots``.

**Add portlets**

In order to add a new portlet to the category select the type of the portlet you
want to add, click ``Add portlet``, fill in the form and click on ``Save
portlet`` button.

**Edit portlets**

In order to edit a portlet click on the ``edit`` link beside the portlet, enter
your data and click on ``Save portlet`` button.

**Delete portlets**

In order to delete a portlet click on the ``delete`` link beside the portlet and
click on ``yes``.
your data and click on ``Save portlet``.