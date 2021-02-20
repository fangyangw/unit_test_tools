class StompConfig(object):
    """This is a container for those configuration options which are common to both clients (sync and async) and are needed to establish a STOMP connection. All parameters are available as attributes with the same name of this object.

    :param uri: A failover URI as it is accepted by :class:`~.StompFailoverUri`.
    :param login: The login for the STOMP brokers. The default is :obj:`None`, which means that no **login** header will be sent.
    :param passcode: The passcode for the STOMP brokers. The default is :obj:`None`, which means that no **passcode** header will be sent.
    :param version: A valid STOMP protocol version, or :obj:`None` (equivalent to the :attr:`DEFAULT_VERSION` attribute of the :class:`~.StompSpec` class).
    :param check: Decides whether the :class:`~.StompSession` object which is used to represent the STOMP sesion should be strict about the session's state: (e.g., whether to allow calling the session's :meth:`~.StompSession.send` when disconnected).
    :param sslContext: An SSL context to wrap around a TCP socket connection. This object is defined in the Python standard library: `ssl.SSLContext <https://docs.python.org/3/library/ssl.html#ssl.SSLContext>`_
    :type sslContext: ssl.SSLContext

    .. note :: Login and passcode have to be the same for all brokers because they are not part of the failover URI scheme.

    .. seealso :: The :class:`~.StompFailoverTransport` class which tells you which broker to use and how long you should wait to connect to it, the :class:`~.StompFailoverUri` which parses failover transport URIs.

    *SSL Example*

    .. code-block:: python

        import ssl
        sslContext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # It's good practice to disable insecure protocols by default. Note that
        # since Python 3.6, SSLv3 is disabled by default.
        sslContext.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_SSLv3

        # For testing and development, it is often useful to disable host cert
        # validation, which requires *both* of the following settings.
        sslContext.check_hostname = False
        sslContext.verify_mode = ssl.CERT_NONE

        # Create the StompConfig as usual. Remember that for TLS/SSL, the URI should
        # begin with "ssl"
        config = StompConfig(
            'ssl://host.com',
            login='admin',
            passcode='admin',
            sslContext=sslContext
        )

    """
    def __init__(self, uri, login=None, passcode=None, version=None, check=True, sslContext=None):
        self.uri = uri
        self.login = login
        self.passcode = passcode
        self.version = version
        self.check = check
        self.sslContext = sslContext
