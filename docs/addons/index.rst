.. _addons:

=======
Add-ons
=======

Optional features of LFS are packages of their own. Each add-on is installed the same way:

#. Install the package, e.g. ``pip install lfs-stripe`` (with lfs-starter: ``uv sync --extra stripe``).
#. Add its app to ``INSTALLED_APPS``, after ``*LFS_APPS``.
#. Include its URLs in the project's ``urls.py``, if it has any.
#. Set its settings, if it has any, and run ``python manage.py migrate``.

The default theme lfs-theme shows the add-ons in the shop by itself once they are installed. A theme of your own
uses the template tags each page names.

.. toctree::
   :maxdepth: 1

   stripe.rst
   paypal.rst
   bulk_prices.rst
   samples.rst
   carousel.rst
   cookie_consent.rst
   gtm.rst
