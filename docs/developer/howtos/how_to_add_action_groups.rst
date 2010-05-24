============================
How to add own action groups
============================

Overview
========

Actions are used to provide an easy and flexible way to add links to the shop.

Actions are grouped by action groups. By default there is only one group, 
which constitutes the tabs (the horizontal menu).

In this how-to you will learn how to add new actions groups and use them within 
your templates.

Add a new action group
======================

1. Login as admin
2. Go to Django's admin interface::

    http://localhost:8000/admin/

3. Go to Core / Action groups
4. Click on "Add action group" button
5. Enter the name of the group, e.g. "Footer"

Display the actions within your templates
=========================================

Insert the "actions" tag to your template as following:

.. code-block:: html

    {% actions <group-id> %}
    {% for action in actions %}
        <div>
            <a href="{{ action.link }}">
                {{ action.title }}
            </a>
        </div>
    {% endfor %}

Whereas the group-id is the id of the newly create group above.

Add actions to the group
========================

1. Go to Management / Shop / Actions.
2. Click on the "Add action" button.
3. Fill in the provided form and select your new group.
4. Click on the "Save action" button.

.. seealso:: 

    * :doc:`/user/shop/actions`