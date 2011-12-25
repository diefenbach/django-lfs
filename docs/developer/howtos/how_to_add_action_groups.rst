.. _how_to_add_own_action_groups:

============================
How to add own action groups
============================

Overview
========

* ``Actions`` are used to provide an easy and flexible way to add links to the shop.

* ``Actions`` are grouped by ``Action Groups``. By default there are two groups,
  which constitutes the ``Tabs`` (the horizontal menu) and the ``footer``.

* In this how-to you will learn how to add new ``Actions Groups`` and how to
  use them within your templates.

Add a new action group
======================

1. Login as admin.
2. Go to Django's admin interface::

    http://localhost:8000/admin/

3. Go to ``Core / Action groups``.
4. Click on the ``Add action group`` button.
5. Enter the name of the group, e.g. ``Sidebar``.

Display the actions within your templates
=========================================

Insert the ``actions`` tag to your template as following:

.. code-block:: html

    {% actions Sidebar %}
    {% for action in actions %}
        <div>
            <a href="{{ action.link }}">
                {{ action.title }}
            </a>
        </div>
    {% endfor %}

.. note::

    We pass the above given group name to the ``actions`` tab. In this case
    ``Sidebar``.

Add actions to the group
========================

1. Open the :term:`LMI` and go to ``Shop / Actions``.
2. Click on the ``Add action`` button.
3. Fill in the provided form and select your new group.
4. Click on the ``Save action`` button.

See also
========

* :ref:`General about actions <actions>`
* :ref:`Actions management interace <actions_management>`
