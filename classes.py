from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import sys
import time
from bs4 import BeautifulSoup
from win10toast import ToastNotifier
from datetime import datetime, timedelta

now = datetime.now()
date = now.strftime('%d')
month = now.strftime('%m')
year = now.strftime('%Y')
str_now = now.strftime('%H:%M:%S')
hour_and_minute = datetime.strptime(str_now, '%H:%M:%S')

period_passed = []

def nearest(period_time):
    splitted_period = str(period_time).split(' ')
    if datetime.strptime(splitted_period[1], '%H:%M:%S') > hour_and_minute:
        return period_time - hour_and_minute
    else:
        period_passed.append('passed')
        return timedelta.max

PERIOD_TIMES = [datetime(int(year), int(month), int(date), hour=8, minute=45, second=0),datetime(int(year),int(month), int(date), hour=8,minute=57,second=0), datetime(int(year),int(month), int(date),hour=9,minute=42,second=0), datetime(int(year),int(month), int(date),hour=10,minute=27,second=0), datetime(int(year),int(month), int(date),hour=11,minute=40,second=0), datetime(int(year),int(month), int(date),hour=12,minute=25,second=0), datetime(int(year),int(month), int(date), hour=13,minute=57,second=0), datetime(int(year),int(month), int(date), hour=14, minute=42, second=0)]

#username and password to login into compass
username = sys.argv[1]
password = sys.argv[2]

#Firefox driver
driver_options = Options()
driver_options.add_argument('--headless')
driver = webdriver.Firefox(options=driver_options)

#Getting the compass website
driver.get('https://mhs-vic.compass.education/login.aspx?sessionstate=disabled')

#Logging into compass
compass_username = driver.find_element_by_id('username')
compass_username.send_keys(username)
compass_password = driver.find_element_by_id('password')
compass_password.send_keys(password)
login_button = driver.find_element_by_id('button1')
time.sleep(1)
login_button.click()

#Getting the current page
element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ext-cal-day-col'))
WebDriverWait(driver, 10).until(element_present)
page = driver.page_source

#Making the current page into beautifulsoup
soup = BeautifulSoup(page, features='html5lib')

#Searching the page for the timetable
timetable = soup.find('td', attrs={'class': 'ext-cal-day-col'})
classes = []
for period in timetable.findAll('span', attrs={'class': 'ext-evt-bd'}):
    classes.append(period.text)

class_dict = {}
#splitting at the semicolon so the computer will alert the user just before the bell rings
for section in classes:
    time_and_class_split = section.split(':')
    if len(time_and_class_split[0]) == 1:
        class_dict['0' + time_and_class_split[0] + ":" + time_and_class_split[1]] = time_and_class_split[2]
    else:
        class_dict[time_and_class_split[0] + ":" + time_and_class_split[1]] = time_and_class_split[2]

#Alerting the user with notifications
toast = ToastNotifier()
closest_period_time_format = min(PERIOD_TIMES, key=nearest)
closest_period = str(closest_period_time_format.strftime('%H:%M'))
#Exiting if all periods have been passed i.e school is over for the day
if len(period_passed) == 8:
    exit()
toast.show_toast(closest_period, class_dict[closest_period], duration=5, icon_path='strawberry.ico')
