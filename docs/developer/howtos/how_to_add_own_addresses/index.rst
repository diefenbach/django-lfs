.. _how_to_add_own_addresses:

========================
How to add own addresses
========================

In this how-to you will learn how to add own addresses to LFS, or better yet,
how to adapt the address fields to your needs.

You can :download:`download the example application
<my_addresses.tar.gz>` here.

Create an Application
=====================

First you need to create a default :term:`Django` application (or use an
existing one), where  you can put in your plugin. If you do not know how to do
this, please refer to the excellent `Django tutorial
<http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement the Address Model
===========================

The main part of the application consists of a address model which must inherit
from the ``BassAddress`` class.

.. code-block:: python

    from lfs.addresses.models import BaseAddress

    class MyAddress(BaseAddress):
        values_before_postal = ("firstname+", "lastname+", "company_name")
        values_after_postal = ("phone", "email")

        company_name = models.CharField(_("Company name"), max_length=50, blank=True, null=True)
        phone = models.CharField(_("Phone"), blank=True, max_length=20)
        mobile = models.CharField(_("Mobile"), blank=True, max_length=20, required=False)
        email = models.EmailField(_("E-Mail"), blank=True, null=True, max_length=50)

In this case we add an extra field ``mobile`` to LFS' default address. In
generell you can add as many fields as you need.

The only LFS specific thing you have to take care of are two attributes:
``values_before_postal`` and ``values_after_postal``, which define the fields,
which are displayed before and after the postal address fields. This is used
when the address is diplayed within LFS, e.g. within the orders or the customer
management interface. If you add an ``+`` at the end of the attribute there will
be no ``div`` around the value. In this ways you can display fields in one row.

Implement the Address Form
==========================

Another important part is to add the form, which is displayed to the shop
customer when he needs to enter his address. To makes things eaysier you should
inherit from ``AddressBaseForm``

.. code-block:: python

    # django imports
    from django import forms

    # lfs imports
    from lfs.addresses.models import AddressBaseForm

    # my_addresses imports
    from my_addresses.models import MyAddress


    class MyAddressForm(AddressBaseForm):
        fields_before_postal = ("firstname", "lastname", "company_name")
        fields_after_postal = ("phone", "mobile", "email")

        class Meta(AddressForm.Meta):
            model = MyAddress

The only LFS specific thing you have to take care of are two attributes:
``fields_before_postal`` and ``fields_after_postal`` which define the fields
which are displayed before and after the postal address fields. This is used
when the form is displayed within LFS, e.g. within the checkout page or within
the ``my addresses`` section.

Plug in the Components
======================

Now, as the code is ready, you can easily plug in your own address:

#. Add your application to the PYTHONPATH

#. Add your application to settings.INSTALLED_APPS (before ``lfs_theme`` if
   you overwrite the default templates)::

     INSTALLED_APPS = (
          ...
          "my_addresses",
     )

#. Add the model to the :ref:`LFS_ADDRESS_MODEL <settings_addresses>` setting::

     LFS_ADDRESS_MODEL = "my_addresses.models.MyAddress"

#. Add the forms to the :ref:`LFS_INVOICE_ADDRESS_FORM <settings_addresses>` and
   :ref:`LFS_SHIPPING_ADDRESS_FORM <settings_addresses>` setting::

     LFS_INVOICE_ADDRESS_FORM = "my_addresses.forms.MyInvoiceAddressForm"
     LFS_SHIPPING_ADDRESS_FORM = "my_addresses.forms.MyShippingAddressForm"

#. As the address is a new model, you have to synchronize your database::

     $ bin/django syncdb

#. Restart your instance and the address should be displayed to the shop
   users for instance within the checkout page.

Good to Know
============

* You can provide different templates to render the addresses. By default LFS
  tries try to get the specific template (``address_view.html``). If it doesn't
  exist, it tries to get one of the specific templates
  (``invoice_address_view.html`` or ``shipping_address_view.html``).

* You can provide different templates to render the address forms. By default
  LFS tries try to get the specific template (``address_form.html``). If it
  doesn't exist, it tries to get one of the specific templates
  (``invoice_address_form.html`` or ``shipping_address_form.html``).

* By default LFS automatically updates default addresses to the values from
  last order. It is possible to change this behavior by setting
  ``LFS_AUTO_UPDATE_DEFAULT_ADDRESSES`` to False.

See Also
========

* :ref:`Address Settings <settings_addresses>`
