import sys

_PY2 = sys.version_info[0] == 2

def makeBytesFromSequence(sequence):
    return binaryType(b''.join(sequence) if _PY2 else sequence)

def nextMethod(iterator):
    return getattr(iterator, 'next' if _PY2 else '__next__')

binaryType = str if _PY2 else bytes # @UndefinedVariable
characterType = str if _PY2 else chr # @UndefinedVariable
textType = unicode if _PY2 else str # @UndefinedVariable
