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

Action groups are not part of the management interface; create one in the Django shell::

    $ python manage.py shell -c "from lfs.core.models import ActionGroup; ActionGroup.objects.create(name='Sidebar')"

Display the actions within your templates
=========================================

Insert the ``actions`` tag of ``lfs_tags`` into your template:

.. code-block:: html

    {% load lfs_tags %}

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

1. Go to ``Shop / Actions``.

2. Click on the ``Add Action`` button.

3. Enter the title and the link, select your new group, and click ``Add Action``.

4. Check ``Active`` and click ``Save``.

See also
========

* :ref:`General about actions <actions_concepts>`
* :ref:`Actions management interace <actions_management>`
