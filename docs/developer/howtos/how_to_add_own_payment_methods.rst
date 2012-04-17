===================================
How to add an own payment processor
===================================

In this how-to you will learn how to add a own payment processor.

Create an application
=====================

First you need to create a default Django application (or use an existing one),
where  you can put in your plugin. If you do not know how to do this, please
refer to the excellent `Django tutorial
<http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement the ``PaymentMethodProcessor`` class
==============================================

The main part of the plugin consists of a class which must provide a certain
API.

Create the class
----------------

Create a class which inherits from ``lfs.plugins.PaymentMethodProcessor``:

.. code-block:: python

    from lfs.plugins import PaymentMethodProcessor

    class MyPaymentMethodProcessor(PaymentMethodProcessor):
        pass


Add the ``process`` method
--------------------------

.. code-block:: python

    def process(self):
        total = self.order.price
        return {
            "accepted": True,
            "next_url": "http://www.acme.com/payment?id=4711&total=%s" % total,
        }

This method is called from LFS when the shop customer submits the checkout page
(while selected this payment method). Within that method you can do whatever
it is necessary to process your payment, e.g.:

* Call an API via HTTP(S)

* Redirect to another URL

Return Value
^^^^^^^^^^^^

The ``process`` method must return a dictionary with following keys (most of
them are optional):

accepted (mandatory)
    Indicates whether the payment is accepted or not. if this is
    ``False`` the customer keeps on the checkout page and gets the
    ``message`` below. If this is ``True`` the customer will be redirected to
    next_url or to LFS' thank-you page

message (optional)
    This message is displayed on the checkout page, when the order is
    not accepted.

message_location (optional)
    The location, where the message is displayed.

next_url (optional)
    The url to which the user is redirect after the payment has been
    processed. if this is not given the customer is redirected to the
    default thank-you page.

order_state (optional)
    The state in which the order should be set. It's just PAID. If it's
    not given the state keeps in SUBMITTED.


Add the ``get_create_order_time`` method
----------------------------------------

.. code-block:: python

    from lfs.plugins import PM_ORDER_IMMEDIATELY

    def get_create_order_time(self):
        return PM_ORDER_ACCEPTED

This method is called from LFS to determine when the order is to be created and
must return one of following values:

PM_ORDER_IMMEDIATELY
    The order is created immediately before the payment is processed.

PM_ORDER_ACCEPTED
    The order is created when the payment has been processed and accepted.

Add the ``get_pay_link`` method
--------------------------------

In order to provide a link to the customer to re-visit the payment provider and
pay his order (if something did go wrong) LFS calls get ``get_pay_link method``
or your class (this is optional).

.. code-block:: python

    def get_pay_link(self):
        return "http://www.acme.com/payment?id=4711&total=%s" % total

The complete plugin
===================

Following all pieces are sticked together to the complete plugin:

.. code-block:: python

    from lfs.plugins import PaymentMethodProcessor
    from lfs.plugins import PM_ORDER_IMMEDIATELY

    class ACMEPaymentMethodProcessor(PaymentMethodProcessor):
        """
        Implements the ACME payment processor.
        """
        def process(self):
            return {
                "accepted": True,
                "next_url": self.get_pay_link(),
            }

        def get_create_order_time(self):
            return PM_ORDER_IMMEDIATELY

        def get_pay_link(self):
            total = self.order.price
            return "http://www.acme.com/payment?id=4711&total=%s" % total

In this example the order is created immediately and the customer is redirected
to the ACME page in order to pay his order. After he has paid he might be
redirected to the ``thank-you`` page of LFS, but this is completely up to ACME.
However, if something goes wrong while he is paying he can always go back to
ACME to pay his order because he gets the pay link via the order confirmation
mail.

Plug in your payment method
===========================

Now as the code is ready, you can easily plugin your payment method:

#. Add your application to the PYTHONPATH.

#. Add the class to the :ref:`LFS_PAYMENT_METHOD_PROCESSORS
   <settings_lfs_payment_method_processors>` setting.

#. If your are using models (which is completely up to you), add the application
   to settings.INSTALLED_APPS and sync your database.

#. :doc:`Add a new payment method </user/howtos/how_to_payment_method>` and
   select your payment method within the ``module`` field.

#. Select the ``type`` of your payment method. Following types are provided:

   * Plain - no further fields are displayed.

   * Bank - fields to enter a bank account are displayed.

   * Credit Card - fields to enter a credit cart are displayed.

#. Save the payment method.

Further hints
=============

* Within the ``PaymentMethodProcessor`` request, the current order or the
  current cart are available as instance variables::

    self.request
    self.cart (only when get_create_order_time returns PM_ORDER_ACCEPTED)
    self.order (only when get_create_order_time returns PM_ORDER_IMMEDIATELY)

* When an external payment processor redirects to LFS the current order is still
  in the session. This means you can redirect to an own view and set the order
  state to PAID, for instance::

        from django.core.urlresolvers import reverse
        from django.http import HttpResponseRedirect
        from lfs.plugins import PAID

        def acme_callback_success_view(request):
            order = request.session.get("order")
            order.state = PAID
            order.save()

            return HTTPRedirectResponse(reverse("lfs_thank_you"))

* All fields of the checkout form are available within the ``process`` method
  via the request variable, e.g.::

     request.POST.get("invoice_firstname")

See also
=========

* :ref:`PaymentMethodProcessor API <payment_method_proccessor>`
