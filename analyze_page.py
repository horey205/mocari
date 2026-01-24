import requests

url = "https://www.shingu.ac.kr/cms/FR_CON/index.do?MENU_ID=1630"
try:
    response = requests.get(url, verify=False) # SSL 인증서 무시 (학교 사이트 등에서 문제 되는 경우 방지)
    response.encoding = response.apparent_encoding # 인코딩 자동 감지
    
    with open("c:/AI_Class/학교식단/shingu_sample.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("HTML saved to shingu_sample.html")
except Exception as e:
    print(f"Error: {e}")
