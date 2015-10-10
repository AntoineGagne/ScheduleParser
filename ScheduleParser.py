import Account
import Calendar
import Events

from bs4 import BeautifulSoup
import datetime
import getpass
import re
import requests

WEEK_DAYS = {"L": 0, "M": 1, "R": 2, "J": 3, "V": 4, "S": 5, "D": 6}

idul = input("Enter your IDUL: ")
pin = getpass.getpass()

account = Account.Account(idul, pin)
login_infos = {'sid' : account.username, 
               'PIN' : account.password}
calendar = Calendar.Calendar()

print("\rProcessing...", end="")

with requests.session() as session:
    #The constant headers that are useful to keep
    session.headers['Host'] = 'capsuleweb.ulaval.ca'
    session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'
    session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    session.headers['Accept-Language'] = 'en-US,en;q=0.5'
    session.headers['Accept-Encoding'] = 'gzip, deflate'
    session.headers['DNT'] = '1'
    session.headers['Connection'] = 'keep-alive'

    #The headers that are needed to login
    login_headers = {'Cookie' : 'TESTID=set; _ga=GA1.2.1516654279.1441114981; __utma=17087078.1516654279.1441114981.1442264931.1442264931.1; __utmz=17087078.1442264931.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); accessibility=false'}
               

    #Connect to the login page
    login_page = session.get("https://capsuleweb.ulaval.ca/pls/etprod8/twbkwbis.P_WWWLogin")
    html_parser = BeautifulSoup(login_page.text)

    #Send a POST to the URL specified by the action attribute of the form
    post_url = "https://capsuleweb.ulaval.ca{0}".format(html_parser.form['action'])
    response = session.post(post_url, data=login_infos, headers=login_headers, allow_redirects=True)

    #Go to the redirection page
    html_parser = BeautifulSoup(response.text)
    redirect_url = html_parser.meta['content'].split('url=')[1]
    redirect_page = session.get("https://capsuleweb.ulaval.ca{0}".format(redirect_url))

    #Go to the "Renseignement des études" page
    informations_about_studies_page_url = "https://capsuleweb.ulaval.ca/pls/etprod8/twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu"
    informations_about_studies_page = session.get(informations_about_studies_page_url)

    #Go to the "Inscription" page
    inscription_page_url = "https://capsuleweb.ulaval.ca/pls/etprod8/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu"
    inscription_page = session.get(inscription_page_url)

    #Go to the "Horaire detaillee" page
    detailed_schedule_page_url = "https://capsuleweb.ulaval.ca/pls/etprod8/bwskfshd.P_CrseSchdDetl"
    detailed_schedule_page = session.get(detailed_schedule_page_url)

    #Choose the most recent schedule
    html_parser = BeautifulSoup(detailed_schedule_page.text)
    post_url = html_parser.find_all('form')[1]['action']
    post_url = "https://capsuleweb.ulaval.ca{0}".format(post_url)
    most_recent_schedule_value = html_parser.find('option')['value']
    form_infos = {'term_in' : most_recent_schedule_value}
    detailed_schedule_page = session.post(post_url, data=form_infos )

    #Parse the HTML of the "Horaire detaillee" page
    html_parser = BeautifulSoup(detailed_schedule_page.text)
    #Get the name of the courses
    captions = html_parser.find_all('caption', 'captiontext')
    good_captions = re.compile(".*-.*")
    filter_good_captions = lambda x: good_captions.match(str(x))
    course_name = list(filter(filter_good_captions, captions))
    tables = html_parser.find_all('table', 'datadisplaytable')
    course_number = 0
    for row in range(3, len(tables), 2):
        course_infos = tables[row].find_all('tr')
        for course_info in course_infos:
            course_info = course_info.find_all('td', 'dddefault')
            if course_info:
                course_caption = course_name[course_number].text
                time = course_info[1].text.split('-')
                starting_time = time[0].split(':')
                ending_time = time[1].split(':')
                week_day = course_info[2].text
                location = course_info[3].text
                date = course_info[4].text.split('-')
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
                if WEEK_DAYS[week_day] >= starting_date_object.weekday():
                    delta_days = WEEK_DAYS[week_day] - starting_date_object.weekday()
                    time_delta = datetime.timedelta(delta_days)
                    starting_date_object = starting_date_object + time_delta
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
                    calendar.events.append(event)
                    #Interval of 7 days between each week
                    for days in range(time_between_start_and_end.days // 7):
                        delta_day = datetime.timedelta(7)
                        starting_date_object = starting_date_object + delta_day
                        ending_date_object = ending_date_object + delta_day
                        event = Events.Event(course_caption,
                                             starting_date_object,
                                             ending_date_object,
                                             location)
                        calendar.events.append(event)
        course_number += 1
calendar.write_to_file()
print("\rFile created with success!")
