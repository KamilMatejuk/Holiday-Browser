import time
from selenium import webdriver


def proxyTest():
    """
    Iterate through each proxy address, and check average
    response time from 5 runs.
    """

    proxys = [
        '91.52.26.73:8080',     #6/8
        '80.187.140.74:8080',   #8/8        6s 
        '18.159.45.67:3128',    #8/8        15s
        '209.250.231.157:33122',#6/8
        '206.198.131.172:8080', #4/5        15s
        '51.161.62.117:8080',   #5/5
        '212.83.131.192:80',    #3/5
        '78.96.125.24:3128',    #5/5
        '35.189.133.228:8080',  #4/5
        '110.164.253.85:8080',  #5/5        19s
        '62.244.28.72:5836',    #4/5
        '199.217.116.5:5836',   #5/5        17s
        '80.23.125.226:3128',   #5/5
        '80.109.201.225:3128',  #4/5
        '109.161.48.141:3128',  #4/5
        '173.249.30.74:8080',   #5/5        7s
        '36.37.73.246:8080',    #5/5
        '134.122.93.160:3128',  #5/5        8s
        '195.154.233.185:5836', #5/5        14s
        '95.217.120.170:8888',  #5/5        7s
        '94.102.2.145:3128',    #5/5        19s
        '148.251.153.226:3128', #5/5        19s
        '103.216.51.210:8191',  #5/5
        '13.75.114.68:25222'    #5/5        17s
    ]
    for proxy in proxys:
        errors = 0
        times = 0
        for _ in range(5):
            options = webdriver.ChromeOptions()
            options.add_argument(f'--proxy-server={proxy}')

            st = time.time()
            with webdriver.Chrome(
                executable_path='/home/kamil/Desktop/Wakacje/files/chromedriver', options=options
                ) as browser:

                browser.get('https://www.booking.com/')
                src = str(browser.page_source)

            if 'ERR_' in src:
                errors += 1
            else:
                times += int(time.time() - st)
        print('%-22s succesful: %d/5   avg time: %.0f s' % (
            proxy, 
            5-errors, 
            (times/(5-errors)) if errors < 5 else 0)
        )