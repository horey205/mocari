import os
import requests
import datetime
import urllib3
import ssl
import sys
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

# -----------------------------------------------------------------------------
# 설정 / Configuration
# -----------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 신구대학교 API URL
API_URL = "https://www.shingu.ac.kr/ajaxf/FR_BST_SVC/BistroCarteInfo.do"
MENU_ID = "1630"
BISTRO_SEQ = "5" # 5: 미래창의관 학생식당 (기본값)

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# SSL Adapter (Legacy Support)
# -----------------------------------------------------------------------------
class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        # 학교 사이트 등의 구형 SSL 호환성을 위해 보안 레벨 낮춤
        ctx = ssl_.create_urllib3_context(ciphers='DEFAULT:@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

# -----------------------------------------------------------------------------
# Main Functions
# -----------------------------------------------------------------------------
def send_telegram_message(message):
    """텔레그램 메시지 전송"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Warn] 텔레그램 토큰이 없어 메시지를 출력만 합니다.")
        print("---------------------------------------------------")
        print(message)
        print("---------------------------------------------------")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML' # HTML 태그 사용 가능
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("텔레그램 메시지 전송 성공")
    except Exception as e:
        print(f"텔레그램 메시지 전송 실패: {e}")

def get_menu_data():
    """API를 통해 이번 주 식단 데이터를 가져옴"""
    # 이번 주 월요일, 금요일 계산
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    friday = monday + datetime.timedelta(days=6) # 넉넉하게 일요일까지 포함해도 됨
    
    start_day_str = monday.strftime("%Y.%m.%d")
    end_day_str = friday.strftime("%Y.%m.%d")
    
    print(f"식단 데이터 요청: {start_day_str} ~ {end_day_str}")

    payload = {
        'MENU_ID': MENU_ID,
        'BISTRO_SEQ': BISTRO_SEQ,
        'START_DAY': start_day_str,
        'END_DAY': end_day_str
    }
    
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    
    try:
        response = session.post(API_URL, data=payload, verify=False, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

def format_menu(menu_item):
    """메뉴 아이템을 보기 좋은 텍스트로 변환"""
    # 구조: CARTE1_NM (제목), CARTE1_CONT (내용)
    message_lines = []
    
    # 코너 1
    if menu_item.get('CARTE1_NM'):
        title = menu_item.get('CARTE1_NM', '').strip()
        content = menu_item.get('CARTE1_CONT', '').strip()
        message_lines.append(f"<b>[ {title} ]</b>")
        if content:
            message_lines.append(content)
        message_lines.append("") # 공백
        
    # 코너 2
    if menu_item.get('CARTE2_NM'):
        title = menu_item.get('CARTE2_NM', '').strip()
        content = menu_item.get('CARTE2_CONT', '').strip()
        message_lines.append(f"<b>[ {title} ]</b>")
        if content:
            message_lines.append(content)
        message_lines.append("")

    # 코너 3
    if menu_item.get('CARTE3_NM'):
        title = menu_item.get('CARTE3_NM', '').strip()
        content = menu_item.get('CARTE3_CONT', '').strip()
        message_lines.append(f"<b>[ {title} ]</b>")
        if content:
            message_lines.append(content)
            
    if not message_lines:
        return "등록된 메뉴가 없습니다."
        
    return "\n".join(message_lines)

def main():
    print("학교 식단 크롤러 시작")
    
    today = datetime.date.today()
    # today_str: API 데이터의 STD_DT 포맷과 맞춤 (YYYYMMDD)
    today_key = today.strftime("%Y%m%d")
    display_date = today.strftime("%Y년 %m월 %d일 (%a)")
    
    json_data = get_menu_data()
    
    if not json_data:
        send_telegram_message(f"[{display_date}] 식단 데이터를 가져오는데 실패했습니다.")
        return

    # JSON 구조 대응 (list 또는 dict)
    items = []
    if isinstance(json_data, dict) and 'data' in json_data:
        items = json_data['data']
    elif isinstance(json_data, list):
        items = json_data
    else:
        print(f"알 수 없는 JSON 구조: {type(json_data)}")
        send_telegram_message(f"[{display_date}] 식단 데이터 구조가 변경되었습니다.")
        return

    # 오늘 메뉴 찾기
    todays_menu = None
    for item in items:
        # STD_DT가 YYYYMMDD 형태라고 가정 (snippet 참고: "20260119")
        # 혹시 STD_YM과 STD_DD로 되어 있을 수도 있음.
        item_date = item.get('STD_DT')
        if not item_date:
            # 대체: YM.DD 형태 조합
            ym = item.get('STD_YM', '').replace('.', '')
            dd = item.get('STD_DD', '')
            if ym and dd:
                item_date = f"{ym}{dd}"
        
        if item_date == today_key:
            todays_menu = item
            break
    
    if todays_menu:
        menu_text = format_menu(todays_menu)
        final_msg = f"🍱 <b>신구대학교 오늘의 학식</b>\n{display_date}\n\n{menu_text}"
        send_telegram_message(final_msg)
    else:
        final_msg = f"🍱 <b>신구대학교 오늘의 학식</b>\n{display_date}\n\n오늘은 운영하는 식단이 없거나 데이터가 없습니다."
        send_telegram_message(final_msg)

if __name__ == "__main__":
    main()
