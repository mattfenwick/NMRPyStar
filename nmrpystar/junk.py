'''
@author: matt
'''

temp = '''
_stop        =  _string("stop_").fmap(posFirst)
_saveclose   =  _string("save_").fmap(posFirst)
_loop        =  _string("loop_").fmap(posFirst)
_dataopen    =  Parser.all([_string("data_").fmap(posFirst), space.not1().many1().fmap(extract)])
_saveopen    =  Parser.all([_string("save_").fmap(posFirst), space.not1().many1().fmap(extract)])


def uqAction(c, cs):
    return model.Value(c.meta, extract([c] + cs))

unquoted = Parser.app(uqAction, special.not1(), space.not1().many0())


saveopen    =  munch(_saveopen)
saveclose   =  munch(_saveclose)
dataopen    =  munch(_dataopen)
loop        =  munch(_loop)
stop        =  munch(_stop)
'''