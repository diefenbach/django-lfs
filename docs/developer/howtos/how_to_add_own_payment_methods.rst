How to add own payment methods
==============================

In this tutorial you will learn how to add own payment methods.

This how to assumes that your are familiar with creating django applications.
If not please refer to the excellent `Django tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_

Create the payment method
-------------------------

* Create a standard application
* Within the ``views.py`` create a method called processed::

    def process(request)

  This method is called from LFS and you can do within that whatever is necessary
  to process your payment, e.g.:

        * Call an API via HTTPS
        * Redirect to another URL

  The method must return a dictionary with following keys:

    **success True/False** (mandatory)
      Indicates whether the payment was successfully or not. If the payment was
      successfully LFS redirects to the default thank-you page or to the given
      next-url (see below). If the payment was not successfully LFS stays on
      the checkout page.

    **next-url** (optional)
      Contains the next URL to which LFS is supposed to redirect after the
      payment was succesfully. If this is not given LFS will redirect to the
      default thank-you page.

    **message** (optional)
      This is message is displayed within the checkout page if the payment was
      not successfully.

    **create-order True/False** (optional)
      Indicates wether LFS is supposed to create an order if the payment method
      was successfully or not.

    **order-state** (optional)
      Returns the state the newly created order should have after the payment
      has been successfully processed. If not state is given the order remains
      in ``submitted`` state. Only in In conjunction with ``create-order`` is  
      True. See ``lfs.order.settings`` for all valid states.

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