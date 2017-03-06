import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import override_settings

from lfs.catalog.models import Category, Product, Property, ProductsPropertiesRelation, PropertyOption, ProductPropertyValue
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, PROPERTY_SELECT_FIELD, VARIANT, PROPERTY_VALUE_TYPE_VARIANT
from lfs.core.models import Country
from lfs.criteria.models import Criterion, CountryCriterion
from lfs.shipping.models import ShippingMethod, ShippingMethodPrice


class ManageTestCase(TestCase):
    """Tests manage interface
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        for i in range(1, 4):
            cat, created = Category.objects.get_or_create(pk=i, name="cat" + str(i), slug="cat" + str(i), position=10,
                                                          parent=None)

        self.username = 'joe'
        self.password = 'bloggs'
        self.email = 'joe@example.com'

        new_user = User(username=self.username, email=self.email, is_active=True, is_superuser=True)
        new_user.set_password(self.password)
        new_user.save()

    # def test_category_sorting(self):
    #     """
    #     Test we get correct sorting of categories from json api
    #     """
    #
    #     self.assertEqual(3, Category.objects.count())
    #     csv = CategorySortView()
    #
    #     js = 'category[3]=root&category[1]=root&category[2]=1'
    #     csv.sort_categories(js)
    #     cat1 = Category.objects.get(pk=1)
    #     cat2 = Category.objects.get(pk=2)
    #     cat3 = Category.objects.get(pk=3)
    #
    #     # check positions are correct
    #     self.assertEqual(cat1.position, 20)
    #     self.assertEqual(cat2.position, 30)
    #     self.assertEqual(cat3.position, 10)
    #
    #     # check parents are correct
    #     self.assertEqual(cat1.parent, None)
    #     self.assertEqual(cat2.parent, cat1)
    #     self.assertEqual(cat3.parent, None)
    #
    #     js = 'category[1]=root&category[2]=root&category[3]=2'
    #     csv.sort_categories(js)
    #     cat1 = Category.objects.get(pk=1)
    #     cat2 = Category.objects.get(pk=2)
    #     cat3 = Category.objects.get(pk=3)
    #
    #     # check positions are correct
    #     self.assertEqual(cat1.position, 10)
    #     self.assertEqual(cat2.position, 20)
    #     self.assertEqual(cat3.position, 30)
    #
    #     # check parents are correct
    #     self.assertEqual(cat1.parent, None)
    #     self.assertEqual(cat2.parent, None)
    #     self.assertEqual(cat3.parent, cat2)

    def test_add_product(self):
        self.client.login(username=self.username, password=self.password)
        products_count = Product.objects.count()
        url = reverse('lfs_manage_add_product')
        response = self.client.post(url, {'name': 'Product name', 'slug': 'productslug'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(products_count + 1, Product.objects.count())

    def test_change_product_subtype(self):
        p = Product.objects.create(name='Product1', slug='product1')

        self.client.login(username=self.username, password=self.password)
        url = reverse('lfs_change_product_subtype', kwargs={'product_id': p.pk})
        response = self.client.post(url, {'sub_type': PRODUCT_WITH_VARIANTS}, follow=True)
        self.assertEqual(response.status_code, 200)
        p = Product.objects.get(pk=p.pk)
        self.assertEqual(p.sub_type, PRODUCT_WITH_VARIANTS)

    def test_manage_add_property(self):
        p = Product.objects.create(name='Product1', slug='product1', sub_type=PRODUCT_WITH_VARIANTS)
        self.client.login(username=self.username, password=self.password)
        url = reverse('lfs_manage_add_property', kwargs={'product_id': p.pk})
        response = self.client.post(url, {'name': 'testproperty'}, follow=True)
        self.assertEqual(response.status_code, 200)
        new_property = Property.objects.latest('id')
        self.assertEqual(new_property.name, 'testproperty')
        self.assertTrue(new_property.local)
        self.assertTrue(ProductsPropertiesRelation.objects.filter(product=p, property=new_property).exists())

    def test_manage_add_property_option(self):
        product = Product.objects.create(name='Product1', slug='product1', sub_type=PRODUCT_WITH_VARIANTS)
        pproperty = Property.objects.create(name='property 1', type=PROPERTY_SELECT_FIELD, local=True, filterable=False)
        ProductsPropertiesRelation.objects.create(product=product, property=pproperty, position=10)

        self.client.login(username=self.username, password=self.password)
        url = reverse('lfs_manage_add_property_option', kwargs={'product_id': product.pk})
        response = self.client.post(url, {'name': 'testpropertyoption', 'property_id': pproperty.pk}, follow=True)
        self.assertEqual(response.status_code, 200)
        new_property_option = PropertyOption.objects.latest('id')
        self.assertEqual(new_property_option.name, 'testpropertyoption')

    @override_settings(USE_L10N=True)
    @override_settings(LANGUAGE_CODE='pl')
    def test_manage_add_shop_property_option_with_locale(self):
        pproperty = Property.objects.create(name='property 1', type=PROPERTY_SELECT_FIELD, local=True, filterable=False)
        self.client.login(username=self.username, password=self.password)
        url = reverse('lfs_add_shop_property_option', kwargs={'property_id': pproperty.pk})

        # add property option with price defined using dot
        response = self.client.post(url,
                                    {'name': 'testpropertyoption',
                                     'action': 'add',
                                     'price': '0.5'}, follow=True)
        self.assertEqual(response.status_code, 200)
        new_property_option = PropertyOption.objects.latest('id')
        self.assertEqual(new_property_option.name, 'testpropertyoption')
        self.assertEqual(new_property_option.price, 0.5)

        # verify how value is shown within template, should be 0,5 due to language code and l10n
        data = json.loads(response.content)
        self.assertTrue('value="0,5"' in data['html'][0][1])

        # change price using comma as a separator and add another option
        response = self.client.post(url,
                                    {'name': 'testpropertyoption2',
                                     'action': 'add',
                                     'price': '0,7'}, follow=True)

        new_property_option2 = PropertyOption.objects.latest('id')
        self.assertEqual(new_property_option2.price, 0.7)

        # test options update
        response = self.client.post(url,
                                    {'name-{}'.format(new_property_option.pk): 'testpropertyoption',
                                     'position-{}'.format(new_property_option.pk): 10,
                                     'price-{}'.format(new_property_option.pk): '0.3',

                                     'name-{}'.format(new_property_option2.pk): 'testpropertyoption2',
                                     'position-{}'.format(new_property_option2.pk): 10,
                                     'price-{}'.format(new_property_option2.pk): '0,9',

                                     'option': [new_property_option.pk, new_property_option2.pk]
                                     }, follow=True)

        new_property_option = PropertyOption.objects.get(pk=new_property_option.pk)
        new_property_option2 = PropertyOption.objects.get(pk=new_property_option2.pk)

        self.assertEqual(new_property_option.price, 0.3)
        self.assertEqual(new_property_option2.price, 0.9)

    def test_manage_variants(self):
        product = Product.objects.create(name='Product1', slug='product1', sub_type=PRODUCT_WITH_VARIANTS)
        pproperty = Property.objects.create(name='property1', type=PROPERTY_SELECT_FIELD, local=True, filterable=False)
        ProductsPropertiesRelation.objects.create(product=product, property=pproperty, position=10)
        property_option = PropertyOption.objects.create(name='property option 1', property=pproperty, position=10)

        variant = Product.objects.create(name='variant', slug='vslug', parent=product, variant_position=10,
                                         sub_type=VARIANT)
        ProductPropertyValue.objects.create(product=variant, property_id=pproperty.pk,
                                            value=property_option.pk, type=PROPERTY_VALUE_TYPE_VARIANT)

        self.client.login(username=self.username, password=self.password)
        url = reverse('lfs_manage_variants', kwargs={'product_id': product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        outvariants = response.context['variants']
        self.assertEqual(len(outvariants), 1)
        self.assertEqual(len(outvariants[0]['properties']), 1)
        self.assertEqual(outvariants[0]['properties'][0]['name'], pproperty.name)
        self.assertEqual(outvariants[0]['properties'][0]['options'][0]['name'], property_option.name)

    def test_manage_update_variants(self):
        product = Product.objects.create(name='Product1', slug='product1', sub_type=PRODUCT_WITH_VARIANTS)
        pproperty = Property.objects.create(name='property1', type=PROPERTY_SELECT_FIELD, local=True, filterable=False)
        ProductsPropertiesRelation.objects.create(product=product, property=pproperty, position=10)
        property_option = PropertyOption.objects.create(name='property option 1', property=pproperty, position=10)

        variant = Product.objects.create(name='variant', slug='vslug', parent=product, variant_position=10,
                                         sub_type=VARIANT)
        ProductPropertyValue.objects.create(product=variant, property_id=pproperty.pk,
                                            value=property_option.pk, type=PROPERTY_VALUE_TYPE_VARIANT)

        self.client.login(username=self.username, password=self.password)
        url = reverse('lfs_manage_update_variants', kwargs={'product_id': product.pk})
        post_data = {
            'action': 'update',
            'variant-{}'.format(variant.pk): '',
            'position-{}'.format(variant.pk): '10',
            'active-{}'.format(variant.pk): '1',
            'slug-{}'.format(variant.pk): 'vslug',
            'active_sku-{}'.format(variant.pk): '',
            'sku-{}'.format(variant.pk): '123',
            'active_name-{}'.format(variant.pk): '',
            'name-{}'.format(variant.pk): 'variant',
            'property-{}|{}|{}'.format(variant.pk, 0, pproperty.pk): property_option.pk,
            'active_price-{}'.format(variant.pk): '1',
            'price-{}'.format(variant.pk): '0.99'
        }

        response = self.client.post(url,
                                    post_data,
                                    follow = True)
        self.assertEqual(response.status_code, 200)

        variant = Product.objects.get(pk=variant.pk)
        self.assertEqual(variant.sku, '123')
        self.assertEqual(variant.price, 0.99)

        # update variant using comma as price separator
        post_data['price-{}'.format(variant.pk)] = '3,44'
        response = self.client.post(url,
                                    post_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        variant = Product.objects.get(pk=variant.pk)
        self.assertEqual(variant.price, 3.44)

    def test_manage_add_price_criteria(self):
        self.client.login(username=self.username, password=self.password)
        shipping_method = ShippingMethod.objects.create(name='Standard', active=True)
        smp = ShippingMethodPrice.objects.create(shipping_method=shipping_method, price=10)

        country_id = Country.objects.all()[0].pk

        url = reverse('lfs_manage_save_shipping_price_criteria', kwargs=dict(shipping_price_id=smp.pk))
        data = {'type-123': 'lfs.criteria.models.CountryCriterion',
                'operator-123': Criterion.IS_SELECTED,
                'position-123': '10',
                'value-123': country_id}

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)

        c = CountryCriterion.objects.latest('id')
        self.assertTrue(country_id in c.value.values_list('id', flat=True))
