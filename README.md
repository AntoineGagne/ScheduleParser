# ScheduleParser

**Deprecated:** With *MonPortail*, this script doesn't work anymore...

- [Usage](#Usage)
- [How to run](#How to run)
- [Dependencies](#Dependencies)
- [Options](#Options) 

## Usage

This program will log into your Université Laval account on Capsule and will parse the schedule and put it in a .csv file that is importable by Google Agenda.

## Dependencies

This program depends on Python 3.x.x and the following modules:
+ beautifulsoup4
+ requests

You can install these dependencies by executing the following command:

```sh
pip install -r requirements.txt
```

## How to run

You can run this program by executing the following command in your terminal:

```sh
python ScheduleParser.py [OPTIONS]
```

## Options
    -h, --help                                                      Print this message.
    -f FILENAME, --filename FILENAME                                File name in which to put the schedule. (default: schedule.csv)
    -d, --description                                               Adds a description to the event. (default: False)
    -s YEAR SEASON, --semester_date YEAR SEASON                     Choose the schedule of a specific semester (ie: 2016 Hiver). (default: None)
