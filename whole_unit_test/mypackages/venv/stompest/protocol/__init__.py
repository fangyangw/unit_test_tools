"""The :mod:`~.protocol` package is a collection of generic components each of which you can use independently for your own STOMP related functionality.

.. note:: Please restrict your imports to the main package :mod:`stompest.protocol`. The subpackage structure is potentially unstable.
"""
from stompest.protocol.failover import StompFailoverTransport, StompFailoverUri
from stompest.protocol.frame import StompFrame
from stompest.protocol.parser import StompParser
from stompest.protocol.spec import StompSpec
from stompest.protocol.session import StompSession
