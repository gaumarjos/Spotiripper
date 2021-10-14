s = str("ciao è!")
print(s)


import os




if not os.environ.get('PYTHONIOENCODING'):
    os.environ['PYTHONIOENCODING'] = str("utf-8")




'''
from __future__ import unicode_literals
import sys
# reload(sys)
sys.setdefaultencoding('utf8')

import re
import unicodedata

def extract_word(text):
    print("Input Text::{}".format(text))
    regex = r"(\w|\s)*"
    matches = re.finditer(regex, text, re.DOTALL)
    newstr = ''
    for matchNum, match in enumerate(matches):
        matchNum = matchNum + 1
        newstr = newstr + match.group()
    print("Output Text::{}".format(newstr))
    return newstr

# s = "ciao èèèè".encode('utf-8')
s1 = "ciao èèèè".encode('ascii', 'replace')
print(s1)

s2 = "ciao éééé".encode('utf-8')
print(s2.decode('utf-8'))



#s2 = unicode("ciao èèèè", 'utf-8')

#extract_word(s)
'''
'''
print(s.encode('unicode-escape'))

print('ciao èèèè'.encode('unicode-escape').replace('\\\\', '\\').decode('unicode-escape'))



text = text.encode(‘utf-8’)
Simple isn’t it!!
But wait you need to strip out extra escape characters to do string operations. here is how you can strip those out
'''