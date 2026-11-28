.. index:: Production, Deployment

==========
Production
==========

This page describes how to run a shop with LFS on a server and how to update it. lfs-starter reads all of the
following settings from environment variables (see its ``.env.example``).

Settings
========

* ``DEBUG = False``, a long random ``SECRET_KEY`` from the environment, your domain in ``ALLOWED_HOSTS`` and
  ``CSRF_TRUSTED_ORIGINS`` (with ``https://``).
* Behind a web server that terminates HTTPS: ``SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")``,
  ``SESSION_COOKIE_SECURE = True`` and ``CSRF_COOKIE_SECURE = True``.
* **Database:** PostgreSQL, with ``django.contrib.postgres`` in ``INSTALLED_APPS`` (the search then ignores
  accents).
* **E-mail:** an SMTP server (``EMAIL_HOST``, ``EMAIL_PORT``, ``EMAIL_HOST_USER``, ``EMAIL_HOST_PASSWORD``,
  ``EMAIL_USE_TLS``) and ``DEFAULT_FROM_EMAIL``. The shop sends the order confirmations and notifications; the
  sender of these mails is the ``From e-mail address`` in ``Shop / Preferences``, which the SMTP server must accept.
* **Static files:** ``STATIC_ROOT`` and, for long browser caching, ``ManifestStaticFilesStorage``:

  .. code-block:: python

      STORAGES = {
          "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
          "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
      }

* **Cache:** LFS caches products, categories and more, and deletes an entry when its object changes. That works only
  if all processes share the cache. With several gunicorn workers use a shared cache such as Redis
  (``django.core.cache.backends.redis.RedisCache``) or Memcached; with ``LocMemCache`` every worker has its own cache,
  and a change shows in the other workers only when their entries expire (by default after 5 minutes). Without a
  shared cache, ``DummyCache`` (no caching) is the safe choice.
* **Errors:** log to the console or a file with ``LOGGING``, so that tracebacks reach the server's logs.
* ``LFS_DOCS = "https://docs.django-lfs.com/"`` shows the help links in the management interface.
* ``robots.txt`` comes from the theme's template ``lfs/shop/robots.txt``; override it in your templates if search
  engines should not see parts of the shop.

Application and web server
==========================

Run the project with an application server, e.g. gunicorn::

    $ gunicorn project.wsgi --bind 127.0.0.1:8000 --workers 4

Put a web server in front of it that terminates HTTPS, redirects HTTP to HTTPS, serves the static and uploaded
files itself, and passes the rest on. A minimal nginx configuration:

.. code-block:: nginx

    server {
        listen 443 ssl;
        server_name shop.example.com;
        # ssl_certificate and ssl_certificate_key, e.g. from Let's Encrypt (certbot)

        client_max_body_size 20m;  # uploads of images and attachments

        location /static/ { alias /srv/shop/static/; expires 30d; }
        location /media/  { alias /srv/shop/media/; }

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 80;
        server_name shop.example.com;
        return 301 https://$host$request_uri;
    }

Backups
=======

A shop's data is its database and the uploaded files (``MEDIA_ROOT``: product images, attachments). Back up both,
daily and before every update, and keep copies off the server:

.. code-block:: console

    $ pg_dump -Fc -d shop > shop-$(date +%Y%m%d).dump
    $ tar czf media-$(date +%Y%m%d).tar.gz media/

Try a restore now and then (``pg_restore -d <empty database> shop-….dump``): a backup that was never restored is
not proven to work.

Deploying a new version
=======================

#. Back up the database.
#. Install the new code and packages.
#. ``python manage.py migrate``
#. ``python manage.py collectstatic --noinput``
#. Restart the application server.
#. Check the shop: start page, a product, the cart, and the management interface.

Updating LFS
============

#. Read the release notes (``HISTORY.txt``) and, for a new major version, :doc:`upgrade_notes`. Add-ons may need
   new settings; e.g. lfs-stripe needs ``STRIPE_PUBLISHABLE_KEY`` since 1.0.2.
#. Try the update on a copy first: restore the latest backup into a second database, run the new version against
   it, and compare it with the shop in production: prices and shipping costs of a few products, an order with
   every payment method up to the order mails, and the management interface.
#. Deploy as above.
