# 학교 급식 알리미 (School Lunch Notifier) for 신구대학교

매일 평일 오전 11시 30분에 신구대학교(미래창의관 학생식당) 오늘의 메뉴를 텔레그램으로 보내주는 자동화 봇입니다.

## 🚀 기능
- **매일 자동 실행**: GitHub Actions를 통해 평일 오전 11:30에 자동 실행됩니다.
- **식단 크롤링**: 신구대학교 홈페이지 API를 사용하여 정확한 메뉴 정보를 가져옵니다.
- **텔레그램 전송**: 오늘의 메뉴를 보기 좋게 정리하여 내 텔레그램으로 보냅니다.

## 🛠️ 설치 및 설정 방법

### 1단계: GitHub에 코드 올리기
이 폴더(`c:/AI_Class/학교식단`)의 모든 파일을 자신의 GitHub 저장소(Repository)에 업로드합니다.

### 2단계: GitHub 설정 (Secret 추가)
1. GitHub 저장소 페이지 상단의 **Settings** 탭 클릭.
2. 왼쪽 메뉴에서 **Secrets and variables** > **Actions** 클릭.
3. **New repository secret** 버튼을 눌러 아래 두 가지 정보를 정확히 입력합니다.

| Name | Secret (값) | 설명 |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `8212219580:AAHHRhpSSfyX9uGY3UV0RQAyP9_Az0KFiZs` | 내 봇의 비밀 키 |
| `TELEGRAM_CHAT_ID` | `7203474705` | 내 봇 채팅방 ID |

> **주의**: 값 앞뒤에 공백이 들어가지 않도록 주의해주세요.

### 3단계: 확인하기
- 설정이 끝나면 **Actions** 탭에서 `Daily School Lunch Notification` 워크플로우를 찾아 **Run workflow** 버튼을 눌러보세요.
- 잠시 후 (약 1분 이내) 텔레그램으로 오늘의 메뉴가 도착하면 성공입니다! 🎉
- 이후부터는 매주 평일 오전 11시 30분에 자동으로 배달됩니다.

## 📝 파일 구성
- `menu_crawler.py`: 식단 데이터를 가져오고 메시지를 보내는 핵심 코드
- `.github/workflows/daily_menu.yml`: 자동 실행 스케줄 설정 파일 (Cron)
- `requirements.txt`: 필요한 라이브러리 목록
