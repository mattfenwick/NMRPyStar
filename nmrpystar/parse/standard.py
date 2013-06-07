from .maybeerror import MaybeError
from .combinators import parserFactory


Parser = parserFactory(MaybeError)
