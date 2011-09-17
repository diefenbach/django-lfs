from windmill.authoring import  WindmillTestClient


def setup_module(module):
    pass


def test_manage_setting_of_price_calculator():
    client = WindmillTestClient(__name__)
    client.open(url="/product/chocolate")
    client.waits.forPageLoad(timeout=u'20000')

    # check that product includes vat
    client.asserts.assertText(xpath=u"//form[@id='product-form']/div[5][@class='prices']/div[2][@class='price-disclaimer']", validator=u'*inc. VAT')

    # open the manage interface
    client.open(url="/manage/")
    client.waits.forPageLoad(timeout=u'20000')
    client.type(text=u'admin', id=u'id_username')
    client.type(text=u'admin', id=u'id_password')
    client.click(xpath=u"//div[@id='content']/div/div[1]/form/button")
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Products', timeout=u'8000')
    client.click(link=u'Products')
    client.waits.forPageLoad(timeout=u'20000')
    client.click(link="Chocolate")
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(timeout=u'8000', id=u'id_price_calculator')
    client.click(id=u'id_price_calculator')
    client.select(option=u'Price excludes tax', id=u'id_price_calculator')
    client.click(xpath=u"//form[@id='product-data-form']/fieldset[4]/div[4]/div[2]")
    client.click(value=u'Save Data')

    # Check that price excludes vat now
    client.open(url="/product/chocolate")
    client.waits.forPageLoad(timeout=u'20000')

    # check that product includes vat
    client.asserts.assertText(xpath=u"//form[@id='product-form']/div[5][@class='prices']/div[2][@class='price-disclaimer']", validator=u'*exc. VAT')


def teardown_module(module):
    pass
