'''
This tool parses specified the *.scss file for definitions of color variables.
A html page partial is generated which displays each color definition found.
'''
import os.path
import re
from gluon.html import *

re_ColorDefinition = re.compile('([\$\-\w]+)\s*:\s*(#\w+)\W')
re_SourceFile      = re.compile('/home/bechmann/projects/web/web2py/applications/shot/(.*)')

input_files = [
               '/home/bechmann/projects/web/web2py/applications/shot/foundation_shot/src/assets/scss/_settings.scss'
               ]
output_file = '/home/bechmann/projects/web/web2py/applications/shot/foundation_shot/src/partials/color_theme.html'
of = open(output_file, 'w')

class ColorDefinition(object):
    def __init__(self, var, code, file):
        self.var  = var
        self.code = code
        m = re_SourceFile.match(file)
        if m:
            self.file = m.group(1)
        else:
            self.file = 'source file unknown'

    def getHtml(self):
        style_text  = 'color: '      + self.code
        style_block = 'background: ' + self.code
        d = DIV(DIV(SPAN('', _style = style_block),
                    DIV('This is some text ...', _style = style_text),
                    DIV(self.var + ': ' + self.code),
                    DIV(self.file),
                    _class = 'color-block'
                    ),
                _class = 'column'
                )



        return d


colors = []
for filename in input_files:
    file = open(filename, 'r')
    for line in file:
        m = re_ColorDefinition.search(line)
        if m:
            colors.append(ColorDefinition(m.group(1), m.group(2), filename))

heading     = H1('Color Theme')
description = P('The following colors have been extracted from the *.scss files by %s.' % os.path.abspath(__file__) )

html_output = DIV(heading,
                  description,
                  DIV(*[c.getHtml() for c in colors],
                  _class='row up-1 medium-up-3 large-up-5')
                  )

of.write(str(html_output))
of.close()