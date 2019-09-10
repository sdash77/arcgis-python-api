from unittest.mock import MagicMock

class MockConnection(MagicMock):
    post = MagicMock()
    get = MagicMock()
    put = MagicMock()
    delete = MagicMock()
    token = MagicMock()
    pass
