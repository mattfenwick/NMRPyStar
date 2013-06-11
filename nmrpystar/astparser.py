from parse import Parser
import model


m = model


# String -> Parser Token Token
def tokentype(t):
    return Parser.satisfy(lambda k: k.tokentype == t)


def loopRest(open):
    def action(ids, vals, close):
        idents, values = [i.value for i in ids], [v.value for v in vals]
        return m.Loop.fromSimple(idents, values, open.meta)
    return Parser.app(action,
                      tokentype('identifier').many0(),
                      tokentype('value').many0(),
                      tokentype('stop')).commit({'message': 'unable to parse loop', 'open': open})

# Parser Token Loop                      
loop = tokentype('loop').bind(loopRest)


# Parser Token (String, String)
datum = Parser.app(lambda i, v: (i.value, v.value), 
                   tokentype('identifier'), 
                   tokentype('value'))

                   
def saveRest(open):
    def action(xs):
        return (open.value, m.Save.fromSimple(xs, open.meta))
    return loop.plus(datum).many0().seq2L(tokentype('saveclose')).fmap(action)

# Parser Token (String, Save)
save = tokentype('saveopen').bind(saveRest)


def dataRest(open):
    return save.many1().fmap(lambda ss: m.Data.fromSimple(open.value, ss, open.meta))

# Parser Token Data
data = tokentype('dataopen').bind(dataRest)


def checkEmpty(tokens):
    if tokens.isEmpty():
        return Parser.pure(None)
    else:
        return Parser.error(('unparsed tokens remaining', tokens.getRest()))
    
# Parser Token Data
#   must consume all tokens
nmrstar = data.seq2L(Parser.get.bind(checkEmpty))
