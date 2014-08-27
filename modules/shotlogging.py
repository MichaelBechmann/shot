# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 6, 2013

This module defines standard logger(s) for the application shot.
'''

from shotconfig import config
import datetime
import logging

# logging, according to http://docs.python.org/2/howto/logging.html

filename = 'applications/%s/__etc/logs/background/%s.log' % (config.appname, datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
fh = logging.FileHandler(filename = filename)
formatter = logging.Formatter('%(asctime)s (%(levelname)s): %(message)s')
fh.setFormatter(formatter)
logger_bg = logging.getLogger()
logger_bg.setLevel(logging.DEBUG)

# remove standard logger (otherwise everything is poured into error.log
logger_bg.removeHandler(logger_bg.handlers[0])

logger_bg.addHandler(fh)