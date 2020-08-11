import time
import datetime
from lists import getCitiesList
from search import checkPossibilities


if __name__ == '__main__':
    # cities fulfilling criteria
    max_distance = 6
    min_population = 0
    max_population = 20000
    cities = getCitiesList(max_distance, min_population, max_population)
    print(f'Found {len(cities)} cities with less then {max_distance} km to sea and population in [{min_population}, {max_population}]')
    '''
    all                         -> 4011 cities
    dist < 10km, pop < 100.000  -> 1232 cities
    dist < 10km, pop < 10.000   -> 1207 cities
    dist < 5km,  pop < 10.000   ->  598 cities
    dist < 5km,  pop < 1.000    ->  556 cities
    without population data     ->  517 cities
    '''
    # data for searching
    people = {
        'adults': 4,
        'children': 2,
        'ages': (10, 15)
    }
    dates = (
        datetime.datetime.strptime('17.08.2020', '%d.%m.%Y'),   # from
        datetime.datetime.strptime('26.08.2020', '%d.%m.%Y')    # to
    )
    times = []
    try:
        for city in cities:
            st = time.time()
            checkPossibilities(city=city,
                            people=people, 
                            dates=dates, 
                            out_file='files/search_results_v2.csv')
            times.append(time.time() - st)
    except KeyboardInterrupt:
        print('avg time for city: %.2f s' % (sum(times) / len(times) if len(times)>0 else 0))
    finally:
        print('avg time for city: %.2f s' % (sum(times) / len(times) if len(times)>0 else 0))