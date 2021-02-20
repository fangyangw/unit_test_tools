import logging
import ssl
import time
import unittest

from stompest.config import StompConfig
from stompest.error import StompConnectionError, StompProtocolError
from stompest.protocol import StompFrame, StompSpec
from stompest.sync import Stomp

logging.basicConfig(level=logging.DEBUG)
LOG_CATEGORY = __name__

from stompest.tests import HOST, PORT, PORT_SSL, LOGIN, PASSCODE, VIRTUALHOST, BROKER

class SimpleStompIntegrationTest(unittest.TestCase):
    DESTINATION = '/queue/stompUnitTest'
    TIMEOUT = 0.1
    log = logging.getLogger(LOG_CATEGORY)

    def getConfig(self, version, port=PORT):
        return StompConfig('tcp://%s:%s' % (HOST, port), login=LOGIN, passcode=PASSCODE, version=version)

    def setUp(self):
        config = self.getConfig(StompSpec.VERSION_1_0)
        client = Stomp(config)
        client.connect(host=VIRTUALHOST)
        client.subscribe(self.DESTINATION, {StompSpec.ACK_HEADER: StompSpec.ACK_AUTO})
        client.subscribe(self.DESTINATION, {StompSpec.ID_HEADER: 'bla', StompSpec.ACK_HEADER: StompSpec.ACK_AUTO})
        while client.canRead(self.TIMEOUT):
            frame = client.receiveFrame()
            self.log.debug('Dequeued old %s' % frame.info())
        client.disconnect()

    def test_1_integration(self):
        config = self.getConfig(StompSpec.VERSION_1_0)
        client = Stomp(config)
        client.connect(host=VIRTUALHOST)

        client.send(self.DESTINATION, b'test message 1')
        client.send(self.DESTINATION, b'test message 2')
        self.assertFalse(client.canRead(self.TIMEOUT))
        client.subscribe(self.DESTINATION, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
        self.assertTrue(client.canRead(self.TIMEOUT))
        client.ack(client.receiveFrame())
        self.assertTrue(client.canRead(self.TIMEOUT))
        client.ack(client.receiveFrame())
        self.assertFalse(client.canRead(self.TIMEOUT))

    def test_2_transaction(self):
        config = self.getConfig(StompSpec.VERSION_1_0)
        client = Stomp(config)
        client.connect(host=VIRTUALHOST)
        client.subscribe(self.DESTINATION, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
        self.assertFalse(client.canRead(self.TIMEOUT))

        with client.transaction(4711) as transaction:
            self.assertEqual(transaction, '4711')
            client.send(self.DESTINATION, b'test message', {StompSpec.TRANSACTION_HEADER: transaction})
            self.assertFalse(client.canRead(0))
        self.assertTrue(client.canRead(self.TIMEOUT))
        frame = client.receiveFrame()
        self.assertEqual(frame.body, b'test message')
        client.ack(frame)

        with client.transaction(4713, receipt='4712') as transaction:
            self.assertEqual(transaction, '4713')
            self.assertEqual(client.receiveFrame(), StompFrame(StompSpec.RECEIPT, {StompSpec.RECEIPT_ID_HEADER: '4712-begin'}))
            client.send(self.DESTINATION, b'test message', {StompSpec.TRANSACTION_HEADER: transaction})
            client.send(self.DESTINATION, b'test message without transaction')
            self.assertTrue(client.canRead(self.TIMEOUT))
            frame = client.receiveFrame()
            self.assertEqual(frame.body, b'test message without transaction')
            client.ack(frame)
            self.assertFalse(client.canRead(0))
        frames = [client.receiveFrame() for _ in range(2)]
        frames = list(sorted(frames, key=lambda f: f.command))
        frame = frames[0]
        client.ack(frame)
        self.assertEqual(frame.body, b'test message')
        frame = frames[1]
        self.assertEqual(frame, StompFrame(StompSpec.RECEIPT, {StompSpec.RECEIPT_ID_HEADER: '4712-commit'}))

        try:
            with client.transaction(4714) as transaction:
                self.assertEqual(transaction, '4714')
                client.send(self.DESTINATION, b'test message', {StompSpec.TRANSACTION_HEADER: transaction})
                raise RuntimeError('poof')
        except RuntimeError as e:
            self.assertEqual(str(e), 'poof')
        else:
            raise
        self.assertFalse(client.canRead(self.TIMEOUT))

        client.disconnect()

    def test_3_timeout(self):
        timeout = 0.2
        client = Stomp(StompConfig(uri='failover:(tcp://localhost:61610,tcp://localhost:61613)?startupMaxReconnectAttempts=1,randomize=false', login=LOGIN, passcode=PASSCODE, version=StompSpec.VERSION_1_0))
        client.connect(host=VIRTUALHOST, connectTimeout=timeout)
        client.disconnect()

        client = Stomp(StompConfig(uri='failover:(tcp://localhost:61610,tcp://localhost:61611)?startupMaxReconnectAttempts=1,backOffMultiplier=3', login=LOGIN, passcode=PASSCODE, version=StompSpec.VERSION_1_0))
        self.assertRaises(StompConnectionError, client.connect, host=VIRTUALHOST, connectTimeout=timeout)

        client = Stomp(StompConfig(uri='failover:(tcp://localhost:61610,tcp://localhost:61613)?randomize=false', login=LOGIN, passcode=PASSCODE, version=StompSpec.VERSION_1_0)) # default is startupMaxReconnectAttempts = 0
        self.assertRaises(StompConnectionError, client.connect, host=VIRTUALHOST, connectTimeout=timeout)

    def test_3_socket_failure_and_replay(self):
        client = Stomp(self.getConfig(StompSpec.VERSION_1_0))
        client.connect(host=VIRTUALHOST)
        headers = {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL}
        token = client.subscribe(self.DESTINATION, headers)
        client.sendFrame(StompFrame(StompSpec.DISCONNECT)) # DISCONNECT frame is out-of-band, as far as the session is concerned -> unexpected disconnect
        self.assertRaises(StompConnectionError, client.receiveFrame)
        client.connect(host=VIRTUALHOST)
        client.send(self.DESTINATION, b'test message 1')
        client.ack(client.receiveFrame())
        client.unsubscribe(token)
        headers = {StompSpec.ID_HEADER: 'bla', StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL}
        client.subscribe(self.DESTINATION, headers)
        headers[StompSpec.DESTINATION_HEADER] = self.DESTINATION
        client.sendFrame(StompFrame(StompSpec.DISCONNECT)) # DISCONNECT frame is out-of-band, as far as the session is concerned -> unexpected disconnect
        self.assertRaises(StompConnectionError, client.receiveFrame)
        client.connect(host=VIRTUALHOST)
        client.send(self.DESTINATION, b'test message 2')
        client.ack(client.receiveFrame())
        client.unsubscribe((StompSpec.ID_HEADER, 'bla'))
        client.disconnect()

    def _test_4_integration_stomp(self, version):
        client = Stomp(self.getConfig(version))
        try:
            client.connect(host=VIRTUALHOST, versions=[version])
        except StompProtocolError as e:
            print('Broker does not support STOMP protocol %s. Skipping this test case. [%s]' % (e, version))
            return

        client.send(self.DESTINATION, b'test message 1')
        client.send(self.DESTINATION, b'test message 2')
        self.assertFalse(client.canRead(self.TIMEOUT))
        token = client.subscribe(self.DESTINATION, {StompSpec.ID_HEADER: 4711, StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
        self.assertTrue(client.canRead(self.TIMEOUT))
        client.ack(client.receiveFrame())
        self.assertTrue(client.canRead(self.TIMEOUT))
        client.ack(client.receiveFrame())
        self.assertFalse(client.canRead(self.TIMEOUT))
        client.unsubscribe(token)
        client.send(self.DESTINATION, b'test message 3', receipt='4711')
        self.assertTrue(client.canRead(self.TIMEOUT))
        self.assertEqual(client.receiveFrame(), StompFrame(StompSpec.RECEIPT, {StompSpec.RECEIPT_ID_HEADER: '4711'}))
        self.assertFalse(client.canRead(self.TIMEOUT))
        client.subscribe(self.DESTINATION, {StompSpec.ID_HEADER: 4711, StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
        self.assertTrue(client.canRead(self.TIMEOUT))
        client.ack(client.receiveFrame())
        self.assertFalse(client.canRead(self.TIMEOUT))
        client.disconnect(receipt='4712')
        self.assertEqual(client.receiveFrame(), StompFrame(StompSpec.RECEIPT, {StompSpec.RECEIPT_ID_HEADER: '4712'}))
        self.assertRaises(StompConnectionError, client.receiveFrame)
        client.connect(host=VIRTUALHOST)
        client.disconnect(receipt='4711')
        self.assertEqual(client.receiveFrame(), StompFrame(StompSpec.RECEIPT, {StompSpec.RECEIPT_ID_HEADER: '4711'}))
        client.close()
        self.assertRaises(StompConnectionError, client.canRead, 0)

    def test_4_integration_stomp_1_1(self):
        self._test_4_integration_stomp(StompSpec.VERSION_1_1)

    def test_4_integration_stomp_1_2(self):
        self._test_4_integration_stomp(StompSpec.VERSION_1_2)

    def test_5_integration_stomp_1_1_heartbeat(self):
        version = StompSpec.VERSION_1_1

        client = Stomp(self.getConfig(StompSpec.VERSION_1_1))
        self.assertEqual(client.lastReceived, None)
        self.assertEqual(client.lastSent, None)

        heartBeatPeriod = 100
        try:
            client.connect(host=VIRTUALHOST, heartBeats=(heartBeatPeriod, heartBeatPeriod), versions=[version])
        except StompProtocolError as e:
            print('Broker does not support STOMP protocol %s. Skipping this test case. [%s]' % (e, version))
            return

        self.assertTrue((time.time() - client.lastReceived) < 0.1)
        if not (client.serverHeartBeat and client.clientHeartBeat):
            print('broker does not support heart-beating. disconnecting ...')
            client.disconnect()
            client.close()
            return

        serverHeartBeatInSeconds = client.serverHeartBeat / 1000.0
        clientHeartBeatInSeconds = client.clientHeartBeat / 1000.0

        start = time.time()
        while (time.time() - start) < (2.5 * max(serverHeartBeatInSeconds, clientHeartBeatInSeconds)):
            time.sleep(0.5 * min(serverHeartBeatInSeconds, clientHeartBeatInSeconds))
            client.canRead(0)
            self.assertTrue((time.time() - client.lastReceived) < (2.0 * serverHeartBeatInSeconds))
            if (time.time() - client.lastSent) > (0.5 * clientHeartBeatInSeconds):
                client.beat()
                self.assertTrue((time.time() - client.lastSent) < 0.1)

        start = time.time()
        try:
            while not client.canRead(0.5 * clientHeartBeatInSeconds):
                pass
            if client.receiveFrame().command == StompSpec.ERROR:
                raise StompProtocolError()
        except (StompConnectionError, StompProtocolError):
            self.assertTrue((time.time() - start) < (3.0 * clientHeartBeatInSeconds))
            self.assertTrue((time.time() - client.lastReceived) < (2.0 * serverHeartBeatInSeconds))
            self.assertTrue((time.time() - client.lastSent) > clientHeartBeatInSeconds)
        else:
            raise
        client.close()

    def test_6_integration_stomp_1_1_encoding_and_escaping_headers(self):
        if BROKER == 'rabbitmq':
            print('Broker does not support unicode characters. Skipping this test case.')
            return

        version = StompSpec.VERSION_1_1
        client = Stomp(self.getConfig(version))
        try:
            client.connect(host=VIRTUALHOST, versions=[version])
        except StompProtocolError as e:
            print('Broker does not support STOMP protocol %s. Skipping this test case. [%s]' % (e, version))
            return

        key = b'fen\xc3\xaatre'.decode('utf-8')
        value = b'\xc2\xbfqu\xc3\xa9 tal?'.decode('utf-8')
        headers = {key: value}
        client.send(self.DESTINATION, body=b'test message 1', headers=headers)
        self.assertFalse(client.canRead(self.TIMEOUT))
        token = client.subscribe(self.DESTINATION, {StompSpec.ID_HEADER: 4711, StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
        self.assertTrue(client.canRead(self.TIMEOUT))
        frame = client.receiveFrame()
        client.ack(frame)
        self.assertEqual(frame.version, version)
        self.assertEqual(frame.headers[key], headers[key])
        self.assertFalse(client.canRead(self.TIMEOUT))
        client.unsubscribe(token)
        client.disconnect(receipt='4712')


class SimpleStompIntegrationTestSSL(SimpleStompIntegrationTest):
    def getConfig(self, version, port=PORT_SSL):
        sslContext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # It's good practice to disable insecure protocols by default
        sslContext.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_SSLv3
        # Disable host name and cert checking for the tests.
        sslContext.check_hostname = False
        sslContext.verify_mode = ssl.CERT_NONE

        return StompConfig(
            'ssl://%s:%s' % (HOST, port),
            login=LOGIN,
            passcode=PASSCODE,
            version=version,
            sslContext=sslContext
        )


if __name__ == '__main__':
    unittest.main()
