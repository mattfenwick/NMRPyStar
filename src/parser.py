import maybeerror as me
import parsercombinators as pc


# interpreter workaround
reload(me)
reload(pc)


Parser = pc.parserFactory(me.MaybeError)
