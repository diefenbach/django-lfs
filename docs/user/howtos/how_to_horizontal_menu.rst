============================
How To Add a Horizontal Menu
============================

The menu at the top of the default theme lfs-theme shows the top-level categories: add a category under ``Catalog /
Categories`` (and uncheck ``Exclude from navigation``) and it appears in the menu. The order follows the category
tree; drag the categories there to change it.

Further links are :ref:`actions <actions_management>`. lfs-theme shows the actions of the group ``Footer`` in the
footer:

#. Go to ``Shop / Actions`` and click ``Add action``.

#. Enter the ``Title`` (the text of the link) and the ``Link``: a path of the shop such as ``/page/about-us/``, a
   full URL, or a ``mailto:`` link. Select the ``Group`` ``Footer`` and add the action.

#. Check ``Active`` and click ``Save``. Only active actions are shown.

#. To change the order, drag the actions in the list on the left.

.. note::

    lfs-theme 1.0 does not show the actions of the group ``Tabs`` (e.g. ``Contact``, which ``lfs_init`` creates).
    A theme of your own can show them with the template tag ``{% actions Tabs %}`` from ``lfs_tags``.
