Getting started
===============

This document explains the first steps after the shop has been installed. For 
installation please refer to :doc:`installation`.

Enter basic information
-----------------------
At first you should go to the shop's preferences and enter basic information. 
For that please 

   * visit http://localhost:8000/manage
   * login with admin/admin
   * browse to Shop / Preferences

Go to the "Shop" tab.

   * Enter a "Name". This is the name of the shop, e.g. *ACME Inc*. It will be used on several
     places, e.g. as the title of all HTML pages.
 
   * Enter the "Shop owner". This is the fullname of the shop owner, e.g. *John Doe*
 
   * Enter "From e-mail address". This e-mail address is used as sender
     for all e-mails which are sent from the shop, e.g. the order has been
     received message to the shop customer.
 
   * Enter "Notification e-mail addresses". To this adresses all notification
     messages will be sent. For example if an order has been submitted.
 
Go to the "Default Values" tab.

   * Select *"Countries"*. All selected countries will be available to the
     shop customers for selection.
 
   * Select *"Default Country"*. This country will be preselected as default country.
 
Enter first category and products
---------------------------------

Now go to Catalog / Categories and add a new category.

Since there are no catgories yet, you will be redirected automatically to the
add category form.

   * Enter "name" and a ``slug" (you will see, that the slug is filled 
     automatically but you can change it of course)
   * Enter a "short description". This will be displayed when the category is
     displayed within a overview, e.g. when a category displays is sub
     cateogories
   * Enter a "description". This will be displayed within the detail view of 
     a category when description as content is selected.
   * Select the "kind of content", this is ``products" (the assigned 
     products of the category will), "categories" (the sub categories of the 
     category will be dsiplay) or "description" (the description field will 
     be displayed)
   * Now save the category
 
Now go to Catalog / Products and add a new Product.

Since there is no product yet, you will redirected automatically to the add
product form.

   * Enter "name" and a ``slug" (you will see, that the slug is filled 
     automatically but you can change it of course)
   * Enter the "SKU" of the product. This is the unique external id of the 
     product - taken from your ERP for instance
   * Enter the "price" of the product
   * Click "Add product"
 
Now you can add more data to your product:

Go to the "Product" tab

   * Enter a "short description". This will be displayed when the product is
     displayed within a overview, e.g. when a category displays it's assigned
     products.
   * Enter a "description". This will be displayed within the detail view of 
     a product.
   * Click "Save data"
 
Go to the "Categories" tab

   * Select the above entered category and click "Save categories".

Go to the "Images" tab

   * Click "Select images" browse to your images and select all images you
     want to upload.

Go to the "Product" tab

   * Select "active" and click "Save product"
   * Click on "View product" to view your new product

What's next?
------------

Now you can:

   * add more catgories and products
   * add accessories and/or related products to your products
   * add variants
   * manage taxes
   * manage shipping and payment methods
   * manage delivery times and stock information
   * Add some portlets to your shop and/or categories