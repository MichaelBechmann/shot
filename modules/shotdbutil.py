# -*- coding: utf-8 -*-
#from gluon.custom_import import track_changes
#track_changes(True)

import re
import random
import string
import datetime
from shotconfig import *
from gluon.dal import DAL
from gluon.dal.objects import Rows
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


def removeDuplicates(db, rows):
    '''
    This function removes duplicate ids from the rows objects.
    '''
    # For some reason the db argument is required for SQLTABLE to work properly.
    rows_compact = Rows(db)
    rows_compact.records = []
    id_list = []
    for row in rows:
        if row.id not in id_list:
            rows_compact.records.append(row)
            id_list.append(row.id)
                    
    return rows_compact


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
        
        # determine the current event
        q  = db.event.active == True
        q_join_type = db.event.type == db.event_type.id
        q &= q_join_type
        # if there are multiple events active => select the last one to be the current event
        self.current = db(q).select(orderby=db.event.id).last()
        
        if self.current == None:
            # in case of an configuration error (no active event) => take first event to not damage too much
            self.current = db(q_join_type).select().first()
        
        self.current.form_label = self._form_label(self.current)

    def get_all(self):
        '''
        This method is used for event filter forms, e.g., in the view table pages
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
    
    def number_of_assigned(self):
        '''
        This method returns the number of sale numbers still already assigned.
        '''
        return len(self.assigned())

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
        This method returns a set of the free numbers.
        '''        
        c = self.config()
        s = set(c) - self._s_assigned()     

        return s
        
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
        This method returns a set of the sale numbers of all helpers at the given event.
        If no event id is passed the default event id of the object is used.
        '''
        if eid == 0:
            eid = self.eid
        query  = (self.db.shift.event == eid)
        query &= (self.db.help.shift == self.db.shift.id)
        query &= (self.db.help.person == self.db.person.id)
        query &= (self.db.person.id == self.db.sale.person)
        query &= (self.db.sale.event == eid)
        
        s = set([row.number for row in self.db(query).select(self.db.sale.number)])
        
        return s
    
    
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
                 

    def get_old_number(self, pid = None):
        '''
        This method tries to identify the most recent sale number the person had.
        Only events of the same type as the current event are considered!
        '''
        if not pid:
            pid = self.pid
        
        n = 0
        query  = (self.db.event.type == self.e.current.event_type.id)
        query &= (self.db.sale.event == self.db.event.id)
        query &= (self.db.sale.person == pid)
        rows = self.db(query).select(self.db.event.id, self.db.sale.number)
        if rows:
            r = rows.sort(lambda row: row.event.id).last()
            n = r.sale.number
        
        return n
    
    def get_old_numbers_of_wait_list_persons(self):
        '''
        This method returns a sorted list containing the old numbers of all persons of the wait list.
        The list is in the same order as the wait list would be resolved (helpers first)
        '''
        l = []
        rows = WaitList(self.db).get_sorted_all()
        for row in rows:
            n = self.get_old_number(int(row.person.id))
            if n != 0:
                l.append(n)

        return l
    
    
    def determine_number(self):
        '''
        This method determines the sale number based on the persons data.
        If no valid sale number could be determined this function returns 0.
        
        old number: last number of this person, not necessarily from the previous event
        free numbers: numbers in the configured number ranges for the event which are not yet assigned
        
        note possible conflict: Who helped at the previous event will get ones old number even if one did not have a number at the previous event.
        
        For the determination of the sale number the following rules are applied:
        0) If there are no numbers available any more => assign 0
        1) If the old number of the person is not yet assigned and the person helped at the previous event => assign old number
           It is possible that this old number is not in the range of configured numbers!
        2) If the old number of the person is not yet assigned and not a number of a helper from the previous event => assign old number
        3) If person has no old number or the old number is already assigned => assign one of the free numbers
        4) Assign numbers of helpers at the previous event not before all other free numbers (block previous helper numbers).
        5) Assign old numbers of persons on the current wait list not before all other free numbers; then in reverse wait list order
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
        
        sn = 0
        if (on > 0 and on not in self.numbers.assigned()):
            if (self.b_helped_previous_event):
                sn = on
            else:
                if on not in self.numbers.helper(self.previousevent):
                    sn = on

        if sn == 0:
            # get all free numbers which shall not be blocked for previous helpers
            s_ohn_removed = self.free - self.numbers.helper(self.previousevent)
            if len(s_ohn_removed) > 0:
                s_current = s_ohn_removed
            else:
                s_current = self.free
                
            # take into account old numbers of persons on the wait list
            onwl = self.get_old_numbers_of_wait_list_persons()
            s_onwl_removed = s_current - set(onwl)
            if len(s_onwl_removed) > 0:
                sn = min(s_onwl_removed)
            else:
                # Set operations cannot be used here anymore because the order old numbers of the wait list persons has to be taken into account!
                for n in reversed(onwl):
                    if n in s_current:
                        sn = n
                        break
        
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

            
class Contributions():
    '''
    This class contains code concerning the helpers and bringers.
    '''
    def __init__(self, db, eid = None):
        self.db = db
        if eid == None:
            self.eid = Events(db).current.event.id
        else:
            self.eid = eid
            
        self.rows_shifts = None
        self.rows_donations = None
            
    def get_shifts(self):
        '''
        This method returns a rows object off all shifts for the selected event.
        '''
        if self.rows_shifts == None:
            self.rows_shifts = self.db(self.db.shift.event == self.eid).select()
        return self.rows_shifts
    
    def get_donations(self):
        '''
        This method returns a rows object off all donations for the selected event.
        '''
        if self.rows_donations == None:
            self.rows_donations = self.db(self.db.donation.event == self.eid).select()
        return self.rows_donations


    def get_helper_list(self):
        '''
        This method returns all persons who are assigned to ANY shift of the event/all helping persons.
        '''
        query  = (self.db.help.person == self.db.person.id)
        query &= (self.db.help.shift  == self.db.shift.id)
        query &= (self.db.shift.event == self.eid)
        
        rows = self.db(query).select(self.db.person.id, self.db.person.name, self.db.person.forename)

        return removeDuplicates(self.db, rows)
    
    def get_helper_list_for_shift(self, sid):
        '''
        This method returns all persons who are assigned to the one shift specified by the parameter.
        The rows are sorted by the persons last names.
        '''
        query  = (self.db.help.person == self.db.person.id)
        query &= (self.db.help.shift  == sid)
        
        rows = self.db(query).select(self.db.person.id, self.db.person.name, self.db.person.forename, self.db.person.place, orderby = self.db.person.name)

        return rows


    def get_bringer_list(self):
        
        # get all persons who bring something
        query  = (self.db.bring.person   == self.db.person.id)
        query &= (self.db.bring.donation == self.db.donation.id)
        query &= (self.db.donation.event == self.eid)
        
        rows = self.db(query).select(self.db.person.id, self.db.person.name, self.db.person.forename)

        return removeDuplicates(self.db, rows)
    
    
    def get_bringer_list_for_donation(self, did):
        '''
        This method returns all persons who are assigned to the one donation specified by the parameter.
        The notes are included.
        The rows are sorted by the persons last names.
        '''
        query  = (self.db.bring.person == self.db.person.id)
        query &= (self.db.bring.donation  == did)
        
        rows = self.db(query).select(self.db.bring.note, self.db.person.id, self.db.person.name, self.db.person.forename, orderby = self.db.person.name)

        return rows
    
    def get_notes_list_for_donation(self, did):
        '''
        This method returns a sorted list of strings containing all DIFFERENT notes for the given donation identified by did.
        Format of strings: note (nx)
        '''
        notes = {}
        for bring in self.db(self.db.bring.donation == did).select():
            if bring.note != None:
                # add note if new, increment counter otherwise
                if bring.note in notes:
                    notes[bring.note] += 1
                elif bring.note:
                    notes[bring.note] = 1
        
        notes_list = []
        
        
        #aux = [(k, v) for k, v in notes.iteritems()]
        aux = notes.items()
        aux.sort(key = lambda x: '%d%s'%(1000 - x[1], x[0]))
        for k, v in aux:
            s = k
            if v > 1:
                s += ' (%dx)' % v
            notes_list.append(s)
            
        return notes_list
    
    def get_persons_with_message(self):
        '''
        This method returns a plain set of person ids corresponding to those persons who left a message.
        '''
        query  = self.db.message.event == self.eid
        query &= self.db.message.person == self.db.person.id
        rows = self.db(query).select(self.db.person.id)
        
        return set([r.id for r in rows])
        
    

    def __extract_numbers_from_rows(self, rows):
        n= {'total':0, 'taken':0, 'open':0}
        for row in rows:
            if not row.target_number:
                row.target_number = 0
            n['total'] += row.target_number
            n['taken'] += row.actual_number
        n['open'] = n['total'] - n['taken']
        return n

    def get_number_of_shifts(self):
        '''
        This method determines the current numbers of shifts and returns a dictionary with the following fields
            'open'  - number of still open shifts, that is, number of still needed helpers
            'taken' - number of shifts already taken by some helper (not equal to the number of helpers as one helper may have taken more than one shift)
            'total' - total number of configured shifts
        '''
        return self.__extract_numbers_from_rows(self.get_shifts())
    
    def get_number_of_donations(self):
        '''
        This method determines the current numbers of donations and returns a dictionary with the same fields as the method above.
        '''
        return self.__extract_numbers_from_rows(self.get_donations())

        
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
        
    def _limit_rows(self, rows, l):
        '''
        Auxiliary method to limit the length the rows objects constructed by other method of this class.
        l>0: number of rows returned, l=0: parameter is ignored, l<0: the last l rows are dropped
        '''
        if l == 0:
            return rows
        else:
            return rows[:l]
        
    def get_sorted_all(self):
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
        return self.rows_wait.sort(lambda row: row.id if row.id in lhelp else row.id + offset)

    def get_sorted(self, l = 0):
        '''
        This method returns only as many rows as numbers are available
        parameter l: specifies the length of the returned rows object  
        '''
        rows = self.get_sorted_all()
        
        # negative numbers in slices do not work
        r = rows[:max([0, Numbers(self.db, self.eid).number_of_available()])]
        return self._limit_rows(r, l)
        
    def get_denials(self, l = 0):
        '''
        This method returns a rows object containing all persons who have no sale yet for the current event
        and have got no denial mail so far.
        parameter l: specifies the length of the returned rows object
        '''
        r = self.rows_wait.find(lambda row: row.denial_sent != True)
        return self._limit_rows(r, l)
    
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
            for row in self.get_sorted_all():
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
        
        n = Contributions(self.db, self.eid).get_number_of_shifts()

        # determine or prognost position on the wait list
        pos = self.get_pos_current(pid)
        if pos == 0:
            pos = self.length() + 1
        
        x  = Numbers(self.db, self.eid).number_of_available() - pos - n['open']
        
        if x > 15:
            msg = 'Es sind noch genügend Kommissionsnummern frei. Sie werden sicher eine Nummer erhalten, sobald unsere Warteliste aufgelöst wird.'
        elif x >= 0:
            msg = 'Es sind noch einige Kommissionsnummern frei. Sie können sich gerne auf die Warteliste setzen. Ob Sie dann eine Nummer erhalten, hängt davon ab, wie viele Helfer wir noch gewinnen können. Um ganz sicher eine Nummer zu erhalten, tragen Sie sich für eine Helferschicht ein.'
        elif x >= -10:
            msg = 'Es sind derzeit Kommissionsnummern nur noch für Helfer verfügbar. Sollten Nummern zurückgegeben werden, könnten Sie evtl. noch eine über die Warteliste erhalten, ohne zu helfen.'
        else:
            msg = 'Es sind derzeit Kommissionsnummern nur noch für Helfer verfügbar. Unsere Warteliste ist auch schon so lang, daß Sie ohne zu helfen sicher keine Nummer mehr erhalten werden.'
        
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
        self.events = e
        
        for label, eid in e.get_all().iteritems():
            self.data[eid] = {'label': label, 'eid': eid, 'current': False, 'numbers': [], 'wait entries': [], 'shifts': [], 'donations': [], 'messages': []}
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


class Reminder():
    '''
    This class provides methods related to the reminder mails.
    Only the current event is considered.
    '''
    def __init__(self, db):
        self.db = db


    def get_all_persons(self):
        '''
        This method constructs the list of persons (vendors, helpers, bringers) who shall be reminded.
        '''
        # get a list of all helpers and bringers
        c = Contributions(self.db)
        
        rows_h = c.get_helper_list()
        rows_b = c.get_bringer_list()
        
        # create list of all persons with a sale
        query  = (self.db.sale.person == self.db.person.id)
        query &= (self.db.sale.event == c.eid)
        rows = self.db(query).select(self.db.person.id, self.db.person.name, self.db.person.forename)
        rows_s = removeDuplicates(self.db, rows)
        
        rows_compact = rows_h | rows_b | rows_s# | removes duplicates!
        
        return rows_compact


class CopyConfig():
    '''
    This class contains code to copy the configuration from an former event to the current event.
    '''
    def __init__(self, db,  source_event_id):
        self.db = db
        self.source_event_id = source_event_id
        
        self.current_event_id = Events(db).current.event.id
        
    def __copy_rows(self, table):
        '''
        This method copies all rows of the given table which are linked to the source event. The new entries are linked to the current event.
        The number of rows (inserted or updated) is returned
        '''
        rows = self.db(table.event == self.source_event_id).select()
        
        n = 0
        for row in rows:
            n += 1
            data = row.as_dict()
            data['event'] = self.current_event_id
            
            # remove id
            if 'id' in data:
                del data['id']
            
            # remove virtual attribute
            if 'actual_number' in data:
                del data['actual_number']
                
            table.update_or_insert(**data)
        
        return n
        
    def copy_donations(self):
        return self.__copy_rows(self.db.donation)
            
    def copy_shifts(self):
        return self.__copy_rows(self.db.shift)
