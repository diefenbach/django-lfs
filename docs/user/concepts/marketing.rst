.. index:: Marketing

.. _marketing_concepts:

=========
Marketing
=========

This section describes the marketing features of LFS.

.. _marketing_concepts_accessories:

Accessories
===========

Accessories are products which are supposed to be sold together with a product,
like shingles to a summerhouse. They are not bidirectional but they need need to
be entered on each product itself.

Accessories are displayed within the ``product view`` and could be added to the
cart alongside with the product. They are also displayed within the ``added to
cart view`` (the view is displayed after a shop customer has added a product to
the cart) in order to offer them to be also added to the cart.

.. _marketing_concepts_discounts:

Discounts
=========

Discounts are a possibility to give a price reduction to customers. They can be
absolute or percentaged based on the total cart price. Discounts can be
restricted by :ref:`criteria <criteria_concepts>` and they are only given if it
meets all criteria. The shop owner can add an arbitrary amount of discounts.

.. _marketing_concepts_featured_products:

Featured Products
=================

Featured products are several product which are supposed to be exposed to the
customer for any reason. They are :doc:`management manually
</user/management/marketing/featured>` an can be displayed displayed to the
customer via the :ref:`featured product portlet
<portlets_concepts_featured_products>`.

.. _marketing_concepts_rating_mails:

Rating Mails
============

Shop owners can send :ref:`rating mails <rating_mails_management>` to shop
customers in order to ask them to rate the products they bought. See also
:ref:`review concepts <reviews_concept>` for more information.

.. _marketing_concepts_related_products:

Related Products
================

Related products are products which are somehow related to a product. They are
not bidirectional related but they need to be assigned to every single product.

Related products can be displayed within the :ref:`Related Products Portlet
<portlets_concepts_related_products>`.

.. _marketing_concepts_top_seller:

Top seller
==========

Top seller are best sold products of the shop. They are calculated automatically
but can be also :doc:`manipulated manually
</user/management/marketing/topseller>`. They are displayed within the :ref:`top
seller portlet <portlets_concepts_top_seller>`

.. _marketing_concepts_vouchers:

Vouchers
========

Vouchers are another possibility to give a price reduction for customers. The
price reduction can be absolute or percentaged based on the total cart price.

They are generic character strings which can be distributed to customers. If a
valid voucher string is entered within the cart or as part of the checkout
process the customer gets the price reduction.

Vouchers can be limited by a start and an end date or a minimum cart price.

Vouchers expire when they have been used for a certain amount of times. A common
way is to expire the voucher right after it has been used the first time.

The shop owner can add an arbitrary amount of vouchers. They can be of the same
or of different types.

See also
========

* :ref:`Discounts Management Interface <discounts_management>`
* :ref:`Products Management Interface <products_management>`
* :ref:`Rating Mails Management Interface <rating_mails_management>`
* :ref:`Review Concepts <reviews_concept>`
* :ref:`Vouchers Management Interface <vouchers_management>`
