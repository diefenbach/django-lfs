from windmill.authoring import  WindmillTestClient


def setup_module(module):
    pass


def test_cart_prices():
    client = WindmillTestClient(__name__)
    client.open(url="/product/chocolate")
    client.waits.forPageLoad(timeout=u'20000')

    # check that product includes vat
    client.asserts.assertText(xpath=u"//form[@id='product-form']/div[5][@class='prices']/div[2][@class='price-disclaimer']", validator=u'*inc. VAT')

    client.waits.forElement(timeout=u'8000', name=u'add-to-cart')
    client.click(name=u'add-to-cart')
    client.waits.forPageLoad(timeout=u'20000')
    client.open(url="/product/apple")
    client.waits.forPageLoad(timeout=u'20000')

    # check that product excludes vat
    client.asserts.assertText(xpath=u"//form[@id='product-form']/div[5][@class='prices']/div[2][@class='price-disclaimer']", validator=u'*exc. VAT')

    client.waits.forElement(timeout=u'8000', name=u'add-to-cart')
    client.click(name=u'add-to-cart')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Checkout', timeout=u'8000')
    client.click(link=u'Checkout')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Checkout', timeout=u'8000')
    client.click(link=u'Checkout')
    client.waits.forPageLoad(timeout=u'20000')

    # check net price of chocolate
    client.asserts.assertText(xpath=u"//div[@id='cart-inline']/table[@class='lfs-default cart']/tbody/tr[2]/td[4][@class='number']", validator=u'61.67 EUR')

    # check vat on chocolate
    client.asserts.assertText(xpath=u"//div[@id='cart-inline']/table[@class='lfs-default cart']/tbody/tr[2]/td[5][@class='number']", validator=u'(8.33 EUR)')

    # check total on chocolate
    client.asserts.assertText(xpath=u"//div[@id='cart-inline']/table[@class='lfs-default cart']/tbody/tr[2]/td[6][@class='number']", validator=u'70.00 EUR')

    # check net price of apple
    client.asserts.assertText(xpath=u"//div[@id='cart-inline']/table[@class='lfs-default cart']/tbody/tr[3]/td[4][@class='number']", validator=u'80.00 EUR')

    # check vat on apple
    client.asserts.assertText(xpath=u"//div[@id='cart-inline']/table[@class='lfs-default cart']/tbody/tr[3]/td[5][@class='number']", validator=u'(16.80 EUR)')

    # check total on apple
    client.asserts.assertText(xpath=u"//div[@id='cart-inline']/table[@class='lfs-default cart']/tbody/tr[3]/td[6][@class='number']", validator=u'96.80 EUR')


def teardown_module(module):
    pass
