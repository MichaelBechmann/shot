# -*- coding: utf-8 -*-
#from gluon.custom_import import track_changes
#track_changes(True)
"""
This module provides all classes concerning email for the shot application.
"""

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from shotconfig import *
from gluon.dal import DAL
from shotdbutil import Events, NumberAssignment, WaitList
from formutils import getAppRequestDataTale
from gluon.html import *
from gluon import current



class EMail:
    """ 
    This is the base class of all mail objects used by the application.
    It defines an html/ plain text two part email (See: http://docs.python.org/library/email-examples.html)
    The constructor argument selects the email account to be used (refer to class EMailAccount)
    """
    
    def __init__(self, template, account_id, mass = False):
        self.account        = EMailAccount(account_id, mass)
        self.send_backup    = False
        self.subject_backup = 'backup'
        self.html           = 'default'
        self.subject        = 'default'
        self.subs           = {'PLACEHOLDER_APPENDIX': ''}
        self.attachments    = []
        
        file = open(config.shotpath + template, 'r')
        self.html = file.read()
        file.close()
   
    def _convert_html_to_text(self):
        """
        This method extracts plain text from a passed html formatted text.
        It works by simply removing the html tags with a regex.
        """
        p = re.compile('<[^>]*>')
        text = p.sub('', self.html)
        return(text)
   
    def _escape(self, text):
        '''
        This method replaces Ü,ß, etc. with the xml encodings.
        usually text.encode('ascii', 'xmlcharrefreplace') would do fine, but somehow web2py detects an exception in the encode() function ...
        '''
        sub = {'ä': '&#228;', 'Ä': '&#196;', 'ö': '&#246;', 'Ö': '&#214;', 'ü': '&#252;', 'Ü': '&#220;', 'ß': '&#223;'}
        for k,v in sub.iteritems():
            text = re.compile(k).sub(v,text)
        return text

 
    def attachpdf(self, file, name):
        """
        This method adds the specified pdf as attachment to the mail.
        Once other types shall be send this method has to be generalized (e.g., http://snippets.dzone.com/posts/show/10237)
        """
        
        a = MIMEApplication(_data = open(config.shotpath + file,"rb").read(), _subtype='pdf')
        a.add_header('Content-Disposition', 'attachment', filename = name)
        self.attachments.append(a)
        
    def add_debug_data(self):
        '''
        This method is special to web2py.
        It adds some environment information to the email for the purpose of error analysis.
        '''
        dd  = str(STRONG('session\n')) + BEAUTIFY(current.session).xml()
        dd += str(STRONG('request.env\n')) + BEAUTIFY(current.request.env).xml()
        dd += str(STRONG('request.vars\n')) + BEAUTIFY(current.request.vars).xml()
        dd += str(STRONG('request.user_agent()\n')) + BEAUTIFY(current.request.user_agent()).xml()
        self.subs['PLACEHOLDER_DEBUG_DATA'] = dd
        
    def do_substitution(self):
        '''
        This method substitutes all placeholder in the html mail text.
        '''
        for k,s in self.subs.iteritems():
            self.html = re.compile(k).sub(str(s), self.html)        
        
    def add_appendix(self, s):
        '''
        This method adds the appendix for the mail actions in the person summary.
        '''
        if s not in ('', None):
            self.subs['PLACEHOLDER_APPENDIX'] = '-------------------------------------------------------\n<br />\n' + s.replace('\n', '<br />\n')
        
    def get_preview(self):
        '''
        This method returns the completed html text as preview of the email.
        '''
        self.do_substitution()
        return self.html
    
    def send(self):
        """
        This method prepares the complete email message, establishes connection with the smtp server, and sends the ShotMail.
        """
        
        # Record the MIME types of both parts - text/plain and text/html.
        body = MIMEMultipart('alternative')
        
        # substitute placeholders
        self.do_substitution()
                   
        text = self._convert_html_to_text()
        bodytext = MIMEText(text, 'plain')
        bodytext.set_charset('utf-8') # set utf8 because of ü,ß,etc. 
        bodyhtml = MIMEText(self._escape(self.html), 'html')
        
    
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        body.attach(bodytext)
        body.attach(bodyhtml)
      
        # construct complete message with attachments
        if len(self.attachments) == 0:
            msg = body
        else:
            msg = MIMEMultipart()
            msg.attach(body)
            for a in self.attachments:
                msg.attach(a)  
        
        if config.mail.simulate_mail:
            self.receiver = config.mail.simulate_to
    
        msg['From']     = self.account.sender
        msg['To']       = self.receiver
        msg['Subject']  = self.subject
        
        #  See http://docs.python.org/library/smtplib.html
        s = smtplib.SMTP_SSL(self.account.server, self.account.port)
        s.login(self.account.login, self.account.passwd)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        
        # backup mail
        if config.email_backup_enabled and self.send_backup:
            msg.__delitem__('To')
            msg['To']       = config.mail.backup_to
            msg.__delitem__('Subject')
            msg['Subject']  = self.subject_backup
            s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()


class ShotMail(EMail):
    '''
    This class is special to the application shot. It handles common operations with the person database records.
    Note: The constructor takes a dictionary representation of a persons database record.
          This is because the database is declared only in the application's controllers, not in the general modules.
    '''
    re_waffle = re.compile('Waffel')
    
    recipe = SPAN('Wir möchten Sie bitten, den Waffelteig nach folgendem Rezept zu machen:', BR(), TABLE(*[TR(TD(x[0]), TD(x[1])) for x in config.recipe_list]))
    
    def __init__(self, db, pid, template, account_id = 'team', mass = False):
        EMail.__init__(self, template, account_id, mass)
        self.pid = pid
        self.db = db
        
        self.events = Events(self.db)
        
        self.person = self.db.person(pid)
        self.receiver = self.person['email']
        self.subs['PLACEHOLDER_DATE'] = self.events.current.date
        self.subs['PLACEHOLDER_ENROL_DATE'] = self.events.current.enrol_date
        self.subs['PLACEHOLDER_FULLNAME'] = self.person.forename + ' ' + self.person.name
        self.subs['PLACEHOLDER_DISABLE_MAIL_URL'] = config.shoturl + 'registration/disable_mail/' + str(self.person.id) + self.person.code

    def add_sale_number(self):
        '''
        This methods retrieves the persons sale number from the database and adds it to the mail.
        '''
        n = NumberAssignment(self.db, self.pid).get_number()
        if n > 0:
            self.number = str(n)
        else:
            self.number = '---'
        self.subs['PLACEHOLDER_SALE_NUMBER'] = self.number 
        
    def add_contributions(self, b_condition = False):
        '''
        This methods retrieves all contributions (the persons sale number from the database and adds it to the mail.
        '''        
        # retrieve help information
        query  = (self.db.shift.event == self.events.current.id)
        query &= (self.db.help.shift == self.db.shift.id)
        query &= (self.db.help.person == self.pid)
        
        elem = [TR(TD(r.shift.day + ', ' + r.shift.time + ', ' + r.shift.activity),
                   TD('('+r.shift.comment+')') if r.shift.comment not in [None, ''] else '')
                    for r in self.db(query).select()]
        if len(elem) > 0:
            helptext = DIV(SPAN('Sie haben sich bereit erklärt, hier zu helfen:'), BR(), TABLE(*elem))
        else:
            helptext = DIV(SPAN('Sie können keine Helferschicht übernehmen.'))
 
        self.subs['PLACEHOLDER_HELP']  = str(helptext)           
        
        
        # retrieve bring information
        query  = (self.db.donation.event == self.events.current.id)        
        query &= (self.db.bring.donation == self.db.donation.id)
        query &= (self.db.bring.person == self.pid)
        
        elem = []
        b_add_recipe = False
        for r in self.db(query).select():
            d = r.donation.item
            if self.re_waffle.search(d):
                b_add_recipe = True
            if r.bring.note != None:
                d += ' (' + r.bring.note + ')'
            elem.append(d)   
                 
        if len(elem) > 0:
            s = ''
            if b_condition:
                s = ' (sofern Sie eine Kommissionsnummer erhalten)'
            bringtext = DIV(SPAN('Sie haben sich bereit erklärt, für das Cafe folgendes zu spenden' + s + ':'), BR(), TABLE(*elem))
        else:
            bringtext = DIV(SPAN('Sie können keinen Kuchen für das Cafe mitbringen.'))

        # add waffle recipe
        if b_add_recipe:
            bringtext = DIV(bringtext, BR(), self.recipe)

        self.subs['PLACEHOLDER_BRING']  = str(bringtext) 

    def add_waitlist_position(self):
        '''
        This method calculates the current position of the person on the wait list and adds it to the mail.
        '''
        wl = WaitList(self.db)
        pos = wl.get_pos_current(self.pid)
        if pos == 0:
            pos = '???'

        self.subs['PLACEHOLDER_WAIT_POSITION'] = str(pos)
        self.subs['PLACEHOLDER_WAIT_STATUS'] = wl.status_text(self.pid)
        

class  RegistrationMail(ShotMail):
    """
    This class defines the email with the personal registration code link.
    """
    def __init__(self, db, pid):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/registration_de.html')
                    
        self.subject = 'Registrierung als Verkäufer'
        self.subs['PLACEHOLDER_REGISTRATION_URL'] = config.shoturl + 'registration/check/' + str(self.person.id) + self.person.code     



class  InvitationMail(ShotMail):
    """
    This class defines the invitation email with the personal link to the registration form.
    """
    def __init__(self, db, pid, mass = False):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/invitation_de.html', mass = mass)
                  
        self.subject = 'Einladung zum Markt'
        self.subs['PLACEHOLDER_FORM_URL'] = config.shoturl + 'registration/form/' + str(self.person.id) + self.person.code
        
        self.send_backup    = False
        self.subject_backup = 'backup invitation: ' + self.person.name + ', ' + self.person.forename

         
class NumberMail(ShotMail):
    '''
    This class defines the email with the person's sale number.
    '''
    def __init__(self, db, pid):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/sale_number_de.html')
        
        self.add_sale_number()
        self.add_contributions()
             
        self.subject = 'Ihre Kommissionsnummer'      
        self.attachpdf('static/Richtlinien.pdf', 'Richtlinien für die Annahme.pdf')    
        self.send_backup    = True
        self.subject_backup = 'backup sale number: ' + ' ' + self.number + ' ' + self.person.name + ', ' + self.person.forename

class NumberFromWaitlistMail(ShotMail):
    '''
    This class defines the email with the person's sale number. It is sent when the wait list is resolved.
    '''
    def __init__(self, db, pid, mass = False):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/sale_number_from_waitlist.html', mass = mass)
        
        self.add_sale_number()
        self.add_contributions()
             
        self.subject = 'Ihre Kommissionsnummer'      
        self.attachpdf('static/Richtlinien.pdf', 'Richtlinien für die Annahme.pdf')    
        self.send_backup    = True
        self.subject_backup = 'backup sale number: ' + ' ' + self.number + ' ' + self.person.name + ', ' + self.person.forename
        
class NumberFromWaitlistMailSuccession(ShotMail):
    '''
    This class defines the email with the person's sale number. It is sent when the wait list is resolved and the person has got a denial previously.
    '''
    def __init__(self, db, pid, mass = False):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/sale_number_from_waitlist_succession.html', mass = mass)
        
        self.add_sale_number()
        self.add_contributions()
             
        self.subject = 'Ihre Kommissionsnummer'      
        self.attachpdf('static/Richtlinien.pdf', 'Richtlinien für die Annahme.pdf')    
        self.send_backup    = True
        self.subject_backup = 'backup sale number: ' + ' ' + self.number + ' ' + self.person.name + ', ' + self.person.forename     

class WaitMail(ShotMail):
    '''
    This class defines the email for persons put on the waitlist.
    '''
    def __init__(self, db, pid):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/wait.html')
        
        self.add_contributions(b_condition = True)
        self.add_waitlist_position() # add_waitlist_position must be called after add_contributions because of the determination of the current event
        
        self.subject = 'Sie sind auf der Warteliste'       
        self.send_backup    = True
        self.subject_backup = 'backup waitlist: ' + self.person.name + ', ' + self.person.forename
        
class WaitDenialMail(ShotMail):
    '''
    This class defines the email for persons who got no number from the waitlist.
    '''
    def __init__(self, db, pid, mass = False):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/wait_denial.html', mass = mass)
        
        self.subject = 'Sie haben leider keine Nummer :('       
        self.send_backup    = False
        self.subject_backup = 'backup waitlist no number: ' + self.person.name + ', ' + self.person.forename
         
class HelperMail(ShotMail):
    '''
    This class defines the email sent to the helpers as a reminder short time before the event.
    '''
    def __init__(self, db, pid, mass = False):
        ShotMail.__init__(self, db, pid, 'static/mail_templates/helper.html', account_id = 'help', mass = mass)
        
        self.add_sale_number()
        self.add_contributions()
             
        self.subject = 'Erinnerung: Sie helfen!'       
        self.send_backup    = False
        self.subject_backup = 'helper: ' + self.person.name + ', ' + self.person.forename
        
class AppropriationRequestMail(ShotMail):
    '''
    This class defines the email sent as a confirmation when a appropriation request is received.
    '''
    def __init__(self, db, aid):
        ar_row = db.request(aid)
        ShotMail.__init__(self, db, ar_row.person, 'static/mail_templates/appropriation_request.html')
        
        self.subject = 'Ihr Antrag auf Fördermittel'       
        self.send_backup    = True
        self.subject_backup = 'Appropriation: ' + self.person.name + ', ' + self.person.forename
        
        self.subs['PLACEHOLDER_APPROPRIATION_REQUEST']  = getAppRequestDataTale(ar_row)
        
          
class ContactMail(EMail):
    '''
    This class defines the email for the SHOT contact form.
    '''
    def __init__(self, category, msg, name, email):
        EMail.__init__(self, 'static/mail_templates/contact_de.html', account_id = 'postmaster')
        self.receiver = config.mail.contactmail_to[category]
        
        self.subject = 'Kontaktanfrage von ' + name
        self.subs['PLACEHOLDER_MSG']    = msg   
        self.subs['PLACEHOLDER_NAME']   = name
        self.subs['PLACEHOLDER_EMAIL']  = email
        if category == 'tech':
            self.add_debug_data()
        else:
            self.subs['PLACEHOLDER_DEBUG_DATA'] = ''
        
class ErrorMail(EMail):
    '''
    This class defines the email which is automatically sent to the system admin in case an error has been detected.
    ''' 
    def __init__(self, msg = 'no message'):
        EMail.__init__(self, 'static/mail_templates/error.html', 'postmaster')
        self.receiver = config.mail.error_to
        self.subject  = 'Error (%s)' % config.shoturl
        self.add_debug_data()
        self.subs['PLACEHOLDER_MSG'] = msg   
        
        