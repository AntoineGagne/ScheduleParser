'''Module that contains the function to parse the Capsule website
   and create a file filled with the courses date and time.
'''
import argparse
import datetime
import getpass
import re

from bs4 import BeautifulSoup
import requests

import Account
import Calendar
import Events


def arguments_parser():
    '''Parse the command line argument.

    Returns:
        The command line arguments parser
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f",
                        "--file_name",
                        type=str,
                        default="schedule.csv",
                        help="File name in which to put the schedule.")
    parser.add_argument("-d",
                        "--description",
                        action='store_true',
                        default=False,
                        help="Adds a description to the event.")
    parser.add_argument("-s",
                        "--semester_date",
                        metavar=("YEAR", "MONTH"),
                        nargs=2,
                        help="Choose the semester schedule you want (ex: 2016 Hiver)")

    return parser.parse_args()


def navigate_website():
    '''Navigate the Capsule website and creates the events file.'''
    #Arguments passed to the program
    arguments = arguments_parser()

    try:
        #Date for which the user wants the schedule
        schedule_date = handle_semester_date(arguments.semester_date)

        idul = input("Enter your IDUL: ")
        pin = getpass.getpass()

        account = Account.Account(idul, pin)
        login_infos = {'sid' : account.username,
                       'PIN' : account.password}

        calendar = Calendar.Calendar(arguments.file_name)

        print("\rLogging in...", end="")

        with requests.session() as session:
            set_session_headers(session)
            login(login_infos, session)
            detailed_schedule_page = navigate_to_schedule(session, schedule_date)
            parsing_schedule(detailed_schedule_page.text, arguments.description, calendar)

    except IndexError:
        print("\rThe username or password provided is incorrect.")
    except RuntimeError:
        print("\rThe precised year should be higher than 2009.\n"
              "The precised month should be one of those:\n  - Hiver\n  - Ete\n  - Automne")


def handle_semester_date(semester_date):
    '''Format the semester_date arguments into the right format.

    Args:
        semester_date (list): The month and year to format

    Returns:
        schedule_date (string): The formatted semester_date
    '''
    schedule_date = None
    if semester_date:
        month = semester_date[1]
        year = semester_date[0]
        if not re.compile("^[AaEeHh].*$").match(month) or int(year) < 2009:
            raise RuntimeError("Invalid command line argument")
        semesters_code = {"A": "09", "H": "01", "E": "05"}
        schedule_date = str(year) + semesters_code[month.capitalize()[0]]

    return schedule_date


def set_session_headers(session):
    '''Set the session headers used to log in to the Capsule website.

    Args:
        session (Session): The session object used to navigate
    '''
    #The constant headers that are useful to keep
    session.headers['Host'] = 'capsuleweb.ulaval.ca'
    session.headers['User-Agent'] = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) '
                                     'Gecko/20100101 Firefox/41.0')
    session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    session.headers['Accept-Language'] = 'en-US,en;q=0.5'
    session.headers['Accept-Encoding'] = 'gzip, deflate'
    session.headers['DNT'] = '1'
    session.headers['Connection'] = 'keep-alive'


def login(login_infos, session):
    '''Log in the Capsule website.

    Args:
        login_infos (dict<string, string>): The username and password of the student
        session (Session): The session object used to navigate
    '''
    #The headers that are needed to login
    login_headers = {'Cookie' : 'TESTID=set; _ga=GA1.2.1516654279.1441114981; '
                                '__utma=17087078.1516654279.1441114981.1442264931.1442264931.1; '
                                '__utmz=17087078.1442264931.1.1.utmcsr=(direct)|utmccn=(direct)|'
                                'utmcmd=(none); accessibility=false'}

    #Connect to the login page
    login_page = session.get("https://capsuleweb.ulaval.ca/pls/etprod8/twbkwbis.P_WWWLogin")
    html_parser = BeautifulSoup(login_page.text, "html.parser")

    #Send a POST to the URL specified by the action attribute of the form
    post_url = "https://capsuleweb.ulaval.ca{0}".format(html_parser.form['action'])
    response = session.post(post_url, data=login_infos, headers=login_headers, allow_redirects=True)

    #Go to the redirection page
    html_parser = BeautifulSoup(response.text, "html.parser")
    redirect_url = html_parser.meta['content'].split('url=')[1]
    session.get("https://capsuleweb.ulaval.ca{0}".format(redirect_url))

    print("\rSuccessfully logged in!", end="")


def navigate_to_schedule(session, schedule_date):
    '''Navigate to the detailed schedule page.

    Args:
        session (Session): The session object used to navigate
        schedule_date (string or None): The code that indicates which semester to parse

    Returns:
        detailed_schedule_page (string): The detailed schedule page HTML
    '''

    #Go to the "Renseignement des études" page
    informations_about_studies_url = ("https://capsuleweb.ulaval.ca/pls/etprod8/"
                                      "twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu")
    session.get(informations_about_studies_url)

    #Go to the "Inscription" page
    inscription_page_url = ("https://capsuleweb.ulaval.ca/pls/etprod8/"
                            "twbkwbis.P_GenMenu?name=bmenu.P_RegMnu")
    session.get(inscription_page_url)

    #Go to the "Horaire detaillee" page
    detailed_schedule_page_url = "https://capsuleweb.ulaval.ca/pls/etprod8/bwskfshd.P_CrseSchdDetl"
    detailed_schedule_page = session.get(detailed_schedule_page_url)

    #Choose the most recent schedule
    html_parser = BeautifulSoup(detailed_schedule_page.text, "html.parser")
    post_url = html_parser.find_all('form')[1]['action']
    post_url = "https://capsuleweb.ulaval.ca{0}".format(post_url)
    most_recent_schedule_value = html_parser.find('option')['value']
    if schedule_date:
        most_recent_schedule_value = schedule_date
    form_infos = {'term_in' : most_recent_schedule_value}
    detailed_schedule_page = session.post(post_url, data=form_infos)

    return detailed_schedule_page


def parsing_schedule(page_html, description, calendar):
    '''Parse the schedule and write the events to a file.

    Args:
        page_html (string): The HTML content of the page
        description (bool): A boolean that indicates if the user wants the course description
        calendar (Calendar): The calendar in which to put the events
    '''
    print("\rParsing the schedule...", end="")
    #Parse the HTML of the "Horaire detaillee" page
    html_parser = BeautifulSoup(page_html, "html.parser")
    #Get the name of the courses
    captions = html_parser.find_all('caption', 'captiontext')
    good_captions = re.compile(".*-.*")
    course_name = [caption for caption in captions if good_captions.match(str(caption))]
    tables = html_parser.find_all('table', 'datadisplaytable')
    course_number = 0
    week_days = {"L": 0, "M": 1, "R": 2, "J": 3, "V": 4, "S": 5, "D": 6}
    for row in range(3, len(tables), 2):
        course_infos = tables[row].find_all('tr')
        for course_info in course_infos:
            course_info = course_info.find_all('td', 'dddefault')
            if course_info:
                course_caption = course_name[course_number].text
                create_events(course_info, course_caption, description, calendar, week_days)
        course_number += 1
    calendar.write_to_file(description)
    print("\rFile created with success!")


def create_events(course_info, course_caption, description, calendar, week_days):
    '''Creates the events and put them in the calendar.

    Args:
        course_info (BeautifulSoup): The content of the current page
        course_caption (string): The name of the course
        description (bool): A boolean that indicates if the user wants the description
        calendar (Calendar): The calendar in which to put the events
        week_days (dict<string, int>): A dictionary containing the int associated with each week day
    '''
    time = course_info[1].text.split('-')
    if len(time) > 1:
        week_day = course_info[2].text
        location = course_info[3].text
        date = course_info[4].text.split('-')
        starting_date_object, ending_date_object = create_date_objects(time, date)
        if week_days[week_day] >= starting_date_object.weekday():
            delta_days = week_days[week_day] - starting_date_object.weekday()
            time_delta = datetime.timedelta(delta_days)
            starting_date_object = starting_date_object + time_delta
            ending_time = time[1].split(':')
            time_between_start_and_end = ending_date_object - starting_date_object
            ending_date_object = datetime.datetime(int(starting_date_object.year),
                                                   int(starting_date_object.month),
                                                   int(starting_date_object.day),
                                                   int(ending_time[0]),
                                                   int(ending_time[1]))
            event = Events.Event(course_caption,
                                 starting_date_object,
                                 ending_date_object,
                                 str(location))
            if description:
                add_description(event, course_info[0].text, course_info[6].text.split())
            calendar.events.append(event)

            #Interval of 7 days between each week
            for _ in range(time_between_start_and_end.days // 7):
                delta_day = datetime.timedelta(7)
                starting_date_object = starting_date_object + delta_day
                ending_date_object = ending_date_object + delta_day
                event = Events.Event(course_caption,
                                     starting_date_object,
                                     ending_date_object,
                                     location)
                if description:
                    add_description(event, course_info[0].text, course_info[6].text.split())
                calendar.events.append(event)


def create_date_objects(time, date):
    '''Create date objects

    Args:
        time (string): The starting and ending time of the event
        date (string): The starting and ending date of the event

    Returns:
        starting_date_object (datetime): The starting date and time of the event
        ending_date_object (datetime): The ending date of the event
    '''
    starting_time = time[0].split(':')
    starting_date = date[0].split('/')
    ending_date = date[1].split('/')
    starting_date_object = datetime.datetime(int(starting_date[0]),
                                             int(starting_date[1]),
                                             int(starting_date[2]),
                                             int(starting_time[0]),
                                             int(starting_time[1]))
    ending_date_object = datetime.datetime(int(ending_date[0]),
                                           int(ending_date[1]),
                                           int(ending_date[2]),
                                           int(starting_time[0]),
                                           int(starting_time[1]))

    return starting_date_object, ending_date_object


def add_description(event, class_type, teacher_name):
    '''Adds the teacher name and the course type to the event.

    Args:
        event (Event): The event in which to add the description
        class_type (string): The type of the course
        teacher_name (list<string>): A list containing the teacher's name and last name
    '''
    event.description = r'"'
    event.description += class_type
    event.description += "\n\n"
    for name in teacher_name:
        event.description += " " + name
    event.description += r'"'


if __name__ == '__main__':
    navigate_website()
