"""Offline contract tests: no actual broker API or orders."""
import json
import unittest
from profitmart_adapter import ProfitmartClient, ProfitmartConfig, ProfitmartError, validate_order_preview


class TestProfitmartReadOnly(unittest.TestCase):
    def setUp(self):
        self.requests = []
        def fake(req):
            self.requests.append(req)
            if req.full_url.endswith("GetQuotes"):
                return json.dumps({"stat": "Ok", "lp": "1298.45", "tsym": "TCS-EQ", "exch": "NSE", "token": "11536", "ltt": "15:25:00"}).encode()
            return b'{"stat":"Ok","values":[]}'
        self.client = ProfitmartClient(
            ProfitmartConfig("https://api.example.com", "DEMO", "test-token"), fake
        )

    def test_quote_and_auth_header(self):
        q = self.client.quote("NSE", "11536")
        self.assertEqual(q["ltp"], "1298.45")
        req = self.requests[0]
        self.assertEqual(req.get_header("Authorization"), "Bearer test-token")
        self.assertIn(b'"token":"11536"', req.data)
        self.assertIn("/NorenWClientAPI/GetQuotes", req.full_url)

    def test_symbol_search_is_separate_from_quote_token(self):
        self.client.search_scrip("TCS")
        self.assertIn(b'"stext":"TCS"', self.requests[0].data)
        with self.assertRaises(ValueError):
            self.client.quote("NSE", "TCS-EQ")

    def test_no_order_submission(self):
        with self.assertRaises(ProfitmartError):
            self.client._post("PlaceOrder", {"uid": "DEMO"})
        ticket = validate_order_preview("TCS-EQ", "BUY", 1)
        self.assertEqual(ticket["execution"], "DISABLED")
        self.assertEqual(len(self.requests), 0)

    def test_fail_closed(self):
        with self.assertRaises(ValueError):
            ProfitmartConfig("http://api.example.com", "DEMO", "secret")
        with self.assertRaises(ValueError):
            validate_order_preview("TCS-EQ", "SELL", 0)
        with self.assertRaises(ValueError):
            self.client.quote("NSE", "1&x=secret")


if __name__ == "__main__":
    unittest.main()
