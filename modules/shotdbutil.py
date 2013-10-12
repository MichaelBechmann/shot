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
        
        self.current = db(db.event.active == True).select().last()
        
    def get_all(self):
        self.all = {r.label:r.id  for r in self.db(self.db.event.id > 0).select()}
        
    def previous(self, eid = 0):
        '''
        This method returns the id of the previous event.
        The argument is the event id of the event for which the previous event shall be determined.
        If no argument is given, the current event is assumed.
        
        Note: The previous event id is not necessarily (current event id - 1) because intermediate events could have been deleted.
        Empty intermediate events (events without connected sales or helps etc.) are not sorted out and should be removed from the database.
        '''
        if eid > 0:
            self.eid = eid
        else:
            self.eid = self.current.id
        self.get_all()
        old=([i for i in self.all.values() if i < self.eid])
        old.append(0) # always return something
        old.sort()
        return old[-1]
        

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
                currentevent = Events(self.db).current.id
                self.db(self.db.person.id == self.id).update(verified = currentevent)
                self.person['verified'] = currentevent # This dictionary must be consistent with the db, otherwise the old current event will be re-written to the db!
                self.b_verified = True

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
        
        self.numbers = Numbers(self.db, self.e.current.id)
        if self.numbers.b_numbers_available() == False:
            return 0
        
        self.previousevent = self.e.previous()
        
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
            eid = self.e.current.id
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
                        sid = self.db.sale.insert(event = self.e.current.id, person = self.pid, number = sn) 
                        log = 'sale # ' + str(sid) + '/ number ' + str(sn) + ' added'
                    else:
                        log = 'no sale added: no more sale numbers available'
                except IntegrityError:
                    # Apparently the determined sale number has just been by somebody else.
                    # The database connection must be refreshed in order to get updated information about the already assigned sale numbers.
                    self.db.commit()
                    pass
                else:
                    break
        else:
            log = 'no sale added: sale # ' + str(sid) + '/ number ' + str(sn) + ' already assigned!'
        
        # add log info to person
        Log(self.db).person(self.pid, log)

        return sid
    
        
class WaitList():
        '''
        This class collects code for the resolution of the wait list.
        '''
        def __init__(self, db):
            self.eid = Events(db).current.id
        
            # get all wait list entries from the current event with no sale linked to it yet
            query  = (db.wait.event == self.eid)
            query &= (db.wait.person == db.person.id)
            query &= (db.wait.sale == None)
            
            self.rows_all = db(query).select(db.wait.id, db.wait.person, db.wait.sale, db.wait.denial_sent)
        
            # get all wait list entries which additionally are linked to shifts
            query_help  = query
            query_help &= (db.person.id == db.wait.person)
            query_help &= (db.person.id == db.help.person)
            query_help &= (db.shift.id == db.help.shift)
            query_help &= (db.shift.event == self.eid)
            
            
            lhelp = []
            for row in db(query_help).select(db.wait.id):
                lhelp.append(row.id)
            
            if len(lhelp) > 0:
                offset = max(lhelp)
            else:
                offset = 0                
            
            # sort helpers in front
            # Note: sort method of rows object does not operate in place!
            aux = self.rows_all.sort(lambda row: row.id if row.id in lhelp else row.id + offset)
            
            # return only as many rows as numbers are available
            # negative numbers in slices do not work
            self.rows_sorted = aux[:max([0, Numbers(db, self.eid).number_of_available()])]
            
            
            # query like != True doesn't work
            query_denial = query & ((db.wait.denial_sent == False) | (db.wait.denial_sent == None))
            self.rows_denial = db(query_denial).select(db.wait.id, db.wait.person)
            
class HelperList():
    '''
    This class contains code concerning the Helper lists.
    '''
    def __init__(self, db):
        self.eid = Events(db).current.id
        
        # get all persons which help
        query  = (db.help.person == db.person.id)
        query &= (db.help.shift  == db.shift.id)
        query &= (db.shift.event == self.eid)
        
        self.rows = db(query).select(db.person.id, db.help.person, db.person.name, db.person.forename)        
        
        # remove multiple occurrence of helping persons
        # For some reason the db argument is required fro SQLTABLE to work properly.
        self.rows_compact = Rows(db)
        # For some reason the records must be cleared (otherwise the helperlist will grow each time this class is called!).
        self.rows_compact.records = []
        
        person_list = []
        for row in self.rows:
            if row.person.id not in person_list:
                self.rows_compact.records.append(row)
                person_list.append(row.person.id)
            
            
            
            
            

    
            