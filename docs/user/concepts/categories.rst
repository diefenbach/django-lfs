.. index:: Category

.. _categories_concepts:

==========
Categories
==========

This section describes the categories of LFS.

* ``Categories`` are used to structure products.

* Every ``Category`` can have either one or no parent ``Category``. In this
  way the ``Category`` tree is built. If the ``Category`` has no parent
  it is a so-called top level ``Category``.

* Every ``Category`` can have an arbitrary amount of products.

* A ``Category`` can either display its sub categories or its products. This
  is up to the selected template.

* A ``Category`` can have portlets. By default the portlets are inherited to the
  sub categories resp. to the assigned products but they can be blocked per
  :term:`slot`.

* A ``Category`` can have a :ref:`static block <static_blocks>` which are
  displayed on top of the ``Category``.

See also
========

* :ref:`Category Management Interface <categories_management>`
