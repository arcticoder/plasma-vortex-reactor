#!/usr/bin/env python3
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def eprint(*a, **k):
    print(*a, **k, file=sys.stderr)

TOKEN = os.environ.get('ZEN_TOKEN') or os.environ.get('TOKEN')
if not TOKEN:
    eprint('ERROR: TOKEN environment variable not set (ZEN_TOKEN or TOKEN)')
    sys.exit(2)

BASE = 'https://zenodo.org'
ACCOUNT_URL = BASE + '/api/account'
DEPOSIT_URL = BASE + '/api/deposit/depositions'
headers = {'Authorization': 'Bearer ' + TOKEN}

# Account check
req = Request(ACCOUNT_URL, headers=headers)
try:
    with urlopen(req, timeout=15) as r:
        data = r.read().decode('utf-8')
        print('ACCOUNT_OK')
        open('tmp/zen_account.json','w').write(data)
except HTTPError as e:
    body = e.read().decode('utf-8', 'replace') if e.fp else ''
    open('tmp/zen_account.json','w').write(body)
    eprint('ACCOUNT_HTTP_ERROR', e.code)
    eprint(body)
    sys.exit(3)
except URLError as e:
    eprint('ACCOUNT_URL_ERROR', e)
    sys.exit(4)

# Create deposition
meta = {"metadata": {
    "title": "Phase 3 Stability (auto)",
    "upload_type": "publication",
    "publication_type": "report",
    "description": "Auto-uploaded Phase 3 Stability paper.",
    "creators": [{"name": "Repository Owner"}],
    "access_right": "open"
}}

req = Request(DEPOSIT_URL, data=json.dumps(meta).encode('utf-8'), headers={**headers, 'Content-Type':'application/json'}, method='POST')
try:
    with urlopen(req, timeout=15) as r:
        data = r.read().decode('utf-8')
        open('tmp/zen_create.json','w').write(data)
        j = json.loads(data)
        depid = str(j.get('id',''))
        if not depid:
            eprint('NO_DEPOSITION_ID_IN_RESPONSE')
            sys.exit(5)
        open('tmp/zen_depid.txt','w').write(depid)
        print('DEPOSITION_CREATED', depid)
except HTTPError as e:
    body = e.read().decode('utf-8', 'replace') if e.fp else ''
    open('tmp/zen_create.json','w').write(body)
    eprint('CREATE_HTTP_ERROR', e.code)
    eprint(body)
    sys.exit(6)
except URLError as e:
    eprint('CREATE_URL_ERROR', e)
    sys.exit(7)

print('OK')
