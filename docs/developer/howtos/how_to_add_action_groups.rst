.. _how_to_add_own_action_groups:

============================
How to add own action groups
============================

Overview
========

In this how-to you will learn how to add new ``Actions Groups`` and how to use
them within your templates.

Add a new action group
======================

1. Login as admin.

2. Go to Django's admin interface::

    http://localhost:8000/admin/

3. Go to ``Core / Action groups``.

4. Click on the ``Add Action Group`` button.

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

2. Click on the ``Add Action`` button.

3. Fill in the provided form and select your new group.

4. Click on the ``Save Action`` button.

See also
========

* :ref:`General about actions <actions_concepts>`
* :ref:`Actions management interace <actions_management>`
