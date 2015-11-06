import datetime

class Event:
    '''A class that represents an event.
    
    Attributes:
        subject (string): The title of the event.
        start_date (datetime): The starting time and date of the event.
        end_date (datetime): The ending time and date of the event.
        description (string): Some extra informations about the event.
        location (string): The location of the event.
    '''
    def __init__(self, subject, start_date, end_date, location):
        '''Constructor for the Event class.

        Args:
            subject (string): The title of the event.
            start_date (datetime): The starting time and date of the event.
            end_date (datetime): The ending time and date of the event.,
            location (string): The location of the event.

        Raises:
            TypeError: If the types don't correspond.
        '''
        if not isinstance(subject, str):
            raise TypeError("The subject type is not a string")
        if not isinstance(start_date, datetime.datetime):
            raise TypeError("The starting date is not a datetime object")
        if not isinstance(end_date, datetime.datetime):
            raise TypeError("The ending date is not a datetime object")
        if not isinstance(location, str):
            raise TypeError("The location is not a string")
        self.subject = subject
        self.start_date = start_date
        self.end_date = end_date
        self.description = ""
        self.location = location

    def format(self):
        '''Format the Event class members
        
        Returns:
            datas (string): The formatted datas.
        '''
        datas = self.subject + ","
        datas += "{0}/{1}/{2},".format(self.start_date.month,
                                       self.start_date.day,
                                       self.start_date.year)

        beginning_minute = self.start_date.minute
        if self.start_date.minute < 10:
            beginning_minute = "0" + str(self.start_date.minute)
        if self.start_date.hour < 12:
            datas += "{0}:{1} AM,".format(self.start_date.hour,
                                          beginning_minute)
        elif self.start_date.hour == 12:
            datas += "12:{0} PM,".format(beginning_minute)
        else:
            datas += "{0}:{1} PM,".format(self.start_date.hour - 12,
                                          beginning_minute)

        datas += "{0}/{1}/{2},".format(self.end_date.month,
                                       self.end_date.day,
                                       self.end_date.year)
        end_minute = self.end_date.minute
        if self.end_date.minute < 10:
            end_minute = "0" + str(self.end_date.minute)
        if self.end_date.hour < 12:
            datas += "{0}:{1} AM,".format(self.end_date.hour,
                                          end_minute)
        elif self.end_date.hour == 12:
            datas += "12:{0} PM,".format(end_minute)
        else:
            datas += "{0}:{1} PM,".format(self.end_date.hour - 12,
                                          end_minute)
        if self.description:
            datas += self.description + ","
        datas += self.location
        return datas
