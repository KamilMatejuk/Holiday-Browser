import os
import time
import math
import datetime
import random
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, NewConnectionError
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

'''
TODO
1. Przepisać wpisywanie dat i filtrów na dodanie do linka
2. Zrobić konwertowanie walut (dolar i euro) - usunąć proxy z poza europy i stanów
'''


def check_booking(city, people, dates, out_file, counter=5):
    """
    Parameters
    ----------
    city : str
        City for which is searching
    people : dict
        Dictionary containing number of adults, children and age of each child
    dates : tuple
        Datetime objects of starting and ending date
    out_file : str
        Name of file to which results will be saved
        
    Check for offers on booking.com
    """

    if counter <= 0:
        return

    url = 'https://www.booking.com/'
    proxy = chooseProxy()
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server={proxy}')

    try:
        with webdriver.Chrome(executable_path='/home/kamil/Desktop/Wakacje/files/chromedriver', options=options) as browser:
            browser.get(url)
            WebDriverWait(browser, 45).until(
                EC.presence_of_element_located((By.XPATH, '/html/body'))
            )
            if 'ERR_' in browser.page_source:
                # couldnt load with given IP, proxy error
                print(f'Page couldn\'t load with IP {proxy}')
                check_booking(city, people, dates, out_file, counter=(counter - 1))
                return

            inputCity(browser, city[0])
            time.sleep(random.randint(1, 3))
            inputDateFrom(browser, dates[0])
            time.sleep(random.randint(1, 3))
            inputDateTo(browser, dates[1])
            time.sleep(random.randint(1, 3))
            inputPeople(browser, people)
            time.sleep(random.randint(1, 3))
            submit_btn_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[4]/div[2]/button'
            submit = waitForXPATH(browser, submit_btn_xpath)
            browser.execute_script("arguments[0].click();", submit)
            if not succesfulSearch(browser, city[0]):
                print('Couldn\'t find ' + city[0])
                return None
            time.sleep(random.randint(2, 5))
            links = getSearchLinks(browser)
    
    except WebDriverException as e:
        # no element on page
        print('IP ' + proxy)
        print(e)
        check_booking(city, people, dates, out_file, counter=(counter - 2))
        return
    except (ConnectionError, MaxRetryError, NewConnectionError) as e:
        print(f'Too many requests for {city[0]}, IP {proxy}, waiting 60 s')
        time.sleep(60)
        check_booking(city, people, dates, out_file, counter=(counter - 1))
        return
    else:
        for link in links:
            time.sleep(random.randint(2, 5))
            save(city, dates, link, out_file)
        print(f'Found {len(links)} for {city[0]} on {proxy}')
        time.sleep(10)


def waitForXPATH(browser, xpath):
    """
    Waits until element is present on webpage, by specified xpath
    """

    return WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def waitForCSS(browser, css):
    """
    Waits until element is present on webpage, by specified css selector
    """

    return WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css))
    )


def inputCity(browser, city):
    """
    Insert city into a form on website.

    Parameters
    ----------
    browser : webdriver.Chrome
        The browser used to connect and scrap webpage
    city : str
        Name of city for search
    """

    city_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[1]/div[1]/div[1]/label/input'
    city_field = waitForXPATH(browser, city_xpath)
    city_field.send_keys(city)


def inputDateFrom(browser, date):
    """
    Insert starting date into a form on website.

    Parameters
    ----------
    browser : webdriver.Chrome
        The browser used to connect and scrap webpage
    date : datetime
        Date on which starts the holiday
    """

    field_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[2]/div[1]/div[2]'
    date_field = waitForXPATH(browser, field_xpath)
    browser.execute_script("arguments[0].click();", date_field)
    month = 1 if (date.month == datetime.datetime.now().month) else 2
    column = date.weekday() + 1
    row = math.ceil((column - 1 + date.day) / 7) + 1
    date_xpath = f'/html/body/div[5]/div/div/div[2]/form/div[1]/div[2]/div[2]/div/div/div[3]/div[{month}]/table/tbody/tr[{row}]/td[{column}]'
    time.sleep(1)
    date = waitForXPATH(browser, date_xpath)
    browser.execute_script("arguments[0].click();", date)



def inputDateTo(browser, date):
    """
    Insert ending date into a form on website.

    Parameters
    ----------
    browser : webdriver.Chrome
        The browser used to connect and scrap webpage
    date : datetime
        Date on which ends the holiday
    """
    
    month = 1 if (date.month == datetime.datetime.now().month) else 2
    column = date.weekday() + 1
    row = math.ceil((column - 1 + date.day) / 7) + 1
    date_xpath = f'/html/body/div[5]/div/div/div[2]/form/div[1]/div[2]/div[2]/div/div/div[3]/div[{month}]/table/tbody/tr[{row}]/td[{column}]'
    date = waitForXPATH(browser, date_xpath)
    browser.execute_script("arguments[0].click();", date)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", waitForXPATH(browser, '/html/body'))


def inputPeople(browser, people):
    """
    Insert people data into a form on website.

    Parameters
    ----------
    browser : webdriver.Chrome
        The browser used to connect and scrap webpage
    people : dict
        Disctionary containing number of adults, number of children and their ages
    
    Example
    -------
    >>> people = {
    ...     'adults': 5 :int,
    ...     'children': 2 :int,
    ...     'ages': (10, 15) :tuple
    ...}
    """
    
    field_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]'
    waitForXPATH(browser, field_xpath).click()

    # parents
    adults_number_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[1]/div/div[2]/span[1]'
    adults_plus_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[1]/div/div[2]/button[2]'
    adults_minus_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[1]/div/div[2]/button[1]'
    number_of_adults = int(waitForXPATH(browser, adults_number_xpath).text)
    if number_of_adults < people.get('adults'):
        for i in range(people.get('adults') - number_of_adults):
            plus = waitForXPATH(browser, adults_plus_xpath)
            time.sleep(1)
            browser.execute_script("arguments[0].click();", plus)
    elif number_of_adults > people.get('adults'):
        for i in range(number_of_adults - people.get('adults')):
            minus = waitForXPATH(browser, adults_minus_xpath)
            time.sleep(1)
            browser.execute_script("arguments[0].click();", minus)
    
    # children
    children_number_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[2]/div/div[2]/span[1]'
    children_plus_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[2]/div/div[2]/button[2]'
    children_minus_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[2]/div/div[2]/button[1]'
    number_of_children = int(waitForXPATH(browser, children_number_xpath).text)
    if number_of_children < people.get('children'):
        for i in range(people.get('children') - number_of_children):
            plus = waitForXPATH(browser, children_plus_xpath)
            time.sleep(1)
            browser.execute_script("arguments[0].click();", plus)
    elif number_of_children > people.get('children'):
        for i in range(number_of_children - people.get('children')):
            minus = waitForXPATH(browser, children_minus_xpath)
            time.sleep(1)
            browser.execute_script("arguments[0].click();", minus)
    
    # children ages
    for i, age in enumerate(people.get('ages')):
        time.sleep(random.random() * 2)
        child_age_xpath = f'/html/body/div[5]/div/div/div[2]/form/div[1]/div[3]/div[2]/div/div/div[4]/select[{i+1}]'
        waitForXPATH(browser, child_age_xpath).send_keys(age)


def succesfulSearch(browser, city):
    """
    Check if the city was successfully recognised.

    Parameters
    ----------
    browser : webdriver.Chrome
        The browser used to connect and scrap webpage
    city : str
        Name of city for search
    """

    header_xpath = '/html/body/div[6]/div/div[3]/div[1]/div[1]/div[4]/div/div[1]/div/h1'
    header = str(waitForXPATH(browser, header_xpath).text)
    return city.lower() in header.lower()


def getSearchLinks(browser):
    """
    Return the result links from webpage

    Parameters
    ----------
    browser : webdriver.Chrome
        The browser used to connect and scrap webpage
    """

    # filters
    waitForCSS(browser, '#filter_price a')
    price = browser.find_elements(By.CSS_SELECTOR, '#filter_price a')[0]
    browser.execute_script("arguments[0].click();", price)
    time.sleep(1)
    avaliable = waitForCSS(browser, '#filter_out_of_stock a')
    browser.execute_script("arguments[0].click();", avaliable)

    # results
    number_of_results_h1 = waitForCSS(browser, '.sr_header h1').text
    number_of_results = int(''.join(i for i in number_of_results_h1 if i.isdigit()))
    
    links = set()
    for i in range(math.ceil(number_of_results/25)):
        waitForCSS(browser, '#hotellist_inner>div')
        soup = BeautifulSoup(browser.page_source, features='html.parser')
        results = soup.select('#hotellist_inner>div')
        for div in results:
            if div.get('class') and 'sr_separator_first' in div.get('class'):
                return links
            link = div.select_one('div a')
            if link:
                links.add('https://www.booking.com' + link.get('href'))
        
        time.sleep(1)
        next_page = waitForCSS(browser, '.bui-pagination__link.paging-next')
        browser.execute_script("arguments[0].click();", next_page)

    return links


def save(city, dates, url, results_file, counter=3):
    """
    Open given url, extract data and save to file.

    Parameters
    ----------
    city : str
        Name of city for search
    dates : tuple
        A pair of `datetime` objects, one for starting and one for ending date
    url : str
        Link to page of hotel
    results_file : str
        Name of the file for saving
    """

    if counter <= 0:
        return

    if not os.path.exists(results_file):
        with open(results_file, 'w+') as f:
            f.write('MIEJSCOWOŚĆ \t WIELKOŚĆ \t ODLEGŁOŚĆ DO MORZA \t NAZWA \t DATA \t CENA ZA CAŁOŚĆ \t CENA ZA DZIEŃ \t NR TELEFONU \t LINK \n')
    
    proxy = chooseProxy()
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server={proxy}')

    try:
        with webdriver.Chrome(executable_path='/home/kamil/Desktop/Wakacje/files/chromedriver', options=options) as browser:
            browser.get(url)

            days = (dates[1] - dates[0]).days
            waitForCSS(browser, '.totalPrice')
            time.sleep(1)
            price_for_all = browser.find_elements(By.CSS_SELECTOR, '.totalPrice .bui-price-display__value.prco-text-nowrap-helper.prco-inline-block-maker-helper')
            time.sleep(1)
            place_name = browser.find_element(By.ID, 'hp_hotel_name')
            if place_name and len(price_for_all) > 0:
                price_for_all = price_for_all[0].text
                place_name = place_name.text

    except (WebDriverException, ConnectionError, MaxRetryError, NewConnectionError):
        save(city, dates, url, results_file, counter=(counter - 1))
        return

    else:
        if type(price_for_all) == str and type(place_name) == str:
            price_for_all_digits = float(''.join(i for i in price_for_all if i.isdigit() or i == '.'))
            price_for_day = price_for_all_digits / days
        else:
            price_for_all = 'NAN'
            price_for_day = 0.00
            place_name = '---'
        with open(results_file, 'a+') as f:
            f.write('%s \t %d \t %.2f km \t %s \t %s \t %s \t %.2f \t %s \t %s \n' % (
                city[0],
                city[2],
                city[1],
                place_name.replace('Homestay ', '').replace('\n', ''),
                dates[0].strftime('%d.%m.%Y') + ' - ' + dates[1].strftime('%d.%m.%Y'),
                price_for_all,
                price_for_day,
                '---',
                url
            ))


def chooseProxy():
    """
    Choose a proxy IP address, at random from two groups.
    Group `proxysBest` have adresses with 100% avaliability 
    and response times below 20s. Group `proxysGood` have 
    avaliability above 75%, but worse response times (sometimes 
    up to one minute). The group is chosen with 75-25 chance, and
    inside the grouo address is chosen with uniform probability.
    """

    proxysBest = [
        '80.187.140.74:8080',   #8/8        6s 
        '18.159.45.67:3128',    #8/8        15s
        '110.164.253.85:8080',  #5/5        19s
        '199.217.116.5:5836',   #5/5        17s
        '173.249.30.74:8080',   #5/5        7s
        '134.122.93.160:3128',  #5/5        8s
        '195.154.233.185:5836', #5/5        14s
        '95.217.120.170:8888',  #5/5        7s
        '148.251.153.226:3128', #5/5        19s
        '13.75.114.68:25222'    #5/5        17s
    ]
    proxysGood = [
        '91.52.26.73:8080',     #6/8
        '209.250.231.157:33122',#6/8
        '51.161.62.117:8080',   #5/5
        '206.198.131.172:8080', #4/5
        '212.83.131.192:80',    #3/5
        '78.96.125.24:3128',    #5/5
        '35.189.133.228:8080',  #4/5
        '62.244.28.72:5836',    #4/5
        '80.23.125.226:3128',   #5/5
        '80.109.201.225:3128',  #4/5
        '109.161.48.141:3128',  #4/5
        '36.37.73.246:8080',    #5/5
        '103.216.51.210:8191',  #5/5
    ]
    if random.random() < 0.75:
        return random.choice(proxysBest)
    else:
        return random.choice(proxysGood)