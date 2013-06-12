'''
@author: mattf
'''
import nmrpystar.parser as nmp
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
    parsed = nmp.fullParse(eg)
    ast = parsed.value['result']
    return (eg, parsed, ast)


def parseFile():
    path = 'test/nmrstar/bmrb17661.txt'
    with open(path, 'r') as infile:
        inputStr = infile.read()
        parsed = nmp.fullParse(inputStr)
        ast = parsed.value
        return (inputStr, parsed, ast)


def parseFromUrl():
    url3 = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/248'
    url2 = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR2/248'
    page = urllib2.urlopen(url3)
    inputStr = page.read()
    page.close()
    parsed = nmp.fullParse(inputStr)
    ast = parsed.value['result']
    return (inputStr, parsed, ast)


def parseFromStdin():
    inputStr = sys.stdin.read()
    parsed = nmp.fullParse(inputStr)
    ast = parsed.value['result']
    return (inputStr, parsed, ast)


if __name__ == "__main__":
    print json.dumps(parseFromStdin()[2].toJSONObject())
