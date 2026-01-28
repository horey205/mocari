import sys
import os
import requests
import datetime
import urllib3
import ssl
import html
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

# Windows terminal encoding fix
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# -----------------------------------------------------------------------------
# 설정 / Configuration
# -----------------------------------------------------------------------------
# 공백 제거 (.strip()) 추가
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

# 신구대학교 API URL
API_URL = "https://www.shingu.ac.kr/ajaxf/FR_BST_SVC/BistroCarteInfo.do"
MENU_ID = "1630"

# 식당 정보
BISTROS = [
    {"name": "교직원식당", "seq": "6", "icon": "🏫"},
    {"name": "학생식당(미래창의관)", "seq": "5", "icon": "🎓"}
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
def get_kst_now():
    """한국 시간(KST) 현재 시간 반환"""
    return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

def send_telegram_message(message):
    """텔레그램 메시지 전송"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Warn] 텔레그램 토큰이 없어 메시지를 출력만 합니다.")
        print("---------------------------------------------------")
        try:
            print(message)
        except UnicodeEncodeError:
            print(message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
        print("---------------------------------------------------")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
        # 'parse_mode': 'HTML'  <-- 에러 방지를 위해 제거
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("텔레그램 메시지 전송 성공")
    except Exception as e:
        print(f"텔레그램 메시지 전송 실패: {e}")
        # 진짜 에러 원인 출력 (중요)
        if 'response' in locals():
            print(f"응답 내용: {response.text}")
        
        # GitHub Actions에서 실패로 표시되도록 에러 코드 반환
        sys.exit(1)

def get_menu_data(seq):
    """API를 통해 특정 식당의 이번 주 식단 데이터를 가져옴"""
    # KST 기준 날짜 계산
    today = get_kst_now().date()
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
    found_any = False
    
    for i in range(1, 7):
        nm_key = f'CARTE{i}_NM'
        cont_key = f'CARTE{i}_CONT'
        
        title = (menu_item.get(nm_key) or '').strip()
        content = (menu_item.get(cont_key) or '').strip()
        
        if title:
            found_any = True
            # HTML 특수문자 이스케이프 (텔레그램 API 오류 방지)
            safe_title = html.escape(title)
            safe_content = html.escape(content)
            
            # HTML 태그 제거 및 텍스트만 사용
            message_lines.append(f"🔸 {title}")
            if content:
                message_lines.append(content)
            message_lines.append("")
            
    if not found_any:
        return "🍽 등록된 메뉴가 없습니다."
        
    return "\n".join(message_lines)

def main():
    print("학교 식단 크롤러 시작")
    
    kst_now = get_kst_now()
    today_key = kst_now.strftime("%Y%m%d")
    display_date = kst_now.strftime("%Y년 %m월 %d일 (%a)")
    
    final_message = f"🍱 신구대학교 오늘의 학식\n{display_date}\n\n"

    for bistro in BISTROS:
        bistro_name = bistro['name']
        bistro_seq = bistro['seq']
        bistro_icon = bistro['icon']
        
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
            else:
                menu_content = "❌ 오늘은 운영하지 않거나 식단 데이터가 없습니다."
        
        final_message += f"{bistro_icon} {bistro_name}\n"
        final_message += f"{menu_content}\n"
        final_message += "━━━━━━━━━━━━━━━\n\n"

    send_telegram_message(final_message.strip())

if __name__ == "__main__":
    main()

