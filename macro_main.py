import multiprocessing
import json
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def do_reserve(setting):
    options = Options()
    options.add_experimental_option('detach', True) # 브라우저 바로 닫힘 방지
    options.add_experimental_option("excludeSwitches", ['enable-logging']) # 불필요한 메시지 제거
    
    id = setting['id']
    passwd = setting['passwd']
    day = setting['day']
    week = setting['week']
    start_time_list = setting['start_time']
    hour = setting['hour']
    book_time_h = setting['book_time_h']
    book_time_m = setting['book_time_m']
    ground_list = setting['ground']

    if day == '월' or day == '월요일' or day.lower() == 'mon' or day.lower() == 'monday':
        day_int = 2
    elif day == '화' or day == '화요일' or day.lower() == 'tue' or day.lower() == 'tuesday':
        day_int = 3
    elif day == '수' or day == '수요일' or day.lower() == 'wed' or day.lower() == 'wednesday':
        day_int = 4
    elif day == '목' or day == '목요일' or day.lower() == 'thu' or day.lower() == 'thursday':
        day_int = 5
    elif day == '금' or day == '금요일' or day.lower() == 'fri' or day.lower() == 'friday':
        day_int = 6
    elif day == '토' or day == '토요일' or day.lower() == 'sat' or day.lower() == 'saturday':
        day_int = 7
    elif day == '일' or day == '일요일' or day.lower() == 'sun' or day.lower() == 'sunday':
        day_int = 1
    else:
        day_int = 1
    
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    # 보통 크롬드라이버를 맞춰서 다운 받은 뒤 실행시킨다 하지만 이렇게하면 계속 버전에 맞춰 다운을 받아줘야함
    # 이때 사용할 수있는게 webdriver manager이다
    # 버전업이 되더라도 진행된다

    ## login
    driver.get('https://www.gimhae.go.kr/yes/05566/05580/05582.web')

    ## init login page loading wait 20 minutes

    try:
        WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="body_content"]/div/div/div/div/h4[2]/a')))
    except TimeoutException:
        print('cannot find login page')
    driver.find_element(By.XPATH, '//*[@id="body_content"]/div/div/div/div/h4[2]/a').click()
    driver.find_element(By.XPATH, '//*[@id="groupId"]').send_keys(id)
    driver.find_element(By.XPATH, '//*[@id="grouppassword"]').send_keys(passwd)
    driver.find_element(By.XPATH, '//*[@id="grouppassword"]').send_keys(Keys.ENTER)

    ## time checker
    # time_stop = datetime.datetime.now()
    # while(not(time_stop.hour == book_time_h and time_stop.minute == book_time_m)):  
    #     time_stop = datetime.datetime.now()

    ## ground page init
    
    for ground_name in ground_list:
        if ground_name == '임호':
            driver.get('https://www.gimhae.go.kr/yes/05561/05630/05681.web')
        elif ground_name == '삼계':
            driver.get('https://www.gimhae.go.kr/yes/05561/05630/05887.web')
        elif ground_name == '장유':
            driver.get('https://www.gimhae.go.kr/yes/05561/05630/05679.web')
        elif ground_name == '안동':
            driver.get('https://www.gimhae.go.kr/yes/05561/05630/05678.web')

        try:
            
            WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="body_content"]/div/div[3]/ul/li[1]')))
            driver.find_element(By.XPATH, '//*[@id="body_content"]/div/div[3]/ul/li[1]').click()
            WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app-lease"]/div[1]/div/div/div[2]/table/tbody/tr[{}]/td[{}]/a/i'.format(week, day_int))))
            day_element = driver.find_element(By.XPATH, '//*[@id="app-lease"]/div[1]/div/div/div[2]/table/tbody/tr[{}]/td[{}]/a/i'.format(week, day_int))
            if day_element.text == '예약불가':
                print('ID : {}, Ground : {}, Week : {}, day : {} is already Full.'.format(id, ground_name, week, day))
                continue
                        
            driver.find_element(By.XPATH, '//*[@id="app-lease"]/div[1]/div/div/div[2]/table/tbody/tr[{}]/td[{}]/a/i'.format(week, day_int)).click()
            
            WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app-lease"]/div[2]/form/div/ul/li[{}-8]/label'.format(start_time_list[0]))))
            flag_check = True
            for start_time in start_time_list:
                flag_check = True
                for click_idx in range(start_time, start_time+hour):
                    ## 하나라도 불가면 다른 시간 알아보기
                    if driver.find_element(By.XPATH, '//*[@id="app-lease"]/div[2]/form/div/ul/li[{}]/label/span[2]/i[2]/span'.format(click_idx-8)).text == '불가':
                        print('ID : {}, Ground : {}, Week : {}, day : {}, start_time : {} is already Full.'.format(id, ground_name, week, day, start_time))
                        flag_check = False
                        break
                    ## 불가가 없으면 통과
                if flag_check:
                    for click_idx in range(start_time, start_time+hour):
                        driver.find_element(By.XPATH, '//*[@id="app-lease"]/div[2]/form/div/ul/li[{}]/label'.format(click_idx-8)).click()
                    driver.find_element(By.XPATH, '//*[@id="app-lease"]/div[2]/form/div/div[2]/button[1]').click()
                    break
            if flag_check:
                WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="leaseSubscriberVO"]/div[2]/div/div/label/i')))
                driver.find_element(By.XPATH, '//*[@id="leaseSubscriberVO"]/div[2]/div/div/label/i').click()
                driver.find_element(By.XPATH, '//*[@id="numPerson"]').send_keys('40')
                driver.find_element(By.XPATH, '//*[@id="eventNm"]').send_keys('친선 축구 경기')
                driver.find_element(By.XPATH, '//*[@id="purpose"]').send_keys('친선 축구 경기')
                driver.find_element(By.XPATH, '//*[@id="leaseSubscriberVO"]/div[4]/div/div/label/i').click()
                driver.find_element(By.XPATH, '//*[@id="leaseSubscriberVO"]/div[5]/p/button').click()
                driver.switch_to.alert.accept()
            else:
                continue

        except TimeoutException:
            print("Loading takes too much time!")

def main():
    ## get setting info
    with open(r'./setting.json', 'r', encoding='UTF8') as f:
        jdata = json.load(f)
    setting_list = list()
    for key, value in jdata.items():
        if key == 'book_start':
            for time_k, time_v in value.items():
                if time_k == 'time_hour':
                    time_h = time_v
                if time_k == 'time_minute':
                    time_m = time_v

        if key == 'settings':
            setting_list = value
    
    for setting in setting_list:
        setting['book_time_h'] = time_h
        setting['book_time_m'] = time_m

    print('--- start_multiprocessing')
    print(len(setting_list))
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(len(setting_list))

    # 실행 함수, 넘겨줄 파라미터
    pool.map(do_reserve, setting_list)

    # 모든 프로세스 종료까지 기다림
    pool.close()
    pool.join()
    # multi end

if __name__ == '__main__':
    main()
