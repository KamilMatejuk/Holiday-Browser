import sys
import time
import datetime
sys.path.append('.') # for using decorators (module from parent dir)
from websites.booking import check_booking


if __name__ == "__main__":
    city = ('Wrocław', 0, 0)
    people = {
        'adults': 4,
        'children': 2,
        'ages': (10, 15)
    }
    dates = (
        datetime.datetime.strptime('17.11.2020', '%d.%m.%Y'),   # from
        datetime.datetime.strptime('26.11.2020', '%d.%m.%Y')    # to
    )
    check_booking(city, people, dates, 'test.csv')