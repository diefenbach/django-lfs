from django.conf.urls.defaults import *

# Shop
urlpatterns = patterns('lfs.utils.views',
    (r'^/test$', "test"),
    (r'^/upload-test$', "upload_test"),
    (r'^/import-easyshop$', "import_easyshop"),
    (r'^/update-products-from-es$', "update_products_from_es"),
    (r'^/update-product-images-from-es$', "update_images_from_es"),
    (r'^/update-accessories-from-es$', "update_accessories_from_es"),
)
