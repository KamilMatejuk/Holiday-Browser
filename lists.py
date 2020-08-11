from geopy import geocoders, distance, exc


def getCoastline():
    """
    Returns a list of coordinates alongside Polish coastline,
    reading form 'coastline.csv'
    """

    with open('files/coastline.csv') as f:
        coast = [(float(l.split()[1]), float(l.split()[0])) for l in f.readlines()]
    # tuples (lat, lon)
    return coast


def distanceToSee(city):
    """
    Calculates distance to see from specified city, based on city name
    """

    try:
        gn = geocoders.GeoNames(username='holiday2')    # geonames.org/login (holidays, holiday2)
        location = gn.geocode(city)
        if location:
            pop = location.raw.get('population')
            lat, lon = location.raw.get('lat'), location.raw.get('lng')
            # poland lat [53, 55] / lon [14, 20]
            coast = getCoastline()
            minDist = min(distance.distance((lat, lon), c).km for c in coast)
            return (minDist, pop)
        return (None, None)
    except Exception as e:
        print(e)
        return (None, None)


def generateCitiesList():
    """
    Generates a file with pairs (city, distance to see) from list of cities
    specified in 'cities.txt' file and saves to 'cities.csv'
    """

    with open('files/cities.txt', 'r+') as f:
        cities = f.read().replace(',', '').splitlines()
    with open('files/cities.csv', 'a+') as f:
        for c in cities:
            dist, pop = distanceToSee(c)
            if dist and dist < 100:
                print('%-25s %.2f' % (c, cities.index(c) / len(cities) * 100) + '%')
                f.write(c + ', \t' + str(dist) + ', \t' + str(pop) + '\n')


def getCitiesList(max_distance :int, min_population :int, max_population :int):
    """
    Parameters
    ----------
    max_distance : int
        Maximal distance to sea in straight line
    min_population : int
        Minimal size of a city
    max_population : int
        Maximal size of a city
    
    Reads cities, distances and populations form file 'cities.csv'
    """

    cities = []
    with open('files/cities.csv') as f:
        for line in f.readlines():
            data = line.split(',')
            city = data[0]
            distance = float(data[1].strip())
            population = int(data[2].strip())
            if distance <= max_distance and \
                min_population <= population <= max_population:
                cities.append((city, distance, population))
    return cities
