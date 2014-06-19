.. index:: Installation

============
Installation
============

Prerequisites
=============

Make sure you have installed:

* Python 2.6.x or 2.7.x
* A RDBMS of your choice (PostgreSQL, MySQL, SQLite or Oracle)

Installation
============

The installation is straightforward and should last just a few minutes. Please
execute following steps:

#. Download the installer from http://pypi.python.org/pypi/django-lfs

#. $ tar xzf django-lfs-installer-<version>.tar.gz

#. $ cd lfs-installer

#. $ python bootstrap.py

#. $ bin/buildout -v

#. Enter your database settings to lfs_project/settings.py

#. $ bin/django syncdb

#. $ bin/django migrate

#. $ bin/django lfs_init

#. $ bin/django collectstatic

#. $ bin/django runserver

#. Browse to http://localhost:8000

.. note::

    If you encounter problems, please see :ref:`trouble shooting
    <trouble_shooting_installation>`.

.. note::

    If you're setting up a production environment then you should not use Django's builtin development
    server (bin/django runserver). Instead, you'll probably want to use uWsgi or Gunicorn servers.
    Check Django (and uWsgi/Gunicorn) documentation for details.

.. note::

    For production environments you're supposed to change robots.txt file (otherwise bots/crawlers like google bot will
    not be allowed to scan your site, which is not what you probably want). Default version of robots.txt is located
    at lfs_theme application: templates/lfs/shop/robots.txt.
    You should create your own 'mytheme' app with structure like:
    templates/lfs/shop/robots.txt and place it in settings.INSTALLED_APPS before(!) 'lfs_theme'. Also note, that in
    production environment it is good to serve robots.txt directly from HTTP server like nginx or Apache.

Migration from versions 0.5 - 0.8 to version 0.9
================================================

Migration from versions 0.5 - 0.8 to version 0.9 can be done with a migration command (``lfs_migrate``)
which migrates existing databases up to version 0.9.

To migrate an existing database please proceed the following steps:

#. Install the new version (see above)

#. Backup your existing database

#. Enter your existing database to lfs_project/settings.py

#. $ bin/django syncdb

#. $ bin/django lfs_migrate

After that your database should be ready to run with the latest release.

Migration from version 0.9.0 to higher one
==========================================

#. Install the new LFS version

#. Backup your existing database

#. Enter your existing database to lfs_project/settings.py

#. $ bin/django migrate

Migration from 0.9.0 without South to 0.9.0 using South
=======================================================

This might be useful if you have github version of LFS that has no migrations yet, and you've updated to the version
that does use South migrations

#. Install the new LFS version

#. Backup your existing database

#. $ bin/django migrate --all --fake 0001

#. $ bin/django migrate order --fake 0002

#. $ bin/django migrate

What's next?
============
Move on to :doc:`getting_started`.
