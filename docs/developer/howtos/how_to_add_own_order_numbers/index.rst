How to add an own order numbers generator
=========================================

LFS order numbers generator is  pluggable. In this tutorial you will learn how
to add an own order numbers generator.

Please see also the :download:`complete example application
<country_specific_order_numbers.tar.gz>` or refer to the default
implementation of LFS within ``lfs_order_numbers``.

Create an application
----------------------

First you need to create a default Django application (or use an existing one).

If you do not know how to do this, please refer to the excellent
`Django tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

The structure of the application should look at least like this::

    my_order_numbers
        __init__.py
        forms.py
        models.py


Implement the application
-------------------------

**Add the model**

Within ``models.py`` file of your application create a class called
``OrderNumberGenerator`` which inherits from LFS' OrderNumberGenerator base
class and add a method to it called ``get_next``:

.. code-block:: python

    from lfs.order_numbers import OrderNumberGenerator as Base

    class OrderNumberGenerator(Base):
        def get_next(formatted):
            return "DOE-4711"

The ``get_next`` method is called when the shop customer submits a new order.
It **must** return a character value which will become the order number of the
new order.

**Add the form**

Within ``forms.py`` of the newly created package add a form called
``OrderNumberGeneratorForm``. This form is used to edit the order numbers
within the management interface of LFS.

.. code-block:: python

    class OrderNumberGeneratorForm(forms.ModelForm):
        class Meta:
            model = OrderNumberGeneratorForm

The ``OrderNumberGeneratorForm`` **must** inherit from ModelForm.

Register your plugin
--------------------

In order to register the plugin add your application to ``INSTALLED_APPS``
and assign your application to ``LFS_APP_ORDER_NUMBERS`` within settings.py::

    INSTALLED_APPS = ("my_order_numbers", ...)
    LFS_APP_ORDER_NUMBERS = "my_order_numbers"

At last run syncdb and restart your instance.

**And that's it**

You should now see your form within the ``Order Numbers``-tab within
Shop/Preferences management interface and the ``get_next``-method of your
model should be called to generate a new order number.

Optionally add your own template
--------------------------------

Optionally you can add your own HTML for the management interface. For this
just add the order_numbers_tab.html template to your application::

    my_order_numbers
        templates
            manage
                order_numbers
                    order_numbers_tab.html

Please refer to the standard template of LFS to get more details. You can find
this on following place::

    lfs/templates/manage/order_numbers/order_numbers_tab.html

.. Note::

    In this case  please make sure that your ``my_order_numbers`` application
    is **before** ``lfs`` within ``INSTALLED_APPS`` of ``settings.py`` so that the
    LFS' default template is overwritten.
