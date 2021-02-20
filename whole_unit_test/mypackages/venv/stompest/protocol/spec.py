from stompest.error import StompProtocolError

class StompSpec(object):
    """This class hosts all constants related to the STOMP protocol specification in its various versions. There really isn't much to document, but you are invited to take a look at all available constants in the source code. Wait a minute ... one attribute is particularly noteworthy, name :attr:`DEFAULT_VERSION` --- which currently is :obj:`'1.0'` (but this may change in upcoming stompest releases, so you're advised to always explicitly define which STOMP protocol version you are going to use).
    
    .. seealso :: Specification of `STOMP protocol <http://stomp.github.com//index.html>`_, your favorite broker's documentation for additional STOMP headers.
    """
    VERSION_1_0, VERSION_1_1, VERSION_1_2 = '1.0', '1.1', '1.2'
    VERSIONS = (VERSION_1_0, VERSION_1_1, VERSION_1_2)
    DEFAULT_VERSION = VERSION_1_0

    ABORT = 'ABORT'
    ACK = 'ACK'
    BEGIN = 'BEGIN'
    COMMIT = 'COMMIT'
    CONNECT = 'CONNECT'
    DISCONNECT = 'DISCONNECT'
    NACK = 'NACK'
    SEND = 'SEND'
    STOMP = 'STOMP'
    SUBSCRIBE = 'SUBSCRIBE'
    UNSUBSCRIBE = 'UNSUBSCRIBE'

    CLIENT_COMMANDS = {
        VERSION_1_0: {
            ABORT, ACK, BEGIN, COMMIT, CONNECT, DISCONNECT,
            SEND, SUBSCRIBE, UNSUBSCRIBE
        },
        VERSION_1_1: {
            ABORT, ACK, BEGIN, COMMIT, CONNECT, DISCONNECT,
            NACK, SEND, STOMP, SUBSCRIBE, UNSUBSCRIBE
        },
        VERSION_1_2: {
            ABORT, ACK, BEGIN, COMMIT, CONNECT, DISCONNECT,
            NACK, SEND, STOMP, SUBSCRIBE, UNSUBSCRIBE
        }
    }

    CONNECTED = 'CONNECTED'
    ERROR = 'ERROR'
    MESSAGE = 'MESSAGE'
    RECEIPT = 'RECEIPT'

    SERVER_COMMANDS = {
        VERSION_1_0: {CONNECTED, ERROR, MESSAGE, RECEIPT}
        , VERSION_1_1: {CONNECTED, ERROR, MESSAGE, RECEIPT}
        , VERSION_1_2: {CONNECTED, ERROR, MESSAGE, RECEIPT}
    }

    COMMANDS = dict(CLIENT_COMMANDS)
    for (version, commands) in SERVER_COMMANDS.items():
        COMMANDS.setdefault(version, set()).update(commands)

    COMMANDS_BODY_ALLOWED = {
        VERSION_1_0: COMMANDS[VERSION_1_0]
        , VERSION_1_1: {SEND, MESSAGE, ERROR}
        , VERSION_1_2: {SEND, MESSAGE, ERROR}
    }

    LINE_DELIMITER = '\n'
    STRIP_LINE_DELIMITER = {
        VERSION_1_2: '\r'
    }

    ESCAPE_CHARACTER = '\\'
    ESCAPED_CHARACTERS = {
        VERSION_1_0: {}
        , VERSION_1_1: {'\\': '\\', 'c': ':', 'n': '\n'}
        , VERSION_1_2: {'\\': '\\', 'c': ':', 'n': '\n', 'r': '\r'}
    }
    COMMANDS_ESCAPE_EXCLUDED = {
        VERSION_1_0: COMMANDS[VERSION_1_0]
        , VERSION_1_1: {CONNECT, CONNECTED}
        , VERSION_1_2: {CONNECT, CONNECTED}
    }

    FRAME_DELIMITER = '\x00'
    HEADER_SEPARATOR = ':'

    ACCEPT_VERSION_HEADER = 'accept-version'
    ACK_HEADER = 'ack'
    CONTENT_LENGTH_HEADER = 'content-length'
    CONTENT_TYPE_HEADER = 'content-type'
    DESTINATION_HEADER = 'destination'
    HEART_BEAT_HEADER = 'heart-beat'
    HOST_HEADER = 'host'
    ID_HEADER = 'id'
    LOGIN_HEADER = 'login'
    MESSAGE_ID_HEADER = 'message-id'
    PASSCODE_HEADER = 'passcode'
    RECEIPT_HEADER = 'receipt'
    RECEIPT_ID_HEADER = 'receipt-id'
    SELECTOR_HEADER = 'selector'
    SESSION_HEADER = 'session'
    SERVER_HEADER = 'server'
    SUBSCRIPTION_HEADER = 'subscription'
    TRANSACTION_HEADER = 'transaction'
    VERSION_HEADER = 'version'

    ACK_AUTO = 'auto'
    ACK_CLIENT = 'client'
    ACK_CLIENT_INDIVIDUAL = 'client-individual'
    CLIENT_ACK_MODES = {ACK_CLIENT, ACK_CLIENT_INDIVIDUAL}

    HEART_BEAT_SEPARATOR = ','

    @classmethod
    def version(cls, version=None):
        """Check whether **version** is a valid STOMP protocol version.
        
        :param version: A candidate version, or :obj:`None` (which is equivalent to the value of :attr:`StompSpec.DEFAULT_VERSION`). 
        """
        if version is None:
            version = cls.DEFAULT_VERSION
        if version not in cls.VERSIONS:
            raise StompProtocolError('Version is not supported [%s]' % version)
        return version

    @classmethod
    def versions(cls, version):
        """Obtain all versions prior or equal to **version**.
        """
        version = cls.version(version)
        for v in cls.VERSIONS:
            yield v
            if v == version:
                break

    @classmethod
    def codec(cls, version):
        return 'ascii' if version == cls.VERSION_1_0 else 'utf-8'
