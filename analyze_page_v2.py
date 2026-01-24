import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Method 1: Simple with Headers
url = "https://www.shingu.ac.kr/cms/FR_CON/index.do?MENU_ID=1630"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("Attempting Method 1 (Simple)...")
try:
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    print(f"Status Code: {response.status_code}")
    with open("c:/AI_Class/학교식단/shingu_sample.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Success with Method 1")
    exit()
except Exception as e:
    print(f"Method 1 failed: {e}")

# Method 2: Custom SSL Context (Legacy Support)
print("\nAttempting Method 2 (Legacy SSL)...")

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        # Allow older ciphers and lower security level
        ctx = ssl_.create_urllib3_context(ciphers='DEFAULT:@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

session = requests.Session()
session.mount('https://', LegacySSLAdapter())

try:
    response = session.get(url, headers=headers, verify=False, timeout=10)
    print(f"Status Code: {response.status_code}")
    with open("c:/AI_Class/학교식단/shingu_sample.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Success with Method 2")
except Exception as e:
    print(f"Method 2 failed: {e}")
