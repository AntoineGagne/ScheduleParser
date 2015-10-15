#!/usr/bin/env python

import ez_setup

#install setuptools
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name = 'ScheduleParser',
      version = '1.0',
      description = 'Export the Universite Laval schedule in a .csv file.',
      author = 'Antoine Gagne',
      author_email = 'antoine.gagne.2@ulaval.ca',
      packages = find_packages(),
      entry_points = {
          'console_scripts': [
              'ScheduleParser = ScheduleParser:schedule_parser',
                             ],
          },

      install_requires = ['beautifulsoup4>=4.4.1',
                          'requests>=2.8.1']
     )
