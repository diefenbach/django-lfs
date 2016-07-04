=================
How To Use Celery
=================

Overview
========

``Celery`` is a distributed task queue that can be used to send e-mails from LFS asynchronously.

There is no special integration in LFS for ``Celery`` but there are general patterns for Django based projects
that can be used to get asynchronous e-mail backend.

Dependencies
============

You need:

 * `celery <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>`_
 * `django-celery-email <https://pypi.python.org/pypi/django-celery-email>`_

as well as some Celery backend, eg Redis. Consult Celery documentation for details.


Installation
============

Follow the Celery's `first steps with Django <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>`_
and django-celery-email `documentation <https://pypi.python.org/pypi/django-celery-email>`_.
