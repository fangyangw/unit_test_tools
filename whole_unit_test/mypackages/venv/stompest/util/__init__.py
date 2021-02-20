import copy
import functools
import sys

from stompest._backwards import textType
from stompest.protocol import StompSpec

_RESERVED_HEADERS = set([StompSpec.MESSAGE_ID_HEADER, StompSpec.DESTINATION_HEADER, 'timestamp', 'expires', 'priority'])

def filterReservedHeaders(headers):
    return dict((header, value) for (header, value) in headers.items() if header not in _RESERVED_HEADERS)

def checkattr(attribute):
    def _checkattr(f):
        @functools.wraps(f)
        def __checkattr(self, *args, **kwargs):
            getattr(self, attribute)
            return f(self, *args, **kwargs)
        return __checkattr
    return _checkattr

def cloneFrame(frame, persistent=None):
    frame = copy.deepcopy(frame)
    frame.unraw()
    headers = filterReservedHeaders(frame.headers)
    if persistent is not None:
        headers['persistent'] = textType(bool(persistent)).lower()
    frame.headers = headers
    return frame
