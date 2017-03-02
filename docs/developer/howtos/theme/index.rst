=====================
How to create a theme
=====================

In this how-to you will learn how to create a theme for LFS.

.. note::

    You can :download:`download the whole theme here <mytheme.tar.gz>`.

Preparations
============

First you have to create a new Django application. This is beyond the purpose
of this tutorial and you should refer to `Django's excellent tutorial
<http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_ if you want to learn
more.

In short, your starting file structure should look like this::

    mytheme
        __init__.py
        templates
            lfs

Registration
============

Register mytheme to Django's template engine.

1. Move the mytheme folder to the PYTHONPATH.

   The easiest way to do that is to put it into the lfs_project folder of the
   buildout.

2. Register the theme

   Add mytheme to INSTALLED_APPS **before** lfstheme::

     INSTALLED_APPS = (
         ...
         "mytheme",
         "lfstheme",
         "django.contrib.admin",
         ...

Copy templates
==============

Now copy the templates you want to change into the lfs folder of mytheme and
adapt them to your needs.

**Important:** you have to keep the original path, e.g: base.html must be within
the root of the lfs folder whereas the cart portlet (cart.html) must be within
the portlets  folder::

    mytheme
        __init__.py
        templates
            lfs
                base.html
                portlets
                    cart.html

Use own css
===========

To use own CSS several steps are necessary.

1. Create a ``static`` folder within mytheme::

    mytheme
        static
        ...

2. Within that create a new CSS-file, e.g. mytheme.css and add your CSS rules,
   e.g.:

   .. code-block:: css

     .breadcrumbs li {
         color: red !important;
     }

   Alternatively you might copy main.css from ``lfstheme`` and adapt it to your
   needs.

3. Go to the ``lfs_project/media`` folder and create a symbolic link to the
   static folder::

   $ ln -s <path/to/buildout>/lfs_project/mytheme/static mytheme

4. Copy base.html to mytheme/templates/lfs (if you haven't done it so far)

5. Include your CSS file to the header::

    <link rel="stylesheet" type="text/css" href="{% static 'mytheme/mytheme.css' %}">

6. Optionally delete the link to main.css (if you just want to use your own CSS).
