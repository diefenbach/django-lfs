import pickle


# For now LFS uses the "deprecated" Django PickleSerializer
# This needs to be changed to the JSONSerializer
class PickleSerializer:
    """
    Simple wrapper around pickle to be used in signing.dumps()/loads() and
    cache backends.
    """

    def __init__(self, protocol=None):
        self.protocol = pickle.HIGHEST_PROTOCOL if protocol is None else protocol

    def dumps(self, obj):
        return pickle.dumps(obj, self.protocol)

    def loads(self, data):
        return pickle.loads(data)
