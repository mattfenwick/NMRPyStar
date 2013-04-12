import scripts.parserdriver as p
import nmrstar.simple.unparser as u



m = p.parseFile(p.readMe())

# with open('testout.txt', 'w') as outfile:
#    outfile.write(u.unparse(m.value['result']))

print u.unparse(m.value['result'])
