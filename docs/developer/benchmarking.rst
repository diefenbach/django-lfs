.. index:: Benchmarking LFS

================
Benchmarking LFS
================

This section describes how to benchmark LFS.

Overview
=========

You can use it in case you want to optimize LFS in terms of speed. In case you
want to add a new feature, please compare the versions with and without your
feature and try to not slow down LFS.

The development buildout comes with ``lfs_bench``, a small application, which
provides some tools to benchmark LFS.

JMeter
======

.. note::

    You can find more information about JMeter here: http://jmeter.apache.org/

1. Install `JMeter <http://jmeter.apache.org/>`_

2. Prepare the database::

    $ bin/django lfs_init
    $ bin/django lfs_generate_content_for_benchmark

3. Start LFS

 * Start LFS in production mode, for instance with ``bin/django-gunicorn``. and
   a reverse proxy in front of it. In other words don't use the development
   server.

 * Set DEBUG to False

4. Start JMeter::

    $ bin/jmeter -t path/to/lfs_bench/jmeter/lfs.jmx -p path/to/lfs_bench/jmeter/user.properties

5. Execute the Testplan and check the result within ``Summary Report`` for
   instance.

ab (Apache Benchmark)
=====================

.. note::

    You can find more information about ``ab`` here:
    http://httpd.apache.org/docs/2.0/programs/ab.html

1. Prepare the database::

    $ bin/django lfs_init
    $ bin/django lfs_generate_content_for_benchmark

2. Start LFS

 * Start LFS in production mode, for instance with ``bin/django-gunicorn``. and
   a reverse proxy in front of it. In other words don't use the development
   server.

 * Set DEBUG to False

3. Use ``ab``, for instance like that::

    $ ab -n 1000 -c 20 http://localhost/product-1-1-1

4. Check the results.

Python Profiling
================

The development buildout comes with a middleware, which let you profile single
requests. Just hang ``?prof`` behind the request you want to profile and you
will get a list of all executed methods, for instance::

    http://localhost/product-1-1-1?prof
