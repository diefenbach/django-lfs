# python imports
import os
import csv

# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

# django imports
from django.http import HttpResponse

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.models import ProductAccessories
from lfs.catalog.models import Image

def test(request):
    """
    """
    return render_to_response("test.html", RequestContext(request))    

def upload_test(request):
    """
    """
    if request.method == "GET":
        return render_to_response("testuploadform.html")

    return HttpResponse()

UPDATE_PATH = "/Users/Kai/Temp/dh2"
def update_accessories_from_es(request):
    """Imports accessories from es
    """
    fh_accessories = open("%s/accessories.csv" % UPDATE_PATH)
    reader = csv.reader(fh_accessories, delimiter=";", quotechar="'")
    
    for row in reader:
        try:
            product   = Product.objects.get(sku=row[0])
            accessory = Product.objects.get(sku=row[1])
        except:
            pass
        else:
            print "Product: %s" % product.name

            try:
                pa = ProductAccessories.objects.get(product=product, accessory=accessory)
            except ObjectDoesNotExist:
                print "Created Accessory: %s" % accessory.name
                ProductAccessories.objects.create(product=product, accessory=accessory, quantity=row[2], position=row[3])
            else:
                print "Updated Accessory: %s" % accessory.name
                pa.quantity = row[2]
                pa.position = row[3]
                pa.save()
    
    return HttpResponse("")
    
def update_images_from_es(request):
    """
    """
    # First we delete all images
    Image.objects.all().delete()
    
    # sku, filename
    fh_images = open("%s/product_images.csv" % UPDATE_PATH)
    reader = csv.reader(fh_images, delimiter=";", quotechar="'")
    
    for row in reader:
        # assign
        try:
            product = Product.objects.get(sku=row[0])
        except ObjectDoesNotExist:
            pass
        else:
            filename = row[1]
            fh_image = open(os.path.join(UPDATE_PATH, "product_images", filename))
        
            # create image
            cf = ContentFile(fh_image.read())
            image = Image(title="Image 1")
            image.image.save(filename, cf)
            image.position = row[2]
            image.save()
            
            product.images.add(image)
    
    fh_image.close()
    return HttpResponse("")
    
def update_products_from_es(request):
    """
    """
    products_fh = open("%s/products.csv" % UPDATE_PATH)
    reader = csv.reader(products_fh, delimiter=";", quotechar="'")
            
    for row in reader:
        try:
            price = float(row[7])
        except:
            price = 0

        try:
            product = Product.objects.get(sku=row[2])
        except ObjectDoesNotExist:
            product = Product()
            product.slug = slugify(row[1])
            product.sku=row[2]
            print "Created Product: %s" % row[2]
        else:
            print "Updated Product: %s" % product.id
            
        product.name = row[3]
        product.price = price
        product.short_description = row[6]
        product.description = row[5]
        product.meta_description = row[4]
        product.for_sale = int(row[15])
        product.for_sale_price = row[16] 
        product.stock_amount = row[10]
        product.manage_stock_amount = not int(row[9])
        product.weight = row[11]
        product.height = row[13]
        product.length = row[12]
        product.width  = row[14]
        
        product.save()
                        
    return HttpResponse("")
                
PATH = "/Users/Kai/Temp/dh"
def import_easyshop(request):
    """Imports Categories, Products and Product Images from ES.
    """
    Category.objects.all().delete()
    Product.objects.all().delete()
    Image.objects.all().delete()
    
    ##### Categories
    categories_fh = open("%s/categories/categories.csv" % PATH)
    reader = csv.reader(categories_fh, delimiter=";", quotechar="'")
    
    # to save uid -> id for later use
    categories = {}
    products = {}
    for row in reader:
        category = Category.objects.create(
            name = row[2],
            slug = slugify(row[1]),
            description = row[6]
        )

        # We map the new lfs category id with Plone's UID and save it. This is 
        # later used to assign products, parent categories and images to the 
        # category
        categories[row[0]] = category.id

    # Now as all categories exist we go through the categories again and assign 
    # the parent category.
    categories_fh.seek(0)
    for row in reader:
        child_id  = categories[row[0]]
        parent_id = categories.get(row[3])
        
        category = Category.objects.get(pk=child_id)
        category.parent_id = parent_id
        category.save()

    ##### Category Images
    fh_images = open("%s/categories/images.csv" % PATH)
    reader = csv.reader(fh_images, delimiter=";", quotechar="'")
    
    for row in reader:
        filename = row[1]
        fh_image = open(os.path.join("%s/categories" % PATH, filename))
        cf = ContentFile(fh_image.read())
        
        category_id = categories.get(row[0])
        if category_id:
            category = Category.objects.get(pk=category_id)
            category.image.save(filename, cf)
            category.save()
                    
    ##### Products
    products_fh = open("%s/products/products.csv" % PATH)
    reader = csv.reader(products_fh, delimiter=";", quotechar="'")
    
    for row in reader:
        try:
            price = float(row[6])
        except:
            price = 0
        
        print len(row[2])
        
        product = Product.objects.create(
            name = row[2],
            slug = slugify(row[1]),
            sku = row[4],
            price = price,
            short_description = row[9],
            description = row[5],
        )
        
        # We map the new lfs product id with Plone's UID and save it. This is 
        # later used to assign images to the products
        products[row[0]] = product.id
        
        # Assign Categories
        for category_uid in row[7].split(","):
            category_id = categories.get(category_uid)
            if category_id:
                product.categories.add(category_id)
                product.save()
    
    ##### Product Image
    fh_images = open("%s/products/images.csv" % PATH)
    reader = csv.reader(fh_images, delimiter=";", quotechar="'")
    
    for row in reader:
        filename = row[1]
        fh_image = open(os.path.join("%s/products/" % PATH, filename))
        cf = ContentFile(fh_image.read())
        image = Image(title="Image 1")
        image.image.save(filename, cf)
        image.save()
        
        product_id = products.get(row[0])
        if product_id:
            product = Product.objects.get(pk=product_id)
            product.images.add(image)
    fh_image.close()
            
    return HttpResponse(reader)