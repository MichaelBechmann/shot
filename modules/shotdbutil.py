# -*- coding: utf-8 -*-
#from gluon.custom_import import track_changes
#track_changes(True)

import re
import random
import string
import datetime
from shotconfig import *
from gluon.dal import DAL


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
        self.current_id = db(db.event.active == True).select().last().id
        self.current = db.event(self.current_id).label
        
        
        self.all = {r.id:r.label  for r in db(db.event.id > 0).select()}
        self.all_labels = self.all.values()
        
    def previous(self, eid = 0):
        '''
        This method returns the id of the previous event.
        The argument is the event id of the event for which the previous event shall be determined.
        If no argument is given, the current event is assumed.
        
        Note: The previous event id is not necessarily (current event id - 1) because intermediate could be deleted.
        Empty intermediate events (events without connected sales or helps etc.) are not sorted out and should be removed from the database.
        '''
        if eid > 0:
            self.eid = eid
        else:
            self.eid = self.current_id
        
        old=([i for i in self.all.keys() if i < self.eid])
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
        
        self._getcode()
        if self.linkcode != None:
            self._verify()


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
                currentevent = self.db(self.db.event.active == True).select().last().id
                self.db(self.db.person.id == self.id).update(verified = currentevent)
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
            
        # greate a list of the partial ranges 
        ll = [range(l[i], l[i+1] + 1) for i in range(0, len(l), 2)]        
        
        # flatten the list of lists
        # see: http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        return sum(ll, [])
    
    
    def config(self):
        '''
        This method returns a list of all numbers available to the public
        '''
        return self._decode(self.event.number_ranges)
        
    def config_kg(self):
        '''
        This method returns a list of all numbers available to persons related to the kindergarten.
        '''  
        return self._decode(self.event.number_ranges_kg)

    def config_all(self):
        '''
        This method returns a list of all available sale numbers (normal + kindergarten).
        '''
        return self.config() + self.config_kg()
    
    def _free(self, kg = False):
        if kg:
            c = self.config_kg()
        else:
            c = self.config()
        s = set(c).difference(self._s_assigned())
        l = list(s)        
        # sort as the set is hash like
        l.sort()
        return l
    
    def free(self):
        '''
        This method returns a list of the free public numbers.
        '''
        return self._free()
        
    def free_kg(self):
        '''
        This method returns a list of the free kindergarten numbers.
        '''
        return self._free(kg = True)
    
    def get_b_numbers_free(self, kg = False):
        '''
        This method returns the info whether or not there are still free numbers.
        '''        
        if len(self._free(kg)) > 0:
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
        self.currentevent  = self.e.current_id
                 

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
        This method determines the sale number for the person based on a set of rules:
        
        1) If the person helped at the previous event => assign old number (last number of this person, not necessarily from the previous event)
        2) If the old number of the person is still free and not a number of a helper from the previous event => assign old number
        3) If person has no old number or the old number is not free any more => assign one of the free numbers
        4) Assign numbers of helpers at the previous event not before all other free numbers (block previous helper numbers).
        '''
        self.previousevent = self.e.previous()
        self.numbers = Numbers(self.db, self.currentevent)
        
        # check whether or not the person helped at the previous event
        query  = (self.db.shift.event == self.previousevent)
        query &= (self.db.help.shift == self.db.shift.id)
        query &= (self.db.help.person == self.pid)
        if len(self.db(query).select()) > 0:
            self.b_helped_previous_event = True
        else:
            self.b_helped_previous_event = False
        
        # get list of potential (= free) sale numbers
        if self.db.person(self.pid).kindergarten != config.no_kindergarten_id:
            self.free = self.numbers.free_kg()
        else:
            self.free = self.numbers.free()
            

        on = self.get_old_number()
        self.on = on
        
        sn = 0
        if (on > 0) and (on in self.free):
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
                sn = max(sprio)
            elif len(self.free) > 0:
                sn = self.free[-1]
        
        return sn
    
    def _get_sale(self, eid = 0):
        '''
        This method returns the sale row object (not the sale number!) of the person for a given event. If no event is passed the current event is assumed
        If the person does not have a number 0 is returned
        '''
        if eid == 0:
            eid = self.currentevent
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
            sn = self.determine_number()
            if sn > 0:
                # add sale entry    
                sid = self.db.sale.insert(event = self.currentevent, person = self.pid, number = sn, number_assigned = True) 
                log = 'sale # ' + str(sid) + '/ number ' + str(sn) + ' added'
            else:
                log = 'no sale added: no numbers free!'
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
            self.eid = Events(db).current_id
        
            # get all wait list entries from the current event which do not have a number yet
            query  = (db.wait.event == self.eid)
            query &= (db.wait.person == db.person.id)
        
            # get all wait list entries which additionally are linked to shifts
            query_help = query
            query_help &= (db.person.id == db.wait.person)
            query_help &= (db.person.id == db.help.person)
            query_help &= (db.shift.id == db.help.shift)
            query_help &= (db.shift.event == self.eid)
            
            rows = db(query).select(db.wait.id, db.wait.person, db.wait.sale)
    
            lhelp = []
            for row in db(query_help).select(db.wait.id):
                lhelp.append(row.id)
            lhelp.sort()
            
            self.rows_sorted = rows.sort(lambda row: row.id if row.id in lhelp else row.id + max(lhelp))
            
            
            
            