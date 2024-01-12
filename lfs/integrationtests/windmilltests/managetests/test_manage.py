from windmill.authoring import WindmillTestClient


def setup_module(module):
    pass


def test_manage_setting_of_price_calculator():
    client = WindmillTestClient(__name__)
    client.open(url="/product/chocolate")
    client.waits.forPageLoad(timeout="20000")

    # check that product includes vat
    client.asserts.assertText(
        xpath="//form[@id='product-form']/div[5][@class='prices']/div[2][@class='price-disclaimer']",
        validator="*inc. VAT",
    )

    # open the manage interface
    client.open(url="/manage/")
    client.waits.forPageLoad(timeout="20000")
    client.type(text="admin", id="id_username")
    client.type(text="admin", id="id_password")
    client.click(xpath="//div[@id='content']/div/div[1]/form/button")
    client.waits.forPageLoad(timeout="20000")
    client.waits.forElement(link="Products", timeout="8000")
    client.click(link="Products")
    client.waits.forPageLoad(timeout="20000")
    client.click(link="Chocolate")
    client.waits.forPageLoad(timeout="20000")
    client.waits.forElement(timeout="8000", id="id_price_calculator")
    client.click(id="id_price_calculator")
    client.select(option="Price excludes tax", id="id_price_calculator")
    client.click(xpath="//form[@id='product-data-form']/fieldset[4]/div[4]/div[2]")
    client.click(value="Save Data")

    # Check that price excludes vat now
    client.open(url="/product/chocolate")
    client.waits.forPageLoad(timeout="20000")

    # check that product includes vat
    client.asserts.assertText(
        xpath="//form[@id='product-form']/div[5][@class='prices']/div[2][@class='price-disclaimer']",
        validator="*exc. VAT",
    )


def teardown_module(module):
    pass
