#!/usr/bin/env python3
"""Prepare archived Android source and add the independent-brand broker API screen."""
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "AMI_Cloud_Build_Android16_GitHub_MCP.zip"
ANDROID = ROOT / "android"
INDEX = ANDROID / "app/src/main/assets/index.html"

if not ARCHIVE.is_file():
    raise SystemExit("Missing packaged Android project archive")
if not (ANDROID / "settings.gradle").exists():
    with ZipFile(ARCHIVE) as z:
        for entry in z.infolist():
            if not entry.filename.startswith("android/"):
                continue
            target = (ROOT / entry.filename).resolve()
            if not target.is_relative_to(ROOT.resolve()):
                raise ValueError("Unsafe path in project archive")
            z.extract(entry, ROOT)

html = INDEX.read_text(encoding="utf-8")
if 'id="broker"' in html:
    print("Broker screen already included; no duplicate patch needed")
    raise SystemExit(0)

def replace_once(old: str, new: str):
    global html
    if html.count(old) != 1:
        raise ValueError(f"Unexpected insertion point: {old[:60]}")
    html = html.replace(old, new, 1)

replace_once(
    '<button data-page="settings"',
    '<button data-page="broker"><span class="ico">⇄</span> Connect Broker</button><button data-page="settings"',
)

broker_screen = """<section id="broker" class="view"><div class="hero"><div class="eyebrow">PRIVATE API CONNECTION</div><h2>Connect your broker, simply.</h2><p>Choose your broker below. AMI is an independent application. Official API authorisation will be available after a compatible secure connection is implemented.</p></div><div class="sectionhead"><h3>Broker API Connection</h3><span>Choose your provider</span></div><div class="configbox"><div class="setting"><label for="brokerProvider">Select broker</label><select id="brokerProvider" aria-label="Select your broker"><option value="profitmart">Profitmart Securities Private Limited</option><option value="other">Other broker (not configured)</option></select></div><button class="btn primary" id="saveBrokerPreference" type="button">Save broker selection</button><div class="smallnote" id="brokerPreferenceStatus" role="status" aria-live="polite"></div><div class="notice" id="brokerConnectionStatus" role="status"><b>API status: Not connected.</b><br>Live market streaming, funds, portfolio, MTM, order book, and Buy/Sell order routing are unavailable until the authorised broker API is securely connected. No trades can be placed from this screen.</div><p class="smallnote">Use your broker's official authorisation flow when available. Never paste passwords, API secrets or trading credentials into an unverified form.</p></div></section>
"""
replace_once('<section id="settings"', broker_screen + '<section id="settings"')
replace_once("settings:'Settings & MCP',forex:", "settings:'Settings & MCP',broker:'Broker API Connection',forex:")
replace_once("const defaults={endpoint:", "const defaults={brokerProvider:'profitmart',endpoint:")
replace_once(
    "byId('refresh').onclick=",
    "byId('brokerProvider').value=settings.brokerProvider==='other'?'other':'profitmart';\n"
    "byId('saveBrokerPreference').onclick=()=>{settings.brokerProvider=byId('brokerProvider').value;store();byId('brokerPreferenceStatus').textContent='Broker preference saved on this device. API is not connected; live orders remain disabled.'};\n"
    "byId('refresh').onclick=",
)
replace_once('</style></head>', """#broker .configbox{max-width:820px}#broker .setting label{font-size:18px;font-weight:800;color:var(--ink)}#broker .setting select{font-size:18px;font-weight:750;min-height:54px}#broker .btn{font-size:17px;font-weight:800;min-height:50px}#broker .notice{font-size:15px;line-height:1.7}#broker .hero p{font-size:16px}#broker .hero h2{font-size:28px}#broker .smallnote{font-size:13px}
</style></head>""")
assert html.count("Profitmart Securities Private Limited") == 1, "Broker name must only appear in selector"
INDEX.write_text(html, encoding="utf-8")
print("Prepared independent-brand broker selector (no live API connected)")
