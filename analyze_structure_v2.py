from bs4 import BeautifulSoup

def extract_contents():
    with open("c:/AI_Class/학교식단/shingu_sample.html", "r", encoding="utf-8") as f:
        html = f.read()
            
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try finding the contents area
    content_div = soup.find(id="contents")
    if not content_div:
        content_div = soup.find(class_="contents")
    
    if content_div:
        print("Found contents div!")
        with open("c:/AI_Class/학교식단/shingu_contents.html", "w", encoding="utf-8") as f:
            f.write(str(content_div))
        
        # 텍스트 내용 미리보기
        text = content_div.get_text(separator='\n', strip=True)
        print("--- Text Preview ---")
        print(text[:500])
        
        # 테이블 찾기
        tables = content_div.find_all('table')
        print(f"\nFound {len(tables)} tables in contents.")
    else:
        print("Could not find div with id='contents' or class='contents'")
        # 레이아웃이 다를 수 있으니 container 등으로 시도
        container = soup.find(id="container")
        if container:
            print("Found container instead.")
            with open("c:/AI_Class/학교식단/shingu_contents.html", "w", encoding="utf-8") as f:
                f.write(str(container))

if __name__ == "__main__":
    extract_contents()
