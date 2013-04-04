import json
import sys


infile = sys.argv[1]

with open(infile, 'r') as i:
    contents = i.read()

# print contents

injson = json.loads(contents)

def dumper(arr):
    # takes in a list of objects
    peaklines = map(json.dumps, arr['peaks'])
    pklins = map(lambda x: '    ' + x, peaklines)
    return '[\n' + ',\n'.join(pklins) + '\n]'

# print injson
print dumper(injson)


