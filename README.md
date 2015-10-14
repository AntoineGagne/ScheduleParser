ScheduleParser
==============
- [Usage](#Usage)
- [How to run](#How to run)
- [Dependencies](#Dependencies)
- [Options](#Options) 

# Dependencies

To run this program, you will need Python 3.X and the following Python modules:
+   requests
+   BeautifulSoup

# Usage

This program will log into your Université Laval account on Capsule and will parse the schedule and put it in a .csv file that is importable by Google Agenda.

# How to run
You can run this program by executing the following command in your terminal:
```
python ScheduleParser.py [OPTIONS]
```

# Options
    -h,--help           Print this message.
    -f                  File name in which to put the schedule. (default: schedule.csv)
    -d                  Adds a description to the event. (default: False)
