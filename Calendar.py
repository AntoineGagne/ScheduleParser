class Calendar:
    '''A class that represents a list of events.

    Attributes:
        file_name (string): The name of the file in which to write the 
                            events.
        events (list<Event>): A list of Event.
    '''
    def __init__(self, file_name = "schedule.csv"):
        '''Constructor of the Calendar class.

        Args:
            file_name (string): The name of the file in which to write the
                                events.

        Raises:
            TypeError: If the file name is not a string.
        '''
        if not isinstance(file_name, str):
            raise TypeError("The file name is not a string")
        self.file_name = file_name
        self.events = []

    def write_to_file(self):
        '''Write the events in a file.'''
        with open(self.file_name, 'w+') as file:
            file.write("Subject,Start Date,Start Time,End Date,End Time,Location")
            for event in self.events:
                file.write("\n")
                file.write(event.format())
