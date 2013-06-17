'''
@author: mattf
'''
from .. import fullparse
import urllib2
import sys
import json



def parseString():
    eg = '''
# a comment
data_startthedata

  save_firstsave
  
    _mykey "and my value"
  
    loop_
      _id1
      _id2
      "hi"
      "bye"
      "byebye"
      "hi ... hi??"
    stop_
  
  save_ # this comment explains that the data's done
'''
    parsed = fullparse.parse(eg)
    return parsed.bind(lambda p: (eg, p))


def parseFile(path):
    with open(path, 'r') as infile:
        inputStr = infile.read()
        parsed = fullparse.parse(inputStr)
        return parsed.bind(lambda p: (inputStr, p))


def parseFromUrl():
    url3 = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/248'
    url2 = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR2/248'
    page = urllib2.urlopen(url3)
    inputStr = page.read()
    page.close()
    parsed = fullparse.parse(inputStr)
    return parsed.bind(lambda p: (inputStr, p))


def parseFromStdin():
    inputStr = sys.stdin.read()
    parsed = fullparse.parse(inputStr)
    return parsed.bind(lambda p: (inputStr, p))


if __name__ == "__main__":
    print json.dumps(parseFromStdin()[2].toJSONObject())
