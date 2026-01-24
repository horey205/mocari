from bs4 import BeautifulSoup

def analyze_html():
    with open("c:/AI_Class/학교식단/shingu_sample.html", "r", encoding="utf-8") as f:
        html = f.read()
            
    soup = BeautifulSoup(html, 'html.parser')
    
    print("--- Title ---")
    print(soup.title.string if soup.title else "No Title")
    
    print("\n--- Tables ---")
    tables = soup.find_all('table')
    for i, table in enumerate(tables):
        print(f"\n[Table {i}] Classes: {table.get('class')}")
        # 헤더 출력
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        print(f"Headers: {headers}")
        # 첫 3행만 출력
        rows = table.find_all('tr')
        for ridx, row in enumerate(rows[:5]): 
            cols = [td.get_text(strip=True) for td in row.find_all('td')]
            if cols:
                print(f"Row {ridx}: {cols}")
                
    print("\n--- Possible Menu Containers (div with 'menu' or 'food') ---")
    divs = soup.find_all('div', class_=lambda x: x and ('menu' in x or 'food' in x))
    for div in divs:
         print(f"Div Class: {div.get('class')}")
         print(div.get_text(strip=True)[:100])

if __name__ == "__main__":
    analyze_html()
