import os
import requests
import datetime
import urllib3
import ssl
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

# 식당 정보
BISTROS = [
    {"name": "교직원식당", "seq": "6"}, # 1. 교직원식당부터
    {"name": "학생식당(미래창의관)", "seq": "5"} # 2. 학생식당
]

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# SSL Adapter (Legacy Support)
# -----------------------------------------------------------------------------
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
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("텔레그램 메시지 전송 성공")
    except Exception as e:
        print(f"텔레그램 메시지 전송 실패: {e}")

def get_menu_data(seq):
    """API를 통해 특정 식당의 이번 주 식단 데이터를 가져옴"""
    # 이번 주 월요일, 금요일 계산
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    friday = monday + datetime.timedelta(days=6)
    
    start_day_str = monday.strftime("%Y.%m.%d")
    end_day_str = friday.strftime("%Y.%m.%d")
    
    payload = {
        'MENU_ID': MENU_ID,
        'BISTRO_SEQ': seq,
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
        print(f"API 호출 실패 (SEQ {seq}): {e}")
        return None

def format_menu(menu_item):
    """메뉴 아이템을 보기 좋은 텍스트로 변환"""
    message_lines = []
    
    # 1~6 코너까지 있을 수 있음 (학생식당은 3개였지만, 교직원은 모름)
    # 일반적인 패턴인 CARTE1 ~ CARTE6 확인
    found_any = False
    
    for i in range(1, 7):
        nm_key = f'CARTE{i}_NM'
        cont_key = f'CARTE{i}_CONT'
        
        if menu_item.get(nm_key):
            found_any = True
            title = menu_item.get(nm_key, '').strip()
            content = menu_item.get(cont_key, '').strip()
            
            # 제목에 불필요한 태그/공백 제거
            message_lines.append(f"<b>🔸 {title}</b>")
            if content:
                message_lines.append(content)
            message_lines.append("") # 공백
            
    if not found_any:
        return "🍽 등록된 메뉴가 없습니다."
        
    return "\n".join(message_lines)

def main():
    print("학교 식단 크롤러 시작")
    
    today = datetime.date.today()
    today_key = today.strftime("%Y%m%d")
    display_date = today.strftime("%Y년 %m월 %d일 (%a)")
    
    final_message = f"🍱 <b>신구대학교 오늘의 학식</b>\n{display_date}\n\n"
    has_menu_today = False

    for bistro in BISTROS:
        bistro_name = bistro['name']
        bistro_seq = bistro['seq']
        
        print(f"[{bistro_name}] 데이터 가져오는 중...")
        json_data = get_menu_data(bistro_seq)
        
        menu_content = "🔒 운영 정보 없음"
        
        if json_data:
            items = []
            if isinstance(json_data, dict) and 'data' in json_data:
                items = json_data['data']
            elif isinstance(json_data, list):
                items = json_data
            
            # 오늘 메뉴 찾기
            todays_item = None
            for item in items:
                item_date = item.get('STD_DT')
                if not item_date:
                    ym = item.get('STD_YM', '').replace('.', '')
                    dd = item.get('STD_DD', '')
                    if ym and dd:
                        item_date = f"{ym}{dd}"
                
                if item_date == today_key:
                    todays_item = item
                    break
            
            if todays_item:
                menu_content = format_menu(todays_item)
                if "등록된 메뉴가 없습니다" not in menu_content:
                    has_menu_today = True
            else:
                menu_content = "❌ 오늘은 운영하지 않거나 식단 데이터가 없습니다."
        
        # 메시지 합치기
        # 아이콘 추가: 교직원(🏫), 학생(🎓)
        icon = "🏫" if "교직원" in bistro_name else "🎓"
        final_message += f"{icon} <b>{bistro_name}</b>\n"
        final_message += f"{menu_content}\n"
        final_message += "-" * 15 + "\n\n"

    # 메시지 전송 (메뉴가 하나라도 있거나, 아예 없어도 안내는 전송)
    # 주말 등 모두 닫았을 때는 "❌ 오늘은 운영하지 않습니다" 하나만 보내는 게 깔끔할 수 있음
    # 하지만 사용자 요청 구성을 유지.
    send_telegram_message(final_message.strip())

if __name__ == "__main__":
    main()
