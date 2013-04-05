import parsercombinators.maybeerror as me
import parsercombinators.combinators as pc


# interpreter workaround
reload(me)
reload(pc)


Parser = pc.parserFactory(me.MaybeError)
