from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver # selenium
from selenium.webdriver.chrome.options import Options

def crawling():
    sections = {100: '정치',
                101: '경제', 
                102: '사회', 
                103: '생활문화',
                105: 'IT과학', 
                104: '세계', 
                }

    news_li = []
    for section_num, section_name in sections.items():
        url = f"https://news.naver.com/section/{section_num}" # url 설정 

        chrome_options = Options()
        # chrome_options.add_argument("--headless") # 창 안뜨게 하는 옵션
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        html = driver.page_source
        soup = bs(html, 'html.parser')
        articles = soup.select("div.sa_text")

        for article in articles:
            news = {}
            news["section"] = section_name
            news["title"] = article.select_one("strong.sa_text_strong").get_text()
            news["url"] = article.select_one("a.sa_text_title")["href"]
            news["press"] = article.select_one("div.sa_text_press").get_text() 

            response = driver.get(news["url"])
            html = driver.page_source
            soup = bs(html, 'html.parser')
            
            video = soup.select_one('div.vod_player_wrap') # 비디오 플레이어 영역이 있으면
            if video: # 비디오 플레이어 다음부터
                news["content"] = " ".join([a.strip() for a in video.next_siblings if isinstance(a,str)])
            else: # 아니면 텍스트 전체 
                news["content"] = soup.select_one('article#dic_area').get_text()

            news_li.append(news)
            
        driver.quit()

    news_df = pd.DataFrame(news_li)
    # news_df.to_csv("news_data.csv")
    
    return news_df