import unittest
import uuid
from arcgis.auth._auth._token import EsriBuiltInAuth

class TestBuiltInAuthTokenParser(unittest.TestCase):
    """Tests working with the built-in authentication token parser."""
    def test_match_oauth_info_valid(self):
        html = '<html><head><script>var oAuthInfo = {"oauth_state": "abc123", "foo": "bar"};</script></head></html>'
        result = EsriBuiltInAuth._match_oauth_info(html)
        assert result is not None
        assert result["oauth_state"] == "abc123"
        assert result["foo"] == "bar"

    def test_match_oauth_info_valid_no_semicolon_valid(self):
        html = '<html><head><script>var oAuthInfo = {"oauth_state": "xyz789"}</script></head></html>'
        result = EsriBuiltInAuth._match_oauth_info(html)
        assert result is not None
        assert result["oauth_state"] == "xyz789"

    def test_match_oauth_info_fallback_on_first_object_valid(self):
        html = '<html><head><script>var anotherObject = {"oauth_state": "abc123"}</script></head></html>'
        result = EsriBuiltInAuth._match_oauth_info(html)
        assert result is not None
        assert result["oauth_state"] == "abc123"

    def test_match_oauth_info_missing(self):
        html = '<html><head><title>Login</title></head></html>'
        result = EsriBuiltInAuth._match_oauth_info(html)
        assert result is None

    def test_match_success_code(self):
        expected = uuid.uuid4().hex
        html = f'<html><head><title>SUCCESS code={expected}</title></head></html>'
        code = EsriBuiltInAuth._match_success_code(html)
        assert code == expected

    def test_match_success_code_missing(self):
        html = '<html><head><title>404</title></head></html>'
        code = EsriBuiltInAuth._match_success_code(html)
        assert code is None

    def test_match_password_reset(self):
        text = '{"oauth_state": "reset123"}'
        result = EsriBuiltInAuth._match_password_reset(text)
        assert result is not None
        assert result["oauth_state"] == "reset123"

    def test_match_password_reset_invalid(self):
        text = 'no json here'
        result = EsriBuiltInAuth._match_password_reset(text)
        assert result is None
