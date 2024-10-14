class Foo:
    """
    Sample Class for Unit Test Template
    This is a sample class that requires gis connection
    """

    def __init__(self, gis):
        self.gis = gis

    def foo_method(self, data):
        # a sample method in Foo class
        pass

    def _foo_private_method(self):
        # a sample private method in Foo class
        pass


# sample util functions
data = None
def util_function_a(data):
    pass

def util_function_b(data):
    pass
