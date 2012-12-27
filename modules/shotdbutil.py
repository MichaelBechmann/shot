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
        
    def vendor(self, vid, s):
        
        log = self.db.vendor[vid].log
        
        if (log == None):
            log = ''
        else:
            log += ' --> '
            
        log += self.now.strftime("%Y-%m-%d %H:%M") + ': ' + s
        
        self.db(self.db.vendor.id == vid).update(log = log)

class Events():
    '''
    This class provides information about the events.
    '''
    def __init__(self, shotdb):
        self.current_id = shotdb(shotdb.event.active == True).select().last().id
        self.current = shotdb.event(self.current_id).label
        
        # note: compact form  self.id = {r.label: r.id for r in shotdb(shotdb.event.id > 0).select()}
        # doesn't work on willy (python 2.6.6 has apparently no list comprehension for dicts!) syntax error !?
        self.id = {}
        for r in shotdb(shotdb.event.id > 0).select():
            self.id[r.label] = r.id      
        self.all     = self.id.keys()


class Ident():
    '''
    This class provides methods for the generation of identification codes and their verification.
    The identification link shall not display the variables used. Instead a single identification string
    comprising the database id and the code shall be used.
    '''
    
    def __init__(self, shotdb = None, linkcode = None):

        self.shotdb = shotdb
        self.linkcode = linkcode
        self.id = 0
        self.b_verified = False      
        
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
        self.vendor = self.shotdb.vendor(self.id)
        if(self.vendor != None):            
            if(c == self.vendor.code):
                currentevent = self.shotdb(self.shotdb.event.active == True).select().last().id
                self.shotdb(self.shotdb.vendor.id == self.id).update(verified = currentevent)
                self.b_verified = True

class Numbers():
    '''
    This class provides methods to retrieve information on the sale numbers from the database.
    The results are evaluated for the given event.
    
    arguments: eid - event database id
    '''
    def __init__(self, shotdb, eid):  
        self.shotdb = shotdb
        self.eid    = eid
        self.event  = self.shotdb.event[eid]
        
    def _s_assigned(self):
        '''
        This method returns a set (not a list) of all assigned numbers
        '''
        q = self.shotdb.sale.event == self.eid
        s = set([r.number for r in self.shotdb(q).select()])
        
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
        This method returns a list of all available numbers for normal vendors
        '''
        return self._decode(self.event.number_ranges)
        
    def config_kg(self):
        '''
        This method returns a list of all available numbers for vendors from the kindergarten.
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
        This method returns a list of the free numbers for normal vendors.
        '''
        return self._free()
        
    def free_kg(self):
        '''
        This method returns a list of the free numbers for vendors from the kindergarten.
        '''
        return self._free(kg = True)
