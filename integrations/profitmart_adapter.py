"""Server-side, read-only Profitmart Noren API adapter for independent AMI.
No Tradetron integration. No credentials are ever embedded in the Android APK.
Configure only in a trusted server environment and follow broker API approval rules.
"""
from dataclasses import dataclass
import json
import os
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_ALLOWED = {
    "UserDetails", "SearchScrip", "GetQuotes", "OrderBook", "Holdings"
}
_EXCHANGES = {"NSE", "BSE", "NFO", "BFO", "MCX", "CDS", "BCD", "NCX", "NIE"}


class ProfitmartError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProfitmartConfig:
    api_base: str
    client_code: str
    access_token: str

    def __post_init__(self):
        u = urlparse(self.api_base)
        if u.scheme != "https" or not u.hostname or u.username or u.password or u.query or u.fragment:
            raise ValueError("Broker API base must be a valid HTTPS URL without credentials")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", self.client_code):
            raise ValueError("Invalid client code")
        if not self.access_token or any(c in self.access_token for c in "\r\n"):
            raise ValueError("Invalid or missing access token")

    @classmethod
    def from_environment(cls):
        # Leave base unset until broker confirms the correct customer API endpoint.
        values = [os.environ.get(k, "") for k in (
            "PROFITMART_API_BASE", "PROFITMART_CLIENT_CODE", "PROFITMART_ACCESS_TOKEN"
        )]
        if not all(values):
            raise ProfitmartError("Not connected: official API base, client code and bearer token are required")
        return cls(*values)


class ProfitmartClient:
    """Use on a private backend only. This interface cannot place/cancel orders."""

    def __init__(self, config: ProfitmartConfig, transport=None):
        self.config = config
        self._transport = transport or self._network

    @staticmethod
    def _network(req):
        # No HTTP redirect permitted (would otherwise risk disclosing the bearer token).
        from urllib.request import build_opener, HTTPRedirectHandler
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise ProfitmartError("Unexpected broker API redirect")
        with build_opener(NoRedirect).open(req, timeout=12) as resp:
            return resp.read(1_000_000)

    def _post(self, endpoint, body):
        if endpoint not in _ALLOWED:
            raise ProfitmartError("Unsupported or write-capable API operation")
        url = self.config.api_base.rstrip("/") + "/NorenWClientAPI/" + endpoint
        raw = ("jData=" + json.dumps(body, separators=(",", ":"))).encode("utf-8")
        req = Request(url, data=raw, headers={
            "Content-Type": "text/plain",
            "Authorization": "Bearer " + self.config.access_token,
            "Accept": "application/json",
        }, method="POST")
        try:
            output = self._transport(req)
            result = json.loads(output)
        except (ValueError, TypeError) as e:
            raise ProfitmartError("Invalid broker response") from e
        except ProfitmartError:
            raise
        except Exception as e:
            # Don't include request, bearer token or broker server error internals.
            raise ProfitmartError("Broker request failed or session expired") from e
        if isinstance(result, dict) and result.get("stat") == "Not_Ok":
            raise ProfitmartError("Broker rejected request: check connection or permissions")
        return result

    def user_details(self):
        return self._post("UserDetails", {"uid": self.config.client_code})

    def search_scrip(self, text, exchange="NSE"):
        if not isinstance(text, str) or not re.fullmatch(r"[A-Za-z0-9&._ -]{1,60}", text):
            raise ValueError("Invalid symbol search")
        if exchange not in _EXCHANGES:
            raise ValueError("Unsupported exchange")
        return self._post("SearchScrip", {
            "uid": self.config.client_code, "stext": text, "exch": exchange
        })

    def quote(self, exchange, instrument_token):
        if exchange not in _EXCHANGES:
            raise ValueError("Unsupported exchange")
        if not re.fullmatch(r"[0-9]{1,24}", str(instrument_token)):
            raise ValueError("Quote requires a valid exchange instrument token, not a trading symbol")
        data = self._post("GetQuotes", {
            "uid": self.config.client_code,
            "exch": exchange, "token": str(instrument_token),
        })
        if not isinstance(data, dict) or data.get("stat") != "Ok" or data.get("lp") is None:
            raise ProfitmartError("No verified market price returned")
        return {
            "exchange": data.get("exch", exchange),
            "token": data.get("token", str(instrument_token)),
            "symbol": data.get("tsym"),
            "ltp": data["lp"],  # Preserve broker-provided value; no simulated quotes.
            "last_trade_time": data.get("ltt"),
            "source": "Profitmart official API",
        }

    def order_book(self):
        return self._post("OrderBook", {"uid": self.config.client_code})

    def holdings(self, account_id, product="C"):
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", account_id):
            raise ValueError("Invalid account ID")
        if product not in {"C", "I", "M"}:
            raise ValueError("Unsupported holdings product")
        return self._post("Holdings", {
            "uid": self.config.client_code, "actid": account_id, "prd": product
        })


def validate_order_preview(symbol, side, quantity, exchange="NSE"):
    """Validate UI ticket locally; *never* submit orders in this module."""
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Z0-9&._-]{1,36}", symbol):
        raise ValueError("Invalid trading symbol")
    if side not in {"BUY", "SELL"} or exchange not in _EXCHANGES:
        raise ValueError("Invalid side or exchange")
    if type(quantity) is not int or not (1 <= quantity <= 100000):
        raise ValueError("Quantity must be a positive integer")
    return {
        "symbol": symbol, "side": side, "quantity": quantity,
        "exchange": exchange, "execution": "DISABLED",
        "reason": "Broker authorization, market data and explicit trade confirmation required"
    }
