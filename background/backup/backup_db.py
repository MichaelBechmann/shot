# -*- coding: utf-8 -*-
if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotlogging import logger_bg
from shotconfig import config
import datetime
import subprocess
'''
This function generates a backup dump of the complete shot database.
'''

logger_bg.info('start with script "backup_db" ...')

try:
    if config.enable_debug:
        p = subprocess.Popen(['whoami'], shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = p.communicate()
        for s in out.split('\n'):
            if s:
                logger_bg.debug('user obtained by whoami: ' + s)
        for s in err.split('\n'):
            if s:
                logger_bg.error(s)
                
        p = subprocess.Popen('echo $SHELL', shell = True, executable = '/bin/bash', stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = p.communicate()
        for s in out.split('\n'):
            if s:
                logger_bg.debug('shell used: ' + s)
        for s in err.split('\n'):
            if s:
                logger_bg.error(s)
                

    cmd = config.db_backup_command % {'timestamp': datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}
    logger_bg.info('shell command: %s' % cmd)
    p = subprocess.Popen(cmd, shell = True, executable = '/bin/bash', stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    
    out, err = p.communicate()
    for s in out.split('\n'):
        if s:
            logger_bg.info(s)
    for s in err.split('\n'):
        if s:
            logger_bg.error(s)
        
    logger_bg.info('all done.')
    
except Exception, e:
    logger_bg.error(str(e)) 