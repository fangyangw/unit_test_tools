import re

from stompest.error import StompFrameError
from stompest.protocol.spec import StompSpec

class _HeadersTransformer(object):
    _ESCAPE_CHARACTER = StompSpec.ESCAPE_CHARACTER

    @classmethod
    def get(cls, *args):
        try:
            return cls._INSTANCES[args]
        except KeyError:
            return cls._INSTANCES.setdefault(args, cls(*args))

    def __init__(self, version, command):
        self._version = version
        self._escapedCharacters = StompSpec.ESCAPED_CHARACTERS[version]
        if command in StompSpec.COMMANDS_ESCAPE_EXCLUDED[version]:
            self._sub = lambda _, text: text
        else:
            self._sub = re.compile(self._regex).sub

    def __call__(self, text):
        try:
            return self._sub(self._replace, text)
        except Exception as e:
            raise StompFrameError('No escape sequence defined for this character (version %s): %s [text=%s]' % (self._version, e, repr(text)))

    def _replace(self, match):
        return self._escapeSequences[match.group(1)]

class _HeadersEscaper(_HeadersTransformer):
    _INSTANCES = {} # each class needs its own instance cache

    @property
    def _escapeSequences(self):
        return {escapeSequence: '%s%s' % (self._ESCAPE_CHARACTER, character) for (character, escapeSequence) in self._escapedCharacters.items()}

    @property
    def _regex(self):
        return '(%s)' % '|'.join(map(re.escape, self._escapeSequences))

class _HeadersUnescaper(_HeadersTransformer):
    _INSTANCES = {} # each class needs its own instance cache

    @property
    def _escapeSequences(self):
        return {'%s%s' % (self._ESCAPE_CHARACTER, character): escapeSequence for (character, escapeSequence) in self._escapedCharacters.items()}

    @property
    def _regex(self):
        return '(%s)' % '|'.join(['%s.' % re.escape(self._ESCAPE_CHARACTER)] + [re.escape(c) for c in self._escapedCharacters.values()])

escape = _HeadersEscaper.get
unescape = _HeadersUnescaper.get
