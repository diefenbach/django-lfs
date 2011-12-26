How To Add Own Payment Methods
==============================

In this tutorial you will learn how to add own payment methods.

Create An Application
----------------------

First you need to create a default Django application (or use an existing one).
If you do not know how to do this, please refer to the excellent `Django
tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement The Payment Method
----------------------------

Add The Process Method
^^^^^^^^^^^^^^^^^^^^^^

Within ``views.py`` file of your application create a method called ``process``
(which is just a default Django view - means it takes the ``request`` as
the first parameter):

.. code-block:: python

    def process(request)

This method is called from LFS when the shop customer submits the checkout page
(while selected this payment method). Within that method you can do whatever
it is necessary to process your payment, e.g.:

    * Call an API via HTTP(S)
    * Redirect to another URL
    * Create an order out of the current cart

Create The Order
^^^^^^^^^^^^^^^^

If the payment was successfully you may want to create the order based on the
current card (this is not done by LFS automatically). However, this is
straightforward:

.. code-block:: python

    import lfs.order.utils
    order = lfs.order.utils.add_order(request)

Create A Pay-Link
^^^^^^^^^^^^^^^^^

For non-real-time payment processors (for instance like PayPal) you may want
to include a pay-link with which the customer can re-pay the order. This link
will be displayed to the customer on the ``thank-you`` page and is part of the
notifcation mail the customer receives when he has submitted an order. To do
that just create the link and add it to the order:

.. code-block:: python

    order.pay_link = "http://www.domain.com/your/pay/link"
    order.save()

Return Value
^^^^^^^^^^^^

The ``process`` method **must** return a dictionary with following keys (some of them are
optional):

**accepted** (mandatory)
  Indicates whether the payment was accepted. If the payment was
  accepted LFS redirects to the default ``thank-you`` page or to the
  given ``next-url`` (see below). If the payment was not accepted LFS
  stays on the ``checkout`` page and displays an optional message. Valid
  values are: True/False.

**next-url** (optional)
  Contains the next URL to which LFS is supposed to redirect after the
  payment was accepted. If this is not given LFS will redirect to the
  default ``thank-you`` page. Valid values are valid URLs.

**message** (optional)
  This message is displayed within the ``checkout`` page if the payment
  was not successfully. Valid values are valid strings.

**message-position** (optional)
  This is the position the message will be displayed within the ``checkout``
  page. If the key is not given the message will be displayed on top of
  the check out page. Valid values are ``default`` (on top of the checkout
  page), ``bank`` (on top of the bank account fields) and ``credit
  card`` (on top of the credit card fields).

Plug In The Payment Method
--------------------------

1. Add your application to the PYTHONPATH.
2. Add the application to settings.INSTALLED_APPS.
3. If your are using models (which is completely up to you), sync your database.
4. :doc:`Add a new payment method </user/howtos/how_to_payment_method>` and
   enter the dotted name of your application into the ``module`` field.
5. Select the ``type`` of your payment method. Following types are provided:

     * Plain - no further fields are displayed.
     * Bank - fields to enter a bank account are displayed.
     * Credit Card - fields to enter a credit cart are displayed.

6. Save the payment method.
