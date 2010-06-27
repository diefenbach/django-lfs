.. index:: Installation

============
Installation
============

Prequisites
===========

Make sure you have installed:

   * Python 2.6.x
   * A RDBMS of your choice (PostgreSQL, MySQL, SQLite or Oracle)

Installation
============

The installation is straightforward and should last just a few minutes.

   1. Download the installer from http://pypi.python.org/pypi/django-lfs
   2. $ tar xzf django-lfs-installer.tar.gz
   3. $ cd django-lfs-installer-<version>
   4. $ python bootstrap.py
   5. $ bin/buildout -v
   6. Enter your database settings to lfs_project/settings.py
   7. $ bin/django syndb
   8. $ bin/django lfs_init
   9. Browse to http://localhost:8000/

That's all!

Please note:
============

* If you encounter problems during ``bin/buildout -v`` or on the first
  run on a Debian or Ubuntu server make sure you have the build tools and
  Python dev packages installed::

    apt-get install build-essential
    apt-get install python-dev
    apt-get install python-all-dev
    apt-get install python-profiler (multiverse repository)

What's next?
============
Move on to :doc:`getting_started`.
