import requests
import datetime
import urllib3
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl_.create_urllib3_context(ciphers='DEFAULT:@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

def test_api():
    url = "https://www.shingu.ac.kr/ajaxf/FR_BST_SVC/BistroCarteInfo.do"
    
    # Calculate Monday and Friday of this week
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    friday = monday + datetime.timedelta(days=4)
    
    start_day_str = monday.strftime("%Y.%m.%d")
    end_day_str = friday.strftime("%Y.%m.%d")
    
    print(f"Requesting menu for {start_day_str} ~ {end_day_str}")

    data = {
        'MENU_ID': '1630',
        'BISTRO_SEQ': '5',  # 미래창의관
        'START_DAY': start_day_str,
        'END_DAY': end_day_str
    }
    
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    
    try:
        response = session.post(url, data=data, verify=False)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"Received JSON with {len(json_data)} items")
                for item in json_data:
                    date = f"{item.get('STD_YM')}.{item.get('STD_DD')}"
                    menu = item.get('CARTE1_NM', 'No Menu') or item.get('CARTE2_NM')
                    print(f"[{date}] {menu}")
            except Exception as e:
                print(f"JSON Parsing Error: {e}")
                print(response.text[:500])
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_api()
