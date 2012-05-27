.. index:: Benchmarking LFS

================
Benchmarking LFS
================

This section describes how to benchmark LFS.

Overview
=========

The development buildout comes with ``lfs_bench``, a small application, which
provides some tools to benchmark LFS.

You can use it in case you want to optimize LFS in terms of speed. In case you
want to development a new feature, please compare the versions with and without
this feature and try to not slow down LFS.

JMeter
======

1. Install `JMeter <http://jmeter.apache.org/>`_

2. Prepare the database::

    $ bin/django lfs_init
    $ bin/django lfs_generate_content_for_benchmark

3. Start LFS

 * Start LFS in production mode, for instance with ``bin/django-gunicorn``. and
   a reverse proxy in front of it. In other words don't use the development
   server.

 * Set DEBUG to False

4. Start JMeter

  Make sure you start it from the buildout base directory (that's the same
  directory you start Django from)::

    $ /path/to/jmeter/bin/jmeter -t src/lfs_bench/lfs_bench/jmeter/lfs.jmx -p src/lfs_bench/lfs_bench/jmeter/user.properties

5. Execute the Testplan and check the result within ``Summary Report`` for
   instance.

Apache Benchmark - ab
=====================

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

The development buildout provides a middleware by default, which let you profile
single requests. Just suffix the request with ``?prof`` in order to get
profiling data, for instance::

    http://localhost/product-1-1-1?prof

See also:

* `JMeter <http://jmeter.apache.org/>`_
* `Apache Benchmark - ab <http://httpd.apache.org/docs/2.0/programs/ab.html>`_
* `Python stats reference <http://docs.python.org/library/profile.html#module-pstats>`_
