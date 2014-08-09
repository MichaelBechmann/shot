# -*- coding: utf-8 -*-

# Attention! This file contains passwords! It must never be made public, e.g., via github!

# This is a tempalte file.
# Fill in the site configuration and rename it to 'siteconfig.py'

# site-dependant paths
shotpath  = '/var/web/web2py/applications/shot/'
shoturl   = 'http://secondhand-ottersweier.de/'
appname   = 'shot'

# passwords
passwd_staff = 'dummy'
passwd_admin = 'dummy'
paswd_mail   = 'dummy'

# email
email_auth = {}
email_auth['web.de']      = ('login',                 'passwd',   'sender')
email_auth['postmaster']  = ('login',                 'passwd',   'sender')
email_auth['team']        = ('login',                 'passwd',   'sender')
email_auth['help']        = ('login',                 'passwd',   'sender')

email_simulate_to     = 'dummy'
email_backup_to       = 'dummy'
email_error_to        = 'dummy'

email_contactmail_to  = {'general':   'dummy',
                         'help':      'dummy',
                         'tech':      'dummy'
                         }

# database connection and backup
db_connection_string = 'mysql://__user__:__password__@__host__/__database__'
db_backup_command = 'mysqldump --user=  --password= shot ...'
