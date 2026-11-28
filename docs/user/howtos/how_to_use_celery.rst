=================
How To Use Celery
=================

LFS sends its e-mails (order confirmations, notifications, rating mails) during the request, with Django's mail
functions. If the mail server is slow, the customer waits for it. To send the mails in the background, use an
e-mail backend that hands them to a task queue; LFS needs no changes for that.

One way is `Celery <https://docs.celeryq.dev/>`_ with `django-celery-email
<https://pypi.org/project/django-celery-email/>`_:

#. Set up Celery for your Django project and a broker such as Redis, see `First steps with Django
   <https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html>`_.

#. Install django-celery-email, add ``"djcelery_email"`` to ``INSTALLED_APPS``, and set::

    EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
    CELERY_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

#. Start a Celery worker next to the shop.

From then on the shop puts every mail into the queue, and the worker sends it.
