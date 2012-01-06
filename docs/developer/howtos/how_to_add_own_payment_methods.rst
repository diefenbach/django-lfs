================================
How to add an own payment method
================================

In this how-to you will learn how to add a own payment method.

Create an application
=====================

First you need to create a default Django application (or use an existing one).
If you do not know how to do this, please refer to the excellent `Django
tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement the PaymentMethod class
=================================

Create the class
----------------

Create a class which inherits from ``lfs.plugins.PaymentMethod``:

.. code-block:: python

    from lfs.plugins import PaymentMethod
    class MyPaymentMethod(PaymentMethod)

Add the ``process`` method
--------------------------

.. code-block:: python

    def process(self, request, cart=None, order=None)

This method is called from LFS when the shop customer submits the checkout page
(while selected this payment method). Within that method you can do whatever
it is necessary to process your payment, e.g.:

* Call an API via HTTP(S)

* Redirect to another URL

Return Value
^^^^^^^^^^^^

The ``process`` method must return a dictionary with following keys (some of
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

    def get_create_order_time(self)

This method is called from LFS to determine when the order is to be created and
must return one of following constants::

PM_ORDER_IMMEDIATELY
    The order is created immediately before the payment is processed.

PM_ORDER_ACCEPTED
    The order is created when the payment has been processed and accepted.

Add the ``get_pay_link`` method
--------------------------------

In order to provide a link to the customer to re-visit the payment provider and
pay his order (if something did go wrong) LFS calls get get_pay_link method.

.. code-block:: python

    def get_pay_link(self):
        return "http://www.domain.com/your/pay/link"

The complete plugin
===================

Following all pieces are sticked together to the complete plugin.

.. code-block:: python

    from lfs.plugins import PaymentMethod
    from lfs.plugins import PM_ORDER_IMMEDIATELY

    class ACMEPaymentMethod(PaymentMethod):
        """
        Implements the ACME payment processor.
        """
        def process(self, request, cart=None, order=None):
            return {
                "accepted": True,
                "next_url": self.get_pay_link(order),
            }

        def get_create_order_item(self):
            return PM_ORDER_IMMEDIATELY

        def get_pay_link(self, order):
            total = order.price
            return "http://www.acme.de/payment?id=4711&total=%s" % total

In this example the order is created immediately and the customer is redirected
to the ACME page in order to pay his order. After he has paid he is redirected
to the ``thank-you`` page, but this is completely up to ACME. If something goes
wrong while he is paying he can always go back to ACME to pay his order because
he gets the pay link via the order confirmation mail.

Plug in your payment method
===========================

Now as the code is ready, you can easily plugin your payment method:

#. Add your application to the PYTHONPATH.

#. Add the application to settings.INSTALLED_APPS.

#. If your are using models (which is completely up to you), sync your database.

#. :doc:`Add a new payment method </user/howtos/how_to_payment_method>` and
   enter the dotted name to your payment method class into the ``module`` field.

#. Select the ``type`` of your payment method. Following types are provided:

   * Plain - no further fields are displayed.

   * Bank - fields to enter a bank account are displayed.

   * Credit Card - fields to enter a credit cart are displayed.

#. Save the payment method.

Further hints
=============

* When an external payment processor redirects to LFS the current order is still
  in the session. This means you can display it on the thank you page or you can
  redirect to a own view and set the order to PAID for instance.

