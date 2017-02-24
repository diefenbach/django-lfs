================
Trouble Shooting
================

.. _trouble_shooting_installation:

Installation
============

If you encounter problems during ``bin/buildout -v`` or on the first run on a
``Debian`` or ``Ubuntu`` server make sure you have the build tools and python
dev packages installed::

    $ sudo apt-get install build-essential
    $ sudo apt-get install python-dev
    $ sudo apt-get install python-all-dev
    $ sudo apt-get install python-profiler (multiverse repository)
    $ sudo apt-get install libjpeg8-dev zlib1g-dev (s. http://pillow.readthedocs.io/en/latest/installation.html)
