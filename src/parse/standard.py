import parse.maybeerror as me
import parse.combinators as pc


# interpreter workaround
reload(me)
reload(pc)


Parser = pc.parserFactory(me.MaybeError)
