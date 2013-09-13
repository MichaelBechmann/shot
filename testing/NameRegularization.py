# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 21, 2013

This module ...
'''

import re

namelist = ['Bechmann', 
            'bechmann', 
            'Bugner   -Bechmann', 
            'bugner-bechmann', 
            ' bechmann', 
            ' bugner - bechmann ', 
            'maier-meier-müller',
            'maier - meier -   müller',
            'von hinten',
            'van der waals',
            'von der Heydt',
            'de Jong',
            'de   jong',
            'oTTERSWEIER',
            'OTTERSWEIER',
            'BUGNER-BECHMANN',
            '  bugner  -   beCHMann   MÜLLER',
            'übelbach',
            'EXÁMPLE',
            'straßburg',
            'BÜHL',
            'Bühl'
            ]

    
    
def regularizeName(s):
    
    # remove leading ans trailing spaces
    reg = s.lstrip().rstrip()
    
    for sep in (' ', '-'):
        reg = re.sub('\s*' + sep + '\s*', sep, reg)  
          
    exceptions = ('von' , 'der', 'van', 'de', 'du')

    aux = []
    for part in reg.split(' '):
        aux.append('-'.join([x in exceptions and x or x.decode().capitalize().encode() for x in part.split('-')]))
    reg = ' '.join(aux)
    
    if s != reg:
        print '    ====> %s != %s !' % (s, reg)
    
    return reg






for n in namelist:
    
    print regularizeName(n)
    #print n.encode('utf-8')
    
    
a = u'H\xf6\xdf'
b = 'H\xc3\xb6\xc3\x9f'
print b == a

print a.encode('utf-8')
print b.encode('utf-8')

print b != a