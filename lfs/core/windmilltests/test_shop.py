from windmill.authoring import  WindmillTestClient


def setup_module(module):
    pass


def test_recordingSuite0():
    client = WindmillTestClient(__name__)
    client.type(text=u'Search stuff', id=u'search-input')
    return


def teardown_module(module):
    pass
