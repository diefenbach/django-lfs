How to add own payment methods
==============================

In this tutorial you will learn how to add own payment methods.

This how to assumes that your are familiar with creating django applications.
If not please refer to the excellent `Django tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_

Create the payment method
-------------------------

* Create a standard application
* Within ``views.py`` create a method called ``processed``::

    def process(request)

  This method is called from LFS when the shop customer submits the order 
  (while selected this payment method). Within that method you can do whatever 
  it is necessary to process your payment, e.g.:

        * Call an API via HTTP(S)
        * Redirect to another URL
        * Create an order out of the current cart

  The method must return a dictionary with following keys:

    **accepted** (mandatory)
      Indicates whether the payment was accepted. If the payment was
      accepted LFS redirects to the default ``thank-you`` page or to the 
      given ``next-url`` (see below). If the payment was not accepted LFS
      stays on the ``checkout`` page and displays an optional message. Valid 
      values are: True/False.

    **next-url** (optional)
      Contains the next URL to which LFS is supposed to redirect after the
      payment was succesfully. If this is not given LFS will redirect to the
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

Plug the payment method in
--------------------------

* Add your application to the PYTHONPATH
* Add the application to settings.INSTALLED_APPS
* If your are using models sync your database
* Add a new payment method and enter the dotted name of your application to 
  the ``module`` field.
* Select the ``type`` of your payment method. Following types are provided:

     * Plain - no further fields are displayed
     * Bank - fields to enter a bank account are displayed
     * Credit Card - fields to enter a credit cart are displayed.
     
* Save the payment method