Customer
========

There are some custom views for login and logout:

customer.views.login
--------------------

The reasons to use a custom login method is: 

  * check checkout type
  * integration of register and login form

checkout.views.login
--------------------

This a slightly different login method which is called within the checkout 
process if it appropriate.

The reasons to use a custom login method is: 

  * check checkout type
  * integration of register and login form

Both login methods are using the Django's standard AuthenticationForm

customer.views.logout
---------------------  
The reasons to use a customer logout method is 

  * just to be complete (provide login and logout).

:mod:`Customer`
===============
  
Models 
------
.. automodule:: lfs.customer.models

   .. autoclass:: Customer
   .. autoclass:: Address
   .. autoclass:: BankAccount   
   .. autoclass:: CreditCard   

Utils 
------   
.. automodule:: lfs.customer.utils

   .. autofunction:: get_or_create_customer
   .. autofunction:: create_customer
   .. autofunction:: get_customer
   .. autofunction:: update_customer_after_login  