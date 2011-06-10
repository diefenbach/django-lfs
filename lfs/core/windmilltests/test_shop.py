from windmill.authoring import  WindmillTestClient

def setup_module(module):
    pass
    

def test_recordingSuite0():
    client = WindmillTestClient(__name__)
    client.click(id=u'2011-a')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(timeout=u'8000', id=u'id_first_name')
    client.type(text=u'Search stuff', id=u'id_search')
    return

def teardown_module(module):
    pass