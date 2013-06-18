'''
@author: mattf
'''
from .. import fullparse
import urllib2
import sys
import json


def withInput(starString):
    parsed = fullparse.parse(starString)
    return parsed.fmap(lambda p: (starString, p))


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
    return withInput(eg)


def parseFile(path):
    with open(path, 'r') as infile:
        inputStr = infile.read()
        return withInput(inputStr)


def parseUrl(myUrl='http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/248'): # this is the url of an NMR-Star3 file
    #url2 = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR2/248'
    page = urllib2.urlopen(myUrl)
    inputStr = page.read()
    page.close()
    return withInput(inputStr)


def parseStdin():
    inputStr = sys.stdin.read()
    return withInput(inputStr)


if __name__ == "__main__":
    print json.dumps(parseStdin()[1].toJSONObject())
