from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from getpass import getpass
import re
from openpyxl import Workbook

from Application import Application
from ApplicationGroup import ApplicationGroup

LOGIN_URL = 'https://mit.s.dk/studiebolig/login/'
APPLICATION_URLS = []
APPLICATIONS = []

options = Options()
options.add_argument('--headless')

driver = webdriver.Firefox(options=options)
driver.get(LOGIN_URL)

while True:
    try:
        driver.find_element(By.ID, 'id_username').send_keys(input('Username: '))
        driver.find_element(By.ID, 'id_password').send_keys(getpass())
        driver.find_element(By.ID, 'id_login').click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.group-toggle-link')))
        print("Login successful!")
        
        break
    except KeyboardInterrupt:
        driver.close()
        break
    except:
        print("Wrong login credentials, try again..")

WebDriverWait(driver, 20).until_not(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Opdaterer ...")]')))
driver.find_element(By.CSS_SELECTOR, 'a.group-toggle-link').click()

moreApplications = True
print("Retrieving all applications...")
while moreApplications:
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Vis flere ejendomme")]')))
        WebDriverWait(driver, 20).until_not(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Opdaterer ...")]')))
        driver.find_element(By.XPATH, '//*[contains(text(), "Vis flere ejendomme")]').click()
    except:
        moreApplications = False
        print("All applications retrieved!")

for item in driver.find_elements(By.CLASS_NAME, 'list-group-item'):
    APPLICATION_URLS.append(item.get_attribute('href'))

print('Processing applications...')
for url in APPLICATION_URLS:
    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'group-toggle-link')))
    name = driver.find_element(By.TAG_NAME, 'h1').get_attribute('innerText')
    print('Processing application ' + name)

    i = 0
    for t in driver.find_elements(By.CLASS_NAME, 'group-toggle-link'):
        tempApplications = []

        rooms = int(re.search("#collapse-(?P<r>\d)", t.get_attribute('href')).group('r'))

        areapriceString = t.find_element(By.TAG_NAME, 'span').find_element(By.TAG_NAME, 'span').find_element(By.TAG_NAME, 'span').get_attribute('innerText')
        areaAndprices = re.search("(?P<a1>\d*)-(?P<a2>\d*).*, (?P<p1>\d*)-(?P<p2>\d*) kr.", areapriceString)

        prices = (int(areaAndprices.group('p1')), int(areaAndprices.group('p2')))

        areas = (int(areaAndprices.group('a1')), int(areaAndprices.group('a2')))

        tbody = driver.find_elements(By.TAG_NAME, 'tbody')[i]
        for c in tbody.find_elements(By.TAG_NAME, 'tr'):
            cc = c.find_elements(By.TAG_NAME, 'td')

            
            addr = cc[0].find_element(By.TAG_NAME, 'a').get_attribute('innerText')

            area = int(re.search(" (?P<a>\d*) m", cc[1].get_attribute('innerText')).group('a'))

            # Pessimistic estimation of price, according to highest price / biggest area
            estPrice = (prices[1] / areas[1]) * area
            if (area == areas[0]):
                estPrice = prices[0]

            rank = ""
            try:
                rankString = cc[2].find_element(By.TAG_NAME, 'a').find_element(By.CLASS_NAME, 'waiting-list-category').get_attribute('innerText')
                rank = re.search("\w", rankString).group(0)
            except:
                rank = "Z?"

            try:
                cc[3].find_element(By.TAG_NAME, 'p')    # Will not exist if button is 'Sign up for this tenancy' (aka you are not signed up)
                application = Application(name=name, rank=rank, rooms=rooms, grossArea=area, estPrice=estPrice, addr=addr, url=url)
                tempApplications.append(application)
            except:
                pass
        
        if (len(tempApplications) > 0):
            topApplication = sorted(tempApplications, key=lambda a: (a.rank, a.estPrice))[0]
            filteredList = list(filter(lambda a: a.rank == topApplication.rank, tempApplications))
            amount = len(filteredList)

            appGroup = ApplicationGroup(app=topApplication, am=amount)
            APPLICATIONS.append(appGroup)

        i += 1

print('All applications processed!')

sortedApps = sorted(APPLICATIONS, key=lambda a: (a.rank, -a.amount))

filename = "applications.xlsx"
workbook = Workbook()
sheet = workbook.active

it = 1
for a in sortedApps:
    sheet["A"+str(it)] = a.rank
    sheet["B"+str(it)] = str(a.amount)
    sheet["C"+str(it)] = a.name
    sheet["D"+str(it)] = str(a.rooms)
    sheet["E"+str(it)] = str(a.grossArea)
    sheet["F"+str(it)] = str(a.estPrice)
    sheet["G"+str(it)] = a.addr
    sheet["H"+str(it)] = a.url

    it += 1

workbook.save(filename=filename)
print('Result: see applications.xlsx')

driver.close()