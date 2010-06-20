.. index:: Installation

============
Installation
============

Prequisites
===========

Make sure you have installed:

   * Python 2.6.x http://www.python.org/download/
   * sqlite http://www.sqlite.org/download.html
   * mercurial http://mercurial.selenic.com/wiki

Please note:

   * The dependency of mercurial will be disappear in near future.
   * You can - of course - use another database but we provide a pre filled sqlite
     database for convenience.
   * If you encounter problems during ``bin/buildout -v`` or on the first
     run on a Debian or Ubuntu server make sure you have the build tools and
     Python dev packages installed::

        apt-get install build-essential
        apt-get install python-dev
        apt-get install python-all-dev
        aptg-et install python-profiler (multiverse repository)

Installation
============

The installation is straightforward and should last just a few minutes.

   1. Get the installer: hg clone http://bitbucket.org/diefenbach/lfs-buildout-development/
   2. cd lfs-buildout-development
   3. python bootstrap.py
   4. bin/buildout -v
   5. bin/django runserver

Now open your browser and visit:

   * The frontend: http://localhost:8000/
   * The management interface: http://localhost:8000/manage

That's all!

Optionally
==========

If you want to use postgresql (for instance) as backend db just replace "sqlite3" with "psycopg2" in the "eggs" section under the "[django]" part

.. NOTE:: to learn more about using 'buildout' go to http://www.buildout.org/docs/index.html

If you are using another database then the provided sqlite you may want to synchronize and initialize it::

    $ bin/django syncdb
    $ bin/django loaddata path/to/your/eggs/django_lfs-xxx/lfs/core/fixtures/lfs_initial.xml

What's next?
============
Move on to :doc:`getting_started`.
