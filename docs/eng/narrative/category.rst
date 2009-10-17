Category
========

General
-------

* Categories are used to browse through the shop.
* Categories can have an arbitrary amount of products.
* Categories can have an arbitrary amount of sub categories.
* Categories can display its sub categories or products.
* Categories have format information which decides how its products or
  categories are displayed.
* Categories can have an optional ``static block`` which can displayed on the top
  of the category page.

Category Tab
------------

* **Name**
    The name of the Category.
* **Slug**
    This is the last part of the URL to display the category. This has to be
    unique for a category.
* **Parent**
    The direct parent category of the category. If this is empty the category
    is a top level category.
* **Short description**
    The short description of the category. This is displayed within within a
    category list. This is true if a category displays its sub categories. See
    content.
* **Description**
    The description of the category. This is displayed within detail views of
    the category.
* **Image**
    The image of the category. This is displayed within within a category list
    This is true if a category displays its sub categories. See content.
* **Static block**
    If a static block is selected it is displayed on top of the category view.
* **Content**
    This decides whether the products or the sub category of a category is
    displayed.
* **Active formats**
    If selected ``product rows``, ``product cols`` and ``category cols`` of the
    category are taken. Otherwise the category inherits formats from the parent
    category.
* **product rows**
    If a categories content is ``products`` then so many rows of products are
    displayed.
* **product cols**
    If a categories content is ``products`` then so many cols of products are
    displayed.
* **categories cols**
    If a categories content is ``categories`` then so many cols of categories
    are displayed.

Please note that the formats are inherited by sub categories (if they don't
have ``àctive formats`` selected). So even if a category has selected
``products`` the information for ``category cols`` could be important for sub
categories and vice versa.

Products Tab
------------

This tab is used to assign products to the displayed category.

SEO Tab
-------

* **Meta keywords**
   The meta keywords of the category. The content of this field is used for the
   meta keywords tag of the category page.
* **Meta description**
   The meta description of the category. the content of this field is used for
   the meta description tag of the category page.