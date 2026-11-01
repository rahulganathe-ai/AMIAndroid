# AMI – independent Profitmart API integration (read-only foundation)

AMI is independent from Tradetron. Tradetron redirect/login URL is **not** an AMI endpoint.

This folder provides a standalone **server-side Python adapter** to Profitmart's documented OAuth Bearer authenticated Noren API. It supports user details, symbol search, quote snapshots, order-book read, holdings read and order-ticket validation. It **cannot submit or cancel trades**. No fake prices. No credentials or tokens are checked into GitHub or baked into the Android app.

## Verified API contract

* POST `/NorenWClientAPI/UserDetails` – `jData={"uid":"..."}`
* POST `/NorenWClientAPI/SearchScrip` – `jData={"uid":"...","stext":"...","exch":"NSE"}`
* POST `/NorenWClientAPI/GetQuotes` – `jData={"uid":"...","exch":"NSE","token":"..."}`
* Bearer token header and `jData=...` body per Profitmart docs.

Sources: https://profitmax.profitmart.in/ApiDocs/ and
https://profitmax.profitmart.in/ApiDocs/docs/Login%20And%20User%20Details/User%20Details/
and https://profitmax.profitmart.in/ApiDocs/docs/Orders%20and%20Trades/Place%20Order/

## Setup on a PRIVATE backend only

The broker must approve AMI's own application/client ID, API secret, production host, login redirect and required market-data/order permissions. Configure these environment variables **only on your secure server**, not in the Android app, GitHub repository, chat, URL query or WebView local storage:

* `PROFITMART_API_BASE`: broker-confirmed HTTPS Noren API base. No assumed Tradetron URL.
* `PROFITMART_CLIENT_CODE`: your authorised client code.
* `PROFITMART_ACCESS_TOKEN`: OAuth bearer token for the active session, obtained via the *broker-approved* OAuth exchange.

Usage (server-side only): `from integrations.profitmart_adapter import ProfitmartClient, ProfitmartConfig` then `client=ProfitmartClient(ProfitmartConfig.from_environment())`, `client.search_scrip("TCS")`, `client.quote("NSE", instrument_token)`. Import from repo root.

To run offline tests: `python3 -m unittest discover -s integrations -p 'test_*.py' -v`

**Not completed**: Profitmart OAuth redirect/token exchange, secure server deployment and user sessions, live streaming WebSocket, symbol master refresh, client-to-server authenticated API, real Buy/Sell order routing and app E2E testing, signed Android Release APK. Until all are implemented and authorised, the Android UI must show **Not connected** and keep `Place order` disabled.

Production: enforce TLS, authenticated app sessions, strict server-side authorization per client, CSRF/CORS policy, rate limits, audit logs without secrets, proper token renewal and encrypted secrets management. Never expose a broker bearer token to an unauthenticated web API.
