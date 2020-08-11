from websites.booking import check_booking
from websites.noclegi import check_noclegi
from websites.fajnewczasy import check_fajnewczasy


def checkPossibilities(city, people, dates, out_file):
    """
    Parameters
    ----------
    people : dict
        Dictionary containing number of adults, children and age of each child
    dates : tuple
        Datetime objects of starting and ending date
    out_file : str
        Name of file to which results will be saved

    Run subfunctions for diffenent domains
    """

    check_booking(city, people, dates, out_file)      # booking.com
    check_noclegi(city, people, dates, out_file)      # noclegi.pl
    check_fajnewczasy(city, people, dates, out_file)  # fajnewczasy.pl