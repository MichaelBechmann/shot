# -*- coding: utf-8 -*-

"""
This module provides all classes concerning email for the shot application.
"""

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from shotconfig import *




class EMail:
    """ 
    This is the base class of all mail objects used by the application.
    It defines an html/ plain text two part email (See: http://docs.python.org/library/email-examples.html)
    The constructor argument selects the email account to be used (refer to class EMailAccount)
    """
    def __init__(self, account_id):
        self.account        = EMailAccount(account_id)
        self.send_backup    = False
        self.subject_backup = 'backup'
        self.html           = 'default'
        self.subject        = 'default'
        self.receiver       = 'michael_bechmann@yahoo.de'
        self.subs           = {}
        self.attachments    = []
        
   
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
   
    def set_html(self, template):
        """
        This method is used to set the html content for the ShotMail.
            first argument: full path to the html email template file to be used.
        """
        file = open(template, 'r')
        self.html = file.read()
        file.close()
        for k,s in self.subs.iteritems():
            self.html = re.compile(k).sub(s, self.html)
 
    def attachpdf(self, file, name):
        """
        This method adds the specified pdf as attachment to the mail.
        Once other types shall be send this method has to be generalized (e.g., http://snippets.dzone.com/posts/show/10237)
        """
        
        a = MIMEApplication(_data = open(file,"rb").read(), _subtype='pdf')
        a.add_header('Content-Disposition', 'attachment', filename = name)
        self.attachments.append(a)       
        
        
    
    def send(self):
        """
        This method prepares the complete email message, establishes connection with the smtp server, and sends the ShotMail.
        """
        
        # Record the MIME types of both parts - text/plain and text/html.
        body = MIMEMultipart('alternative')
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
        
    
        msg['From']     = self.account.sender
        msg['To']       = self.receiver
        msg['Subject']  = self.subject
        
        #  See http://docs.python.org/library/smtplib.html
        s = smtplib.SMTP(self.account.server, self.account.port)
        s.login(self.account.login, self.account.passwd)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        
        # backup mail
        if self.send_backup:
            msg.__delitem__('To')
            msg['To']       = config.backup_to
            msg.__delitem__('Subject')
            msg['Subject']  = self.subject_backup
            s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()


class ShotMail(EMail):
    '''
    This class is special to the application shot. It handles common operations with the vendor database records.
    Note: The constructor takes a dictionary representation of a vendors database record.
          This is because the database is declared only in the application's controllers, not in the general modules.
    '''
    
    def __init__(self, account_id, vendor):
        EMail.__init__(self, account_id)
        self.receiver = vendor['email']
        self.subs['PLACEHOLDER_FULLNAME'] = vendor['forename'] + ' ' + vendor['name']

class  RegistrationMail(ShotMail):
    """
    This class defines the email with the vendor registration link.
    """
    def __init__(self, vendor):
        ShotMail.__init__(self, 'shot_staff', vendor)            
        self.subject = config.regmail.subject
        self.subs['PLACEHOLDER_REGISTRATION_URL'] = config.regmail.linkbase + str(vendor['id']) + vendor['code']
        self.set_html(config.regmail.template)       

class  InvitationMail(ShotMail):
    """
    This class defines the invitation email with the personal link to the registration form.
    """
    def __init__(self, vendor):
        ShotMail.__init__(self, 'shot_staff', vendor)            
        self.subject = config.invmail.subject
        self.subs['PLACEHOLDER_FORM_URL'] = config.invmail.linkbase + str(vendor['id']) + vendor['code']
        self.set_html(config.invmail.template)
        
        self.send_backup    = True
        self.subject_backup = 'backup invitation: ' + vendor['name'] + ', ' + vendor['forename']

class  WaitlistMail(ShotMail):
    """
    This class defines the mail informing that a vendor is on the waitlist.
    """
    def __init__(self, vendor):
        ShotMail.__init__(self, 'shot_staff', vendor)            
        self.subject = 'Sie sind auf der Warteliste!'
        self.set_html(siteconfig.shotpath + 'static/mail_templates/waitlist_de.html')
        
        self.send_backup    = True
        self.subject_backup = 'backup waitlist: ' + vendor['name'] + ', ' + vendor['forename']

class  UnzhurstMail(ShotMail):
    """
    special one time mail
    """
    def __init__(self, vendor):
        ShotMail.__init__(self, 'shot_staff', vendor)            
        self.subject = 'Information'
        self.set_html(siteconfig.shotpath + 'static/mail_templates/unzhurst_de.html')
        
        self.send_backup    = True
        self.subject_backup = 'backup unzhurst: ' + vendor['name'] + ', ' + vendor['forename']
              
class NumberMail(ShotMail):
    '''
    This class defines the email with the vendor's sale number.
    '''
    def __init__(self, vendor, number, contributions):
        '''
        vendor is a database record containing name and email
        number and contributions are strings!
        '''
        ShotMail.__init__(self, 'shot_staff', vendor)
        self.subject = config.numbermail.subject       
        self.subs['PLACEHOLDER_SALE_NUMBER']    = number              
        self.subs['PLACEHOLDER_CONTRIBUTIONS']  = contributions
        self.set_html(config.numbermail.template)
        self.attachpdf(config.numbermail.attachment, config.numbermail.attachmentname)    
        
        self.send_backup    = True
        self.subject_backup = 'backup sale number: ' + ' ' + number + ' ' + vendor.name + ', ' + vendor.forename
        
        
        
          
class ContactMail(EMail):
    '''
    This class defines the email for the SHOT contact form.
    '''
    def __init__(self, category, msg, name, email):
        EMail.__init__(self, 'shot_staff')
        self.receiver = config.contactmail.to[category]
        self.subject = config.contactmail.subject + ' von ' + name
        self.subs['PLACEHOLDER_MSG']    = msg   
        self.subs['PLACEHOLDER_NAME']   = name
        self.subs['PLACEHOLDER_EMAIL']  = email     
        self.set_html(config.contactmail.template) 
