# -*- coding: utf-8 -*-
#from gluon.custom_import import track_changes
#track_changes(True)

import re
import random
import string
import datetime
from shotconfig import *
from gluon.dal import DAL, Rows
from gluon.contrib.pymysql import IntegrityError


def extractTableFields(table, data):
    '''
    This function returns a dictionary which contains only those entries from the dictionary "data" which are fields of "table"
    '''
    data_red = {}
    for k, v in data.iteritems():
        if k in table.fields:
            data_red[k] = v
    
    return data_red


class Log:
    """
    This class provides auxiliary functions for the logging of database modifications
    """
    def __init__(self, db):
        self.db   = db
        self.now  = datetime.datetime.now()
        
    def person(self, pid, s):
        
        log = self.db.person[pid].log
        
        if (log == None):
            log = ''
        else:
            log += ' --> '
            
        log += self.now.strftime("%Y-%m-%d %H:%M") + ': ' + s
        
        self.db(self.db.person.id == pid).update(log = log)

class Events():
    '''
    This class provides information about the events.
    '''
    def __init__(self, db):
        self.db = db
        q  = db.event.active == True
        q &= db.event.type == db.event_type.id
        self.current = db(q).select().last()
        self.current.form_label = self._form_label(self.current)

    def get_all(self):
        '''
        This method is used for the event filter form in the view table pages
        '''
        q  = self.db.event.id > 0
        q &= self.db.event.type == self.db.event_type.id
        
        self.all = {self._form_label(r):r.event.id  for r in self.db(q).select()}
        return self.all
    
    def _form_label(self, e):
        return '%s, %s' % (e.event_type.label,e.event.date)
    
        
    def get_visible(self):
        '''
        This method returns a rows object of all events for which the visible flag is set.
        '''
        return self.db(self.db.event.visible == True).select(self.db.event.label, self.db.event.date, self.db.event.time, self.db.event.enrol_date)
        
    def previous_id(self, eid = 0):
        '''
        This method returns the id of the previous event OF THE SAME TYPE.
        The argument is the event id of the event for which the previous event shall be determined.
        If no argument is given, the current event is assumed.
        
        Note: The previous event id is not necessarily (current event id - 1) because intermediate events could have been deleted.
        Empty intermediate events (events without connected sales or helps etc.) are not sorted out and should be removed from the database.
        '''
        if eid == 0:
            eid = self.current.event.id
            
        t = self.db.event[eid].type
            
        query  = self.db.event.type == t
        query &= self.db.event.id < eid
        old = [e.id for e in self.db(query).select()]
        old.append(0) # always return something
        return max(old)
    
    def get_current_announcement(self, b_include_time = False):
        '''
        This method returns an announcement string with label, date, and optionally time of the current event.
        '''
        s = '%s am %s' % (self.current.event.label, self.current.event.date)
        if b_include_time:
            s += ', %s' % self.current.event.time
            
        return s
    

class Ident():
    '''
    This class provides methods for the generation of identification codes and their verification.
    The identification link shall not display the variables used. Instead a single identification string
    comprising the database id and the code shall be used.
    '''
    
    def __init__(self, db = None, linkcode = None):

        self.db = db
        self.linkcode = linkcode
        self.id = 0
        self.b_verified = False
        self.person = None    
        
        
        if self.linkcode != None:
            self._verify()
        else:
            self._getcode() 


    def _getcode(self):
        '''
        This method generates a random identification code.
        The code shall start with a first letter, not a digit.
        '''
        char = string.ascii_lowercase + string.digits
        self.code = random.choice(string.ascii_lowercase) + ''.join([random.choice(char) for i in range(12)])
        
        
    def _verify(self):
        '''
        This method checks if the code matches the data base entry referenced by the id.
        If so, the successful code verification is stored in the data base.
        '''
        p = re.compile('([0-9]+)')
        m = p.match(self.linkcode)
        if(m):
            self.id = int(m.group(0))
            c = self.linkcode.replace(m.group(0),'',1)
            
        self.b_verified = False
        self.person = self.db.person(self.id)
        if(self.person != None):            
            if(c == self.person.code):
                currentevent = Events(self.db).current.event.id
                self.db(self.db.person.id == self.id).update(verified = currentevent)
                self.person['verified'] = currentevent # This dictionary must be consistent with the db, otherwise the old current event will be re-written to the db!
                self.b_verified = True

class PersonEntry():
    '''
    This class provides methods to insert and update the records of the table "person".
    '''
    def __init__(self, db, data):
        '''
        "data" is a reference to a dictionary containing the the form/database fields of the person record.
        Note that data may contain more fields (from forms combining several tables).
        '''
        self.db = db
        # construct a dictionary containing only the fields of the table "person"
        self.data = extractTableFields(db.person, data)
            
        # self.data must not contain an id!
        # Otherwise an error "IntegrityError: PRIMARY KEY must be unique" will occur at the insert and update operations
        # if this id is different from self.id.
        # The only relevant id here is self.id!
        if self.data.has_key('id'):
            del self.data['id']
            
        self.id       = None
        self.exists   = False
        self.verified = False
        
        # check if person is already known to the database      
        q  = db.person.name     == self.data['name']
        q &= db.person.forename == self.data['forename']
        q &= db.person.email    == self.data['email']
        rows = db(q).select()

        if (len(rows) > 0):
            self.id     = rows[0].id
            self.exists = True
            
            # Check if email address has already been verified.
            ev = rows[0].verified # event number of verification
            if (ev != None and ev > 0):
                self.verified = True
                
    def insert(self):
        '''
        Creates a new database record for the person.
        '''
        self.data['code'] = Ident().code  
        self.id = self.db.person.insert(**self.data)
        Log(self.db).person(self.id, 'initial')

        
    def update(self):
        '''
        Updates an existing database record for the person.
        '''
        # construct string with the old values of the fields to be modified
        oldperson = self.db.person(self.id)
        s = 'update fields: '
        sep = ''
        for f, v in self.data.iteritems():
            op =oldperson[f] 
            if op != v:
                s +=sep + f + ' (' + str(op) + ')'
                sep = ', '
        
        self.db(self.db.person.id == self.id).update(**self.data)
        Log(self.db).person(self.id, s)
        
    def set_mail_enabled(self):
        self.data['mail_enabled'] = True
        
    def disable_mail(self):
        '''
        This method sets the flag in the person entry to disable round mails.
        '''
        self.data['mail_enabled'] = False
        self.update()


class Numbers():
    '''
    This class provides methods to retrieve information on the sale numbers from the database.
    The results are evaluated for the given event.
    
    arguments: eid - event database id
    '''
    def __init__(self, db, eid):  
        self.db = db
        self.eid    = eid
        self.event  = self.db.event[eid]
        
    def _s_assigned(self):
        '''
        This method returns a set (not a list) of all assigned numbers
        '''
        q = self.db.sale.event == self.eid
        s = set([r.number for r in self.db(q).select()])
        
        # if there should be a sale entry without number
        if None in s:
            s.remove(None)
        return s

    def assigned(self):
        '''
        Create a list of all sale numbers already assigned for the given event.
        '''
        l = list(self._s_assigned())
        l.sort()
        return l
    

    def _decode(self, s):
        '''
        This method creates a list of integers from the string representation of number ranges.
        '''
        l = map(int, re.compile('\d+').findall(s))
            
        # now check if the length of the list is even
        # if not => remove last element
        if len(l) & 1:
            l.pop()
            
        # create a list of the partial ranges 
        ll = [range(l[i], l[i+1] + 1) for i in range(0, len(l), 2)]        
        
        # flatten the list of lists
        # see: http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        return sum(ll, [])
    
    
    def config(self):
        '''
        This method returns a list of all numbers available to the public
        '''
        return self._decode(self.event.number_ranges)

    
    def free(self):
        '''
        This method returns a list of the free numbers.
        '''        
        c = self.config()
        l = list(set(c) - self._s_assigned())       
        # sort as the set is hash like
        l.sort()
        return l
        
    def number_of_available(self):
        '''
        This method returns the number of sale numbers still available.
        '''
        n = len(self.free())
        if self.event.numbers_limit > 0:
            # number limit is set
            n = min(n, self.event.numbers_limit - len(self.assigned()))
        return n
    
    def b_numbers_available(self):
        '''
        This method returns the info whether or not there are still numbers available.
        '''
        if self.number_of_available() > 0:
            b = True
        else:
            b = False
        return b
    
    def helper(self, eid = 0):
        '''
        This method returns a list of the sale numbers of all helpers at the given event.
        If no event id is passed the default event id of the object is used.
        '''
        if eid == 0:
            eid = self.eid
        query  = (self.db.shift.event == eid)
        query &= (self.db.help.shift == self.db.shift.id)
        query &= (self.db.help.person == self.db.person.id)
        query &= (self.db.person.id == self.db.sale.person)
        query &= (self.db.sale.event == eid)
        
        l = [row.number for row in self.db(query).select(self.db.sale.number)]
        
        return l
    
    
class NumberAssignment():
    '''
    This class collects everything needed to determine and to assign sale numbers.
    All operations are generally done for the current event.
    '''
    def __init__(self, db, pid):
        '''
        pid is the person id
        '''
        self.db = db
        self.pid = pid
        self.e = Events(self.db)      
                 

    def get_old_number(self):
        '''
        This method tries to identify the most recent sale number the person had
        '''
        n = 0
        query  = (self.db.sale.event == self.db.event.id)
        query &= (self.db.sale.person == self.pid)
        rows = self.db(query).select(self.db.event.id, self.db.sale.number)
        if rows:
            r = rows.sort(lambda row: row.event.id).last()
            n = r.sale.number
        
        return n
    
    def determine_number(self):
        '''
        This method determines the sale number based on the persons data.
        If no valid sale number could be determined this function returns 0.
        
        For the determination of the sale number the following rules are applied:
        0) If there are no numbers available any more => assign 0
        1) If the person helped at the previous event => assign old number (last number of this person, not necessarily from the previous event)
        2) If the old number of the person is still free and not a number of a helper from the previous event => assign old number
        3) If person has no old number or the old number is not free any more => assign one of the free numbers
        4) Assign numbers of helpers at the previous event not before all other free numbers (block previous helper numbers).
        '''
        
        self.numbers = Numbers(self.db, self.e.current.event.id)
        if self.numbers.b_numbers_available() == False:
            return 0
        
        self.previousevent = self.e.previous_id()
        
        # check whether or not the person helped at the previous event
        query  = (self.db.shift.event == self.previousevent)
        query &= (self.db.help.shift == self.db.shift.id)
        query &= (self.db.help.person == self.pid)
        if len(self.db(query).select()) > 0:
            self.b_helped_previous_event = True
        else:
            self.b_helped_previous_event = False
        
        # get list of potential (= free) sale numbers
        self.free = self.numbers.free()

        on = self.get_old_number()
        self.on = on
        
        sn = 0
        if (on > 0 and on not in self.numbers.assigned()):
            if (self.b_helped_previous_event):
                sn = on
            else:
                ohn = self.numbers.helper(self.previousevent)
                if on not in ohn:
                    sn = on

        if sn == 0:
            # get all free numbers which shall not be blocked for previous helpers
            sprio = set(self.free) - set(self.numbers.helper(self.previousevent))
            if len(sprio) > 0:
                sn = min(sprio)
            elif len(self.free) > 0:
                sn = self.free[-1]
        
        return sn
    
    def _get_sale(self, eid = 0):
        '''
        This method returns the sale row object (not the sale number!) of the person for a given event. If no event is passed the current event is assumed
        If the person does not have a number 0 is returned
        '''
        if eid == 0:
            eid = self.e.current.event.id
        query  = (self.db.sale.event == eid)
        query &= (self.db.sale.person == self.pid)
        rows = self.db(query).select()
        if len(rows) > 0:
            sale = rows.last()
        else:
            sale = None
        return sale
    
    
    def get_number(self, eid = 0):
        '''
        This method returns person's sale number for the given event. If no event is passed the current event is assumed
        If the person does not have a number 0 is returned
        '''
        sale = self._get_sale(eid)
        if sale != None:
            n = sale.number
        else:
            n = 0
        
        return n
    
    def assign_number(self):
        '''
        This method determines a suitable sale number and creates a sale entry in the database.
        If the person already has a sale number for the current event then a new sale entry must not be created!
        If successful the sale number is returned and 0 otherwise.
        '''
        sale = self._get_sale()
        if sale != None:
            sid = sale.id
            sn = sale.number
        else:
            sid = 0
            
        if sid == 0:
            while True:
                try:
                    sn = self.determine_number()
                    if sn > 0:
                        # add sale entry    
                        sid = self.db.sale.insert(event = self.e.current.event.id, person = self.pid, number = sn) 
                        log = 'sale # ' + str(sid) + '/ number ' + str(sn) + ' added'
                    else:
                        log = 'no sale added: no more sale numbers available'
                except IntegrityError:
                    # Apparently the determined sale number has just been taken by somebody else.
                    # The database connection must be refreshed in order to get updated information about the already assigned sale numbers.
                    self.db.commit()
                else:
                    break
        else:
            log = 'no sale added: sale # ' + str(sid) + '/ number ' + str(sn) + ' already assigned!'
        
        # add log info to person
        Log(self.db).person(self.pid, log)

        return sid

            
class Help():
    '''
    This class contains code concerning the Helper lists.
    '''
    def __init__(self, db, eid = None):
        self.db = db
        if eid == None:
            self.eid = Events(db).current.event.id
        else:
            self.eid = eid
        
    def get_helper_list(self):
        
        # get all persons which help
        query  = (self.db.help.person == self.db.person.id)
        query &= (self.db.help.shift  == self.db.shift.id)
        query &= (self.db.shift.event == self.eid)
        
        rows = self.db(query).select(self.db.person.id, self.db.help.person, self.db.person.name, self.db.person.forename)  
        
        # remove multiple occurrence of helping persons
        # For some reason the db argument is required for SQLTABLE to work properly.
        rows_compact = Rows(self.db)
        # For some reason the records must be cleared (otherwise the helperlist will grow each time this class is called!).
        rows_compact.records = []
        
        person_list = []
        for row in rows:
            if row.person.id not in person_list:
                rows_compact.records.append(row)
                person_list.append(row.person.id)
                
        return rows_compact
    
    
    def determine_number_of_shifts(self):
        '''
        This method determines the current numbers of shifts:
            self.n_open  - number of still open shifts, that is, number of still needed helpers
            self.n_taken - number of shifts already taken by some helper (not equal to the number of helpers as one helper may have taken more than one shift)
            self.n_total - total number of configured shifts
        '''
        query = self.db.shift.event == self.eid
        rows = self.db(query).select()
        self.n_total = 0
        self.n_taken = 0
        self.n_open  = 0
        for row in rows:
            self.n_total += row.target_number
            self.n_taken += row.actual_number
        self.n_open = self.n_total - self.n_taken
        
        
class WaitList():
    '''
    This class collects code for the resolution of the wait list.
    '''
    def __init__(self, db):
        self._current_pos = {}
        self.db = db
        self.eid = Events(db).current.event.id
    
        # get all wait list entries from the current event
        self.query_wait  = (db.wait.event == self.eid)
        self.query_wait &= (db.wait.person == db.person.id)

        self.rows_all = db(self.query_wait).select(db.wait.id, db.wait.person, db.wait.denial_sent)
        
        # get all wait list entries which already have a sale assigned
        query_sale  = self.query_wait
        query_sale &= (db.person.id == db.wait.person)
        query_sale &= (db.person.id == db.sale.person)
        query_sale &= (db.sale.event == self.eid)
        
        lsale = []
        for row in db(query_sale).select(db.wait.id):
            lsale.append(row.id)
            
        # create auxiliary rows object containing all wait list entries without sale
        self.rows_wait = self.rows_all.find(lambda row: row.id not in lsale)
        
        
    def _get_sorted_all(self):
        '''
        This method returns a rows object containing all persons who have no sale yet for the current event.
        All persons who help at the current event are sorted at the beginning of the list.
        '''
        # get all wait list entries which additionally are linked to shifts
        query_help  = self.query_wait
        query_help &= (self.db.person.id == self.db.wait.person)
        query_help &= (self.db.person.id == self.db.help.person)
        query_help &= (self.db.shift.id  == self.db.help.shift)
        query_help &= (self.db.shift.event == self.eid)
        
        
        lhelp = []
        for row in self.db(query_help).select(self.db.wait.id):
            lhelp.append(row.id)
        
        if len(lhelp) > 0:
            offset = max(lhelp)
        else:
            offset = 0

        # sort helpers in front
        # Note: sort method of rows object does not operate in place!
        return(self.rows_wait.sort(lambda row: row.id if row.id in lhelp else row.id + offset))
        

    def get_sorted(self):
        
        rows = self._get_sorted_all()
        
        # return only as many rows as numbers are available
        # negative numbers in slices do not work
        return rows[:max([0, Numbers(self.db, self.eid).number_of_available()])]
        
    def get_denials(self):
        '''
        This method returns a rows object containing all persons who have no sale yet for the current event
        and have got no denial mail so far.
        '''
        return self.rows_wait.find(lambda row: row.denial_sent != True)
    
    def get_pos_current(self, pid):
        '''
        Returns the current position on the wait list for person pid (all sales and helps taken into account).
        '''
        # check if position has been determined already
        if self._current_pos.has_key(pid):
            return self._current_pos[pid]
        
        pos = 0
        count = 0
        if pid != None:
            for row in self._get_sorted_all():
                count += 1
                if row.person.id == pid:
                    pos = count
                    break
        
        self._current_pos[pid] = pos
        return pos
    
    def length(self):
        '''
        This method returns the current length of the real wait list,
        that is, the number of persons on the wait list with no sale number yet.
        '''
        return len(self.rows_wait)
    
    def status_text(self, pid):
        '''
        This method analyses the current position of a person on the wait list and the still open shifts.
        It returns a status corresponding message for the sale form and e-mails.
        '''
        if pid != None and NumberAssignment(self.db, pid).get_number(self.eid) > 0:
            return 'Sie haben bereits eine Kommissionsnummer für den kommenden Markt.'
        
        h = Help(self.db, self.eid)
        h.determine_number_of_shifts()
        
        # determine or prognost position on the wait list
        pos = self.get_pos_current(pid)
        if pos == 0:
            pos = self.length() + 1
        
        x  = Numbers(self.db, self.eid).number_of_available() - pos - h.n_open
        
        if x > 20:
            msg = 'Es sind noch genügend Kommissionsnummern frei. Sie werden sicher eine Nummer erhalten, sobald unsere Warteliste aufgelöst wird.'
        elif x >= 0:
            msg = 'Es sind nur noch wenige Kommissionsnummern frei. Da wir Helfer bevorzugt behandeln, ist unsicher, ob Sie über die Warteliste eine Nummer erhalten werden.'
        elif x >= -15:
            msg = 'Es sind derzeit leider keine Kommissionsnummern mehr frei. Sollten Nummern zurückgegeben werden, könnten Sie evtl. noch eine über die Warteliste erhalten.'
        else:
            msg = 'Es sind leider keine Kommissionsnummern mehr frei. Unsere Warteliste ist auch schon so lang, daß Sie sicher keine Nummer mehr erhalten werden.'
        
        return msg
    
            
class WaitListPos():
    '''
    This class contains code to calculate the position of a person on the wait list of a given event.
    ''' 
    def __init__(self, db, pid, eid = None):
        
        if eid == None:
            eid = Events(db).current.event.id
            
        query = (db.wait.event == eid)
        rows = db(query).select()
            
        # determine wait id of the person
        self.pos = 0
        if len(rows) > 0:
            prow = rows.find(lambda r: r.person == pid).last()
            if prow != None:
                # determine how many ids are lower
                self.pos = len([r for r in rows if prow.id >= r.id])

            
class Person():
    '''
    This class provides methods related to the person summary.
    '''
    def __init__(self, db, pid):
        self.record = db(db.person.id == pid).select().first()
        
        self.data = {}
        e = Events(db)
        for label, eid in e.get_all().iteritems():
            self.data[eid] = {'label': label, 'current': False, 'numbers': [], 'wait entries': [], 'shifts': [], 'donations': [], 'messages': []}
            if eid == e.current.event.id:
                self.data[eid]['current'] = True 
        
        # retrieve all sale numbers
        query =  (db.event.id == db.sale.event)
        query &= (db.person.id == db.sale.person)
        query &= (db.person.id == pid)
        
        for row in db(query).select(db.event.id, db.sale.id, db.sale.number):
            self.data[row.event.id]['numbers'].append((row.sale.id, row.sale.number))
        
        # retrieve all entries in waitlist
        query =  (db.event.id == db.wait.event)
        query &= (db.person.id == db.wait.person)
        query &= (db.person.id == pid)
        
        for row in db(query).select():
            self.data[row.event.id]['wait entries'].append((row.wait.id, 'enrollment position: %d' %(WaitListPos(db, pid, row.event.id).pos)))
            
            if row.event.id ==e.current.event.id:
                current_pos = WaitList(db).get_pos_current(pid)
                if current_pos > 0:
                    self.data[e.current.event.id]['wait entries'].append((row.wait.id, 'current wait position: %d' % current_pos))
                    
                if row.wait.denial_sent:
                    self.data[e.current.event.id]['wait entries'].append((row.wait.id, 'denial mail sent'))


        # retrieve all helps
        query =  (db.event.id == db.shift.event)
        query &= (db.help.shift == db.shift.id)
        query &= (db.help.person == db.person.id)
        query &= (db.person.id == pid)
        
        for row in db(query).select(db.event.id, db.help.id, db.shift.activity, db.shift.day, db.shift.time):
            self.data[row.event.id]['shifts'].append((row.help.id, '%(shift.activity)s, %(shift.day)s, %(shift.time)s' % row))       
        
        # retrieve all brings
        query =  (db.event.id == db.donation.event)
        query &= (db.bring.donation == db.donation.id)
        query &= (db.bring.person == db.person.id)
        query &= (db.person.id == pid)
        
        for row in db(query).select(db.event.id, db.bring.id, db.donation.item, db.bring.note):
            eid = row.event.id
            s = row.donation.item
            if row.bring.note not in ('', None):
                s = s + ' (' + row.bring.note + ')'
            self.data[eid]['donations'].append((row.bring.id, s))      
        
        # retrieve messages
        query =  (db.event.id == db.message.event)
        query &= (db.person.id == db.message.person)
        query &= (db.person.id == pid)
        
        for row in db(query).select(db.event.id, db.message.id, db.message.text):
            eid = row.event.id
            self.data[eid]['messages'].append((row.message.id, '%(message.text)s' % row))
            
        #  create sorted list
        self.eventdata = []
        for eid in sorted(self.data.keys(), reverse=True):
            self.eventdata.append(self.data[eid])
            

class  AppropriationRequestEntry():
    '''
    This class provides the database interface for the table request.
    '''
    def __init__(self, db, data, pid):
        '''
        "data" is a reference to a dictionary containing the the form/database fields of the request record.
        Note that data may contain more fields (from forms combining several tables).
        '''
        # construct a dictionary containing only the fields of the table "request"
        self.data = extractTableFields(db.request, data)

        # set the relation to the table person
        self.data['person'] = pid
        
        # add time stamp
        self.data['date_of_receipt'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # insert record
        self.aid = db.request.insert(**self.data)
        Log(db).person(pid, 'appropriation request added')


class User():
    '''
    This class provides methods related to the team member user accounts.
    '''
    def __init__(self, db, uid):
        self.db = db
        self.uid = uid
        
    def get_groups(self):
        query  = self.db.auth_membership.user_id == self.uid
        query &= self.db.auth_membership.group_id == self.db.auth_group.id
        
        return self.db(query).select()
        
        