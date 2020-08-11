import sys
import time
import datetime
sys.path.append('..') # for using decorators (module from parent dir)
from selenium import webdriver
from websites.booking import inputCity, waitForXPATH


def check_booking(city, people, dates, out_file, counter=5):
    url = 'https://www.booking.com/'
    with webdriver.Chrome(executable_path='/home/kamil/Desktop/Wakacje/files/chromedriver') as browser:
        browser.get(url)
        inputCity(browser, city[0])
        submit_btn_xpath = '/html/body/div[5]/div/div/div[2]/form/div[1]/div[4]/div[2]/button'
        submit = waitForXPATH(browser, submit_btn_xpath)
        browser.execute_script("arguments[0].click();", submit)
        linkInjection(browser, people, dates)


def linkInjection(browser, people, dates):
    url = str(browser.current_url)
    # people and dates
    data_index = url.find('checkin_year')
    if data_index > -1:
        url = url[:data_index]
    new_data_url = f'checkin_year={dates[0].year}&' + \
                   f'checkin_month={dates[0].month}&' + \
                   f'checkin_monthday={dates[0].day}&' + \
                   f'checkout_year={dates[1].year}&' + \
                   f'checkout_month={dates[1].month}&' + \
                   f'checkout_monthday={dates[1].day}&' + \
                   f'group_adults={people.get("adults")}&' + \
                   f'group_children={people.get("children")}'
    for age in people.get('ages'):
        new_data_url += f'&age={age}'
    new_data_url += f'&no_rooms=1&from_sf=1'
    url += new_data_url
    # filters
    filters = '&nflt=pri%3D1%3Boos%3D1%3B'
    url += filters
    return url


if __name__ == "__main__":
    city = ('Junoszyno', 0, 0)
    people = {
        'adults': 4,
        'children': 2,
        'ages': (10, 15)
    }
    dates = (
        datetime.datetime.strptime('17.08.2020', '%d.%m.%Y'),   # from
        datetime.datetime.strptime('26.08.2020', '%d.%m.%Y')    # to
    )
    check_booking(city, people, dates, 'test.csv')