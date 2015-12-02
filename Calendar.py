'''Module that contains the class to create calendars.'''

class Calendar:
    '''A class that represents a list of events.

    Attributes:
        file_name (string): The name of the file in which to write the
                            events.
        events (list<Event>): A list of Event.
    '''
    def __init__(self, file_name="schedule.csv"):
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

    def write_to_file(self, has_description=False):
        '''Write the events in a file.

        Args:
            has_description (bool): A boolean indicating if there is a description.

        Raises:
            TypeError: If has_description is not a boolean.
        '''
        if not isinstance(has_description, bool):
            raise TypeError("has_description is not a boolean")
        with open(self.file_name, 'w+') as file:
            if not has_description:
                file.write("Subject,Start Date,Start Time,End Date,End Time,Location")
            else:
                file.write("Subject,Start Date,Start Time,End Date,End Time,Description,Location")
            for event in self.events:
                file.write("\n")
                file.write(event.format())
