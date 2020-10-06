from urllib.request import urlopen

import os
import time
import math
import datetime
import random
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, NewConnectionError
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

'''
TODO
1. Przepisać wpisywanie dat i filtrów na dodanie do linka
2. Zrobić konwertowanie walut (dolar i euro) - usunąć proxy z poza europy i stanów
'''


def check_booking(city:str, people:dict, dates:tuple, out_file:str, counter=5):
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

    url = generateUrl(city, people, dates)
    proxy = chooseProxy()
    options = webdriver.ChromeOptions()
    # options.add_argument(f'--proxy-server={proxy}')
    # options.add_argument('--headless')
    try:
        with webdriver.Chrome(executable_path='/home/kamil/Desktop/Wakacje/files/chromedriver', options=options) as browser:
            browser.get(url)
            WebDriverWait(browser, 45).until(
                EC.presence_of_element_located((By.XPATH, '/html/body'))
            )
            # couldn't load with given IP, proxy error
            if 'ERR_' in browser.page_source:
                print(f'Page couldn\'t load with IP {proxy}')
                check_booking(city, people, dates, out_file, counter=(counter - 1))
                return
            soup = BeautifulSoup(browser.page_source, features='html.parser')
            # couldn't find city
            if city[0].lower() not in str(soup.title).lower():
                print(f'Couldn\'t find {city[0]}')
                return
            links = getSearchLinks(soup, url)

    except TimeoutException:
        print(f'Too long waiting time for {city[0]}, IP {proxy}')
        check_booking(city, people, dates, out_file, counter=(counter - 1))
        return
    except WebDriverException:
        # no element on page
        print('IP ' + proxy + ', WebDriverException')
        check_booking(city, people, dates, out_file, counter=(counter - 1))
        return
    except (ConnectionError, MaxRetryError, NewConnectionError):
        print(f'Too many requests for {city[0]}, IP {proxy}')
        check_booking(city, people, dates, out_file, counter=(counter - 1))
        return
    else:
        for link in links:
            time.sleep(random.randint(2, 5))
            save(city, dates, link, out_file)
        print(f'Found {len(links)} for {city[0]} on {proxy}')


def generateUrl(city, people, dates):
    """
    Parameters
    ----------
    city : str
        City for which is searching
    people : dict
        Dictionary containing number of adults, children and age of each child
    dates : tuple
        Datetime objects of starting and ending date
        
    Generates search url for booking.com with given data
    """

    # basic url
    url = 'https://www.booking.com/searchresults.pl.html?'
    # city name
    url += f'ss={city[0]}'
    # start date
    url += f'&checkin_year={dates[0].year}'
    url += f'&checkin_month={dates[0].month}'
    url += f'&checkin_monthday={dates[0].day}'
    # end date
    url += f'&checkout_year={dates[1].year}'
    url += f'&checkout_month={dates[1].month}'
    url += f'&checkout_monthday={dates[1].day}'
    # people
    url += f'&group_adults={people.get("adults", 0)}'
    url += f'&group_children={people.get("children", 0)}'
    for age in people.get('ages', []):
        url += f'&age={age}'
    # url += f'&no_rooms={}'
    # show only avaliable
    url += '&nflt=oos%3D1%3B'
    return url


# def getSearchLinks(browser, url, secondary=False):
#     # dodać &offset=25 do linku
#     """
#     Return the result links from webpage

#     Parameters
#     ----------
#     browser : webdriver.Chrome
#         The browser used to connect and scrap webpage
#     url : str
#         A link of search page
#     secondary : bool
#         Specifies if its the first page of search (False), or one of the next (True)
#     """

#     browser.get(url)
#     time.sleep(5)
#     soup = BeautifulSoup(browser.page_source, features='html.parser')
#     links = set()
#     results = soup.select('#hotellist_inner>div')
#     for div in results:
#         if div.get('class') and 'sr_separator_first' in div.get('class'):
#             return links
#         link = div.select_one('div a')
#         if link:
#             links.add('https://www.booking.com' + link.get('href'))
    
#     if secondary:
#         return links

#     number_of_results_h1 = soup.select_one('.sr_header h1')
#     if number_of_results_h1 is not None:
#         number_of_results = int(''.join(i for i in number_of_results_h1.text if i.isdigit()))
#         for i in range(math.floor(number_of_results/25)):
#             links = links | getSearchLinks(browser, url + f'&offset={25 * (i+1)}', True)

#     return links


# def save(city, dates, url, results_file, counter=3):
#     """
#     Open given url, extract data and save to file.

#     Parameters
#     ----------
#     city : str
#         Name of city for search
#     dates : tuple
#         A pair of `datetime` objects, one for starting and one for ending date
#     url : str
#         Link to page of hotel
#     results_file : str
#         Name of the file for saving
#     """

#     if counter <= 0:
#         return

#     if not os.path.exists(results_file):
#         with open(results_file, 'w+') as f:
#             f.write('MIEJSCOWOŚĆ \t WIELKOŚĆ \t ODLEGŁOŚĆ DO MORZA \t NAZWA \t DATA \t CENA ZA CAŁOŚĆ \t CENA ZA DZIEŃ \t NR TELEFONU \t LINK \n')
    
#     proxy = chooseProxy()
#     options = webdriver.ChromeOptions()
#     options.add_argument(f'--proxy-server={proxy}')
#     # options.add_argument('--headless')
#     # options.add_argument('--ignore-certificate-errors')

#     try:
#         with webdriver.Chrome(executable_path='/home/kamil/Desktop/Wakacje/files/chromedriver', options=options) as browser:
#             browser.get(url)
#             WebDriverWait(browser, 45).until(EC.presence_of_element_located((By.XPATH, '/html/body/div')))
#             if 'ERR_' in browser.page_source:
#                 # couldnt load with given IP, proxy error
#                 print(f'Page couldn\'t load with IP {proxy}')
#                 save(city, dates, url, results_file, counter=(counter - 1))
#                 return
#             soup = BeautifulSoup(browser.page_source, features='html.parser')
#             with open('soup.html', 'w+') as f:
#                 f.write(str(soup))

#     except (WebDriverException, ConnectionError, MaxRetryError, NewConnectionError):
#         save(city, dates, url, results_file, counter=(counter - 1))
#         return

#     else:
#         days = (dates[1] - dates[0]).days
#         price_for_all = soup.select('.totalPrice .bui-price-display__value.prco-text-nowrap-helper.prco-inline-block-maker-helper')
#         if price_for_all is not None and len(price_for_all) > 0:
#             price_for_all = price_for_all[0].text
#             multiplier = {
#                 '€': 4.40,
#                 '$': 3.70,
#                 'zł': 1.00,
#                 '': 0.00
#             }
#             for currency in multiplier:
#                 if currency in price_for_all:
#                     value_multiplier = multiplier.get(currency)
#                     break
#             price_for_all = float(''.join(i for i in price_for_all if i.isdigit() or i == '.')) * value_multiplier
#             price_for_day = price_for_all / days
#         else:
#             price_for_all = 0.00
#             price_for_day = 0.00
            
#         place_name = soup.select_one('#hp_hotel_name')
#         if place_name is not None:
#             place_name = place_name.text.splitlines()[2].replace('\n', '')
        
#         with open(results_file, 'a+') as f:
#             f.write('%s \t %d \t %.2f km \t %s \t %s \t %.2f zł \t %.2f zł \t %s \t %s \n' % (
#                 city[0],
#                 city[2],
#                 city[1],
#                 str(place_name),
#                 dates[0].strftime('%d.%m') + ' - ' + dates[1].strftime('%d.%m'),
#                 price_for_all,
#                 price_for_day,
#                 '---',
#                 url
#             ))


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
        '199.217.116.5:5836',   #5/5        17s
        '173.249.30.74:8080',   #5/5        7s
        '134.122.93.160:3128',  #5/5        8s
        '195.154.233.185:5836', #5/5        14s
        '95.217.120.170:8888',  #5/5        7s
        '148.251.153.226:3128', #5/5        19s
    ]
    proxysGood = [
        '91.52.26.73:8080',     #6/8
        '51.161.62.117:8080',   #5/5
        '206.198.131.172:8080', #4/5
        '212.83.131.192:80',    #3/5
        '80.23.125.226:3128',   #5/5
        '80.109.201.225:3128',  #4/5
    ]
    if random.random() < 0.75:
        return random.choice(proxysBest)
    else:
        return random.choice(proxysGood)