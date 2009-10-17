Address management
==================

Some information regarding to address handling.

General
-------

* The shop customer can enter two addresses while he checks out: shipping and
  invoice address
* The shop customer first enters the invoice address
* If the shipping address differs from the invoice address he can additionally
  add a shipping address.

Storing
-------

Adresses
^^^^^^^^

* The order object stores both adresses in the designed fields separated from
  each other (no reference to the address objects of the customer) even if they
  don't differ. This data are kept forever even if the addresses of the customer
  changed later.
* The customer object stores references to addresses. If there is no shipping
  address the field will be let empty.

E-Mail
^^^^^^

* If the customer is registered the e-mail address will be stored in and 
  retrieved from Django's default user object. This e-mail address will then be 
  used and hence there will be no e-mail address field displayed to the customer
  on the checkout page.
* If the customer is not registered the e-mail adress will be stored within the 
  invoice address object hence there will be a e-mail address field displayed 
  to the customer on the checkout page.

Displaying
-----------

* Both addresses will be displayed on the order, even if they don't differ from 
  each other. This will happen automatically because both address fields will 
  be field when the order will be created (see `Storing`_)

Management
----------

* The shop customer can manage his addresses via "My account".
* At them moment he can enter maximal two adresses: one invoice and one shipping 
  address (This may be changed in future to an arbitrary amout). If there is 
  no shipping adress he can add one.