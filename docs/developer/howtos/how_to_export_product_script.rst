=====================================
How to create a product export script
=====================================

Overview
========

LFS provides a generic export engine for products :doc:`(see here for more)
</user/management/utils/export>`. In this tutorial you will learn how to
create your own scripts to format the data like you want to.

Create an application
======================

First you need to create a default Django application (or use an existing one).
If you do not know how to do this, please refer to the excellent `Django
tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Create the code
===============

Within the __init__.py of your application create a function that will return
the products, like so:

.. code-block:: python
    :linenos:

    # python imports
    import csv

    # django imports
    from django.http import HttpResponse
    from django.core.mail import send_mail

    # lfs imports
    from lfs.export.utils import register

    def export(request, export):
        """Export method for acme.com
        """
        response = HttpResponse(mimetype="text/csv")
        response["Content-Disposition"] = "attachment; filename=acme.txt"

        writer = csv.writer(response, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)

        for product in export.get_products():
            writer.writerow(product.id, product.get_name())

        return response

    register(export, "acme.com")

The code explained
-------------------

1-6
    Some simple Python and Django imports. These may vary for your code.

9
    Imports the register method to register your script.

11
    The function which will contain your code to create the exported data.

14/15
    We decided to give a response with a download back. Your code may vary here.

16
    We decided to use Python csv modules. You code may vary here.

19
    All selected products can be get with the ``get_products`` method of the
    passed export object.

24
    The registration of your function. This line must be called while Django
    is starting up.

Plug in the export script
=========================

Now go ``Utils / Export`` within the LFS Management Interface, create a new
export, select the products and your newly script and call it via the ``Export``
button. :doc:`(See here for more) </user/management/utils/export>`.
