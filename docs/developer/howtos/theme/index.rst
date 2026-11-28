=====================
How to create a theme
=====================

In this how-to you will learn how to change the look of a shop: its templates and its CSS.

The storefront of LFS comes from the theme lfs-theme (app ``lfs_theme``): templates under ``templates/lfs/`` and
static files under ``static/lfs_theme/``. Django uses the first template it finds with a given path, so a template
with the same path in your project or in your own theme replaces the one of lfs-theme. Everything you do not
replace stays as it is.

Find the templates
==================

Look up where lfs-theme is installed::

    $ python -c "import lfs_theme, os; print(os.path.dirname(lfs_theme.__file__))"

Its ``templates/lfs/`` folder holds all storefront templates, for instance ``base.html`` (the frame of every page)
and ``portlets/cart.html`` (the cart portlet).

Small changes: templates in the project
=======================================

For a few changes, put the templates into the project's template folder. lfs-starter has one, ``templates/``; in
another project add it to ``DIRS`` in ``TEMPLATES``. Copy the template you want to change there, keeping its path
below ``templates/``, and adapt it::

    templates
        lfs
            portlets
                cart.html

Your own theme
==============

For a larger redesign, or to use it in several shops, create a theme of its own: a Django app with templates and
static files.

#. Create the app with this structure::

    mytheme
        __init__.py
        templates
            lfs
        static
            mytheme

#. Register it in ``INSTALLED_APPS`` **before** ``lfs_theme``, so its templates win. Keep ``lfs_theme``: it provides
   every template your theme does not replace::

    INSTALLED_APPS = [
        "mytheme",
        "lfs_theme",
        *LFS_APPS,
        ...
    ]

#. Copy the templates you want to change into ``mytheme/templates/lfs/``, keeping their paths, and adapt them::

    mytheme
        templates
            lfs
                base.html
                portlets
                    cart.html

Use your own CSS
================

#. Create a CSS file in your theme, e.g. ``mytheme/static/mytheme/mytheme.css``:

   .. code-block:: css

     .breadcrumb {
         color: red;
     }

#. Copy ``lfs/base.html`` into your theme (if you haven't done so already) and include your CSS after the one of
   lfs-theme, so your rules win:

   .. code-block:: html+django

     <link rel="stylesheet" href="{% static 'lfs_theme/css/lfs_theme.css' %}">
     <link rel="stylesheet" href="{% static 'mytheme/mytheme.css' %}">

   lfs-theme is built with `Bootstrap 5 <https://getbootstrap.com/>`_, so its classes and CSS variables are
   available in your templates and CSS.

#. In production, run ``python manage.py collectstatic`` after every change of a static file.

.. note::

    Templates you copy do not get the improvements of later lfs-theme releases. Copy only the templates you really
    change, and compare them with the new version of lfs-theme when you upgrade.
