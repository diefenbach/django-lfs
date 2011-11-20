.. index:: Installation

============
Installation
============

Prequisites
===========

Make sure you have installed:

   * Python 2.6.x or 2.7.x
   * A RDBMS of your choice (PostgreSQL, MySQL, SQLite or Oracle)

Installation
============

The installation is straightforward and should last just a few minutes.

   1. Download the installer from http://pypi.python.org/pypi/django-lfs
   2. $ tar xzf django-lfs-installer-<version>.tar.gz
   3. $ cd lfs-installer
   4. $ python bootstrap.py
   5. $ bin/buildout -v
   6. Enter your database settings to lfs_project/settings.py
   7. $ bin/django syncdb
   8. $ bin/django lfs_init
   9. $ bin/django collectstatic
   10. $ bin/django runserver
   11. Browse to http://localhost:8000/

**Please note**:

* If you encounter problems during ``bin/buildout -v`` or on the first
  run on a Debian or Ubuntu server make sure you have the build tools and
  Python dev packages installed::

    apt-get install build-essential
    apt-get install python-dev
    apt-get install python-all-dev
    apt-get install python-profiler (multiverse repository)

Migration
=========

Starting with version 0.6 we provide a migration command (``lfs_migrate``)
which migrates existing databases to the latest release.

To migrate an existing database please proceed the following steps:

   1. Install the new version (see above)
   2. Backup your existing database
   3. Enter your existing database to lfs_project/settings.py
   4. $ bin/django syncdb
   5. $ bin/django lfs_migrate

After that your database should be ready to run with the latest release.


What's next?
============
Move on to :doc:`getting_started`.
