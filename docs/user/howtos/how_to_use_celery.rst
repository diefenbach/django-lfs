=================
How To Use Celery
=================

Overview
========

In this how-to you will learn how to use ``Celery`` with LFS. It is used to send
e-mails from LFS asynchronously.

``Celery`` is integrated with LFS by default. If it is installed and properly
set up LFS will make use of it. If not LFS, will work as expected, though.

Install Celery
==============

To install ``Celery`` proceed the following steps:

#. $ pip install django-celery

#. Add the following lines to settings.py::

    import djcelery
    djcelery.setup_loader()

#. Add ``djcelery`` and ``kombu.transport.django`` to ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        "...",
        "djcelery",
        "kombu.transport.django", # only needed when the broker is Django's database
    )

#. Sync your database::

    $ bin/django syncdb

#. Add a broker to ``settings.py``::

    BROKER_URL = "django://"

#. Start ``Celery``::

    $ bin/django celeryd --loglevel info

Note
====

This is the easiest way to setup ``Celery`` with LFS, which uses Django's
database as broker. You might want to use another broker to make use of all
features of ``Celery``. For that please refer to the excellent `documentation of
celery <http://docs.celeryproject.org/en/latest/index.html>`_.

Running Celery as a Deamon
==========================

In a production environment you might want to start ``Celery`` as deamon. To
make things easier we provide a init.d and a belonging configure script as a
start (both are heavily based on the examples of the ``Celery`` documentation).
Please see https://github.com/diefenbach/celery.

To start ``Celery`` as daemon:

* Put both scripts into the same directory

* Adapt the settings within celery.cfg and

* Execute celery.sh like::

    $ ./celery.sh start

.. seealso::

    `Running celeryd as a daemon <http://docs.celeryq.org/en/latest/cookbook/daemonizing.html>`_

See Also
========

* `Celery homepage <http://celeryproject.org/>`_
* `Celery with Django <http://docs.celeryproject.org/en/latest/django/index.html>`_
