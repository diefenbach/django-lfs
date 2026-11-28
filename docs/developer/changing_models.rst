.. index:: Changing models

===============
Changing models
===============

This section describes how to change the models of LFS when you develop LFS itself.

LFS uses Django's migrations; see `Migrations <https://docs.djangoproject.com/en/5.2/topics/migrations/>`_ in
Django's documentation.

#. Change the model, for instance add a field to a model in ``lfs.customer``.

#. Create the migration for the app::

    $ python manage.py makemigrations customer

#. Apply it::

    $ python manage.py migrate

#. Commit the migration together with the model change. It is created in the ``migrations/`` directory of the app.

Migrations must not depend on a shop's settings: every shop runs the same migrations, whatever it has configured.
If a field takes its choices or default from a setting, the migration gets a fixed value, not the shop's value. To
check that the models and the migrations match, run::

    $ python manage.py makemigrations --check --dry-run

In your own shop, do not change LFS's models. Put your own models into your own app, or link to LFS's models from
there (for instance with a ``OneToOneField`` to ``lfs.catalog.models.Product``).
