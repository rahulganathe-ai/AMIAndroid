#!/usr/bin/env python3
"""Configure a stable, secret-backed Android release signature on the CI runner."""
import base64
import binascii
import os
from pathlib import Path

needed = ('AMI_KEYSTORE_BASE64','AMI_KEYSTORE_PASSWORD','AMI_KEY_ALIAS','AMI_KEY_PASSWORD')
missing = [name for name in needed if not os.environ.get(name)]
if missing:
    raise SystemExit('Release signing not configured. Configure GitHub Actions secrets: ' + ', '.join(missing))
try:
    raw = base64.b64decode(os.environ['AMI_KEYSTORE_BASE64'], validate=True)
except (binascii.Error, ValueError) as exc:
    raise SystemExit('AMI_KEYSTORE_BASE64 is not valid Base64') from exc
if len(raw) < 100:
    raise SystemExit('Signing keystore appears invalid (too small)')

root = Path(__file__).resolve().parents[1]
store_dir = Path(os.environ.get('RUNNER_TEMP', root / '.ci-private')).resolve()
store_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
store = store_dir / 'ami-release.jks'
fd = os.open(str(store), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'wb') as stream:
    stream.write(raw)

build = root / 'android/app/build.gradle'
content = build.read_text(encoding='utf-8')
if 'AMI_SIGNING_STORE_FILE' in content:
    raise SystemExit('Release signing already configured; refusing duplicate patch')
if 'android {' not in content:
    raise SystemExit('Unrecognized Android Gradle project')
block = """android {
    signingConfigs {
        release {
            storeFile file(System.getenv('AMI_SIGNING_STORE_FILE'))
            storePassword System.getenv('AMI_KEYSTORE_PASSWORD')
            keyAlias System.getenv('AMI_KEY_ALIAS')
            keyPassword System.getenv('AMI_KEY_PASSWORD')
        }
    }
    buildTypes {
        release {
            minifyEnabled false
            signingConfig signingConfigs.release
        }
    }
"""
build.write_text(content.replace('android {', block, 1), encoding='utf-8')
with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as env:
    env.write('AMI_SIGNING_STORE_FILE=' + str(store) + '\n')
print('Release configuration prepared using private, persistent keystore')
