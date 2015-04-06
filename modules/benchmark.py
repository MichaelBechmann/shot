# -*- coding: utf-8 -*-
'''
creation: bechmann, Apr 4, 2015

This module contains some benchmark tests to evaluate the performance of the various web servers used.
'''
from gluon.html import *
from datetime import datetime
from gluon.dal import DAL
import time

class Benchmark():
    '''
    This is the parent class of all benchmark tests.
    Note: The standard module "timeit" cannot easily be used in the integrated web2py environment.
    '''
    
    id =       'default'
    duration = 0
    repetitions = 1
    
    def run(self):
        start = datetime.now()
        
        for i in range(self.repetitions):
            self.test()
        
        end = datetime.now()
        delta = end - start
        self.duration = delta.total_seconds()
        return dict(id= self.id, duration = self.duration)
    
    def test(self):
        '''
        Default implementation, to be overloaded by the child classes.
        '''
        pass
    
    
class BenchmarkCalculations(Benchmark):
    id = 'Arithmetic calculations'
    
    def test(self):
        w = 2000
        for i in range (-w, w):
            res = [(i*i, i/n, i%n, i+i-n) for n in range(1, w)]
            
            
class BenchmarkListManipulation(Benchmark):
    id = 'Manipulation of long large lists'
    
    def test(self):
        w = 200000
        l = ['This is some test text. The number is %d (for sorting)' % (x%7) for x in range(w)]
        l.sort()
        l2 = [(s, 'Some other test text') for s in l]
        
        for i in range(w):
            l2.append(['Yet another test text' for x in range(5)])
            
        
        
class BenchmarkHTMLHelper(Benchmark):
    id = 'Using web2py html helper functions'
    
    def test(self):
        wrows = 5000
        wcols = 5
        t = TABLE(*[TR(*[DIV(SPAN('Some text'), A('some link'), DIV('more text')) for col in range(wcols)]) for row in range(wrows)])

class BenchmarkDBQuery(Benchmark):
    id = 'Multiple database queries'
    
    def __init__(self, db):
        self.db = db
    
    def test(self):
        w = 300
        for i in range(w):
            for e in range(1,5):
                
                p = self.db.person(i)
                
                query  = (self.db.sale.event == e)  
                query &= (self.db.sale.person == self.db.person.id)
                query &= (self.db.person.id == i)
        
                rows = self.db(query).select(self.db.person.name, self.db.sale.number)


class BenchmarkSleep(Benchmark):
    id = 'Simply sleeping'
    
    def test(self):
        time.sleep(600)
        