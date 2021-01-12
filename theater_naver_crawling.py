#출저 : https://teamlab.github.io/jekyllDecent/blog/crawling%20with%20python/Selenium%EC%9C%BC%EB%A1%9C-%EB%84%A4%EC%9D%B4%EB%B2%84-%EC%97%B0%EA%B7%B9-%EB%8D%B0%EC%9D%B4%ED%84%B0-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%98%EA%B8%B0-with-Python


from urllib.parse import quote_plus  # 한글 텍스트를 퍼센트 인코딩으로 변환
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # 해당 태그를 기다림
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # 태그가 없는 예외 처리
import time
import pandas as pd

_input = input('''-월--일, -월, 이번주, 이번주말 중 선택하여 입력해주세요.
                                 (-은 숫자 입력, 이번년도만 가능) : ''')
user_input = quote_plus(_input)

url = f'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&query={user_input}%20%EC%97%B0%EA%B7%B9%20%EA%B3%B5%EC%97%B0'
chromedriver = 'C:\python\patent\chromedriver.exe'

options = webdriver.ChromeOptions()
# options.add_argument('headless')  # 웹 브라우저를 띄우지 않는 headlss chrome 옵션 적용
options.add_argument('disable-gpu')  # GPU 사용 안함
options.add_argument('lang=ko_KR')  # 언어 설정
driver = webdriver.Chrome(chromedriver, options=options)

driver.get(url)

try:
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'list_title')))
    theater_list = []
    pageNum = int(driver.find_element_by_class_name('_totalCount').text)
    count = 0

    for i in range(1, pageNum):
        theater_data = driver.find_elements_by_class_name('list_title')
        img_data = driver.find_elements_by_class_name('list_thumb')
        # print(theater_data)
        for k in theater_data:
            theater_list.append(k.text.split('\n'))

        for j in img_data:  # 이미지 크롤링
            count += 1
            j.screenshot(f'img/{count}.png')

        driver.find_element_by_xpath("//a[@class='btn_page_next _btnNext on']").click()
        time.sleep(2)


except TimeoutException:
    print('해당 페이지에 연극 정보가 존재하지 않습니다.')

finally:
    driver.quit()

for i in range(len(theater_list)):
    theater_list[i].append(theater_list[i][1].split('~')[0]) #1번째 인덱스(날짜)를 잘라서 잘라진 1번째 날짜
    theater_list[i].append(theater_list[i][1].split('~')[1]) #1번째 인덱스(날짜)를 잘라서 잘라진 2번째 날짜

for i in range(len(theater_list)):
    if theater_list[i][4] == '오픈런':
        theater_list[i][4] = '50.01.01.'
        theater_list[i].append('True')
    else:
        theater_list[i].append('False')




import pandas as pd
theater_df = pd.DataFrame(theater_list,columns=['연극명', '기간', '장소', '개막일', '폐막일', '오픈런'])
theater_df.index = theater_df.index+1

theater_df['개막일'] = pd.to_datetime(theater_df['개막일'], format='%y.%m.%d.')
theater_df['폐막일'] = pd.to_datetime(theater_df['폐막일'], format='%y.%m.%d.')

theater_df.to_csv(f'theater_{_input}_df.csv',mode='w',encoding='CP949',header=True,index=True)
print(theater_df)