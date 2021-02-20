import unittest

from stompest.error import StompProtocolError
from stompest.protocol import commands, StompFrame, StompSession, StompSpec

class StompSessionTest(unittest.TestCase):
    def test_session_init(self):
        session = StompSession(check=False)
        self.assertEqual(session.version, StompSpec.DEFAULT_VERSION)
        session.send('', b'', {})
        session.subscribe('bla1', {'bla2': 'bla3'})
        session.unsubscribe((StompSpec.DESTINATION_HEADER, 'bla1'))

        session = StompSession()
        self.assertRaises(StompProtocolError, lambda: session.send('', b'', {}))
        self.assertRaises(StompProtocolError, lambda: session.subscribe('bla1', {'bla2': 'bla3'}))
        self.assertRaises(StompProtocolError, lambda: session.unsubscribe((StompSpec.DESTINATION_HEADER, 'bla1')))

        session = StompSession(StompSpec.VERSION_1_1)
        self.assertEqual(session.version, StompSpec.VERSION_1_1)

        self.assertRaises(StompProtocolError, lambda: StompSession(version='1.3'))
        self.assertRaises(StompProtocolError, lambda: session.send('', '', {}))

    def test_session_connect(self):
        session = StompSession(StompSpec.VERSION_1_0, check=False)
        self.assertEqual(session.version, StompSpec.VERSION_1_0)
        for attribute in (session.server, session.id, session.lastSent, session.lastReceived):
            self.assertEqual(attribute, None)
        for attribute in (session.clientHeartBeat, session.serverHeartBeat):
            self.assertEqual(attribute, 0)
        self.assertEqual(session.state, StompSession.DISCONNECTED)
        frame = session.connect(login='', passcode='')
        self.assertEqual(session.state, StompSession.CONNECTING)
        self.assertEqual(frame, commands.connect(login='', passcode='', versions=None))
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SESSION_HEADER: 'hi'}))
        self.assertEqual(session.state, StompSession.CONNECTED)
        self.assertEqual(session.version, StompSpec.VERSION_1_0)
        self.assertEqual(session.server, None)
        self.assertEqual(session.id, 'hi')
        frame = session.disconnect()
        self.assertEqual(frame, commands.disconnect())
        session.close()
        self.assertEqual(session.server, None)
        self.assertEqual(session.id, None)
        self.assertEqual(session.state, StompSession.DISCONNECTED)
        self.assertRaises(StompProtocolError, session.connect, login='', passcode='', versions=[StompSpec.VERSION_1_1])

        session = StompSession(version=StompSpec.VERSION_1_1, check=False)
        self.assertEqual(session.version, StompSpec.VERSION_1_1)
        frame = session.connect(login='', passcode='')
        self.assertEqual(frame, commands.connect('', '', {}, [StompSpec.VERSION_1_0, StompSpec.VERSION_1_1]))
        self.assertEqual(session.state, StompSession.CONNECTING)
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SERVER_HEADER: 'moon', StompSpec.SESSION_HEADER: '4711', StompSpec.VERSION_HEADER: StompSpec.VERSION_1_1}))
        self.assertEqual(session.state, StompSession.CONNECTED)
        self.assertEqual(session.server, 'moon')
        self.assertEqual(session.id, '4711')
        self.assertEqual(session.state, StompSession.CONNECTED)
        self.assertEqual(session.version, StompSpec.VERSION_1_1)
        frame = session.disconnect('4711')
        self.assertEqual(frame, commands.disconnect('4711'))
        session.close()
        self.assertEqual(session.server, None)
        self.assertEqual(session.id, None)
        self.assertEqual(session.state, StompSession.DISCONNECTED)

        session.connect(login='', passcode='', versions=[StompSpec.VERSION_1_0, StompSpec.VERSION_1_1])
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SESSION_HEADER: '4711'}))
        self.assertEqual(session.state, StompSession.CONNECTED)
        self.assertEqual(session.server, None)
        self.assertEqual(session.id, '4711')
        self.assertEqual(session.version, StompSpec.VERSION_1_0)
        frame = session.disconnect()
        session.close()
        self.assertEqual(frame, commands.disconnect())
        self.assertEqual(session.server, None)
        self.assertEqual(session.id, None)
        self.assertEqual(session.state, StompSession.DISCONNECTED)
        self.assertEqual(session.version, StompSpec.VERSION_1_1)

        session = StompSession(version=StompSpec.VERSION_1_1, check=False)
        frame = session.connect(login='', passcode='', versions=[StompSpec.VERSION_1_1])
        self.assertEqual(frame, commands.connect('', '', {}, [StompSpec.VERSION_1_1]))
        self.assertEqual(session._versions, [StompSpec.VERSION_1_1])
        self.assertEqual(session.state, StompSession.CONNECTING)
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SERVER_HEADER: 'moon', StompSpec.SESSION_HEADER: '4711', StompSpec.VERSION_HEADER: StompSpec.VERSION_1_1}))
        self.assertEqual(session.clientHeartBeat, 0)
        self.assertEqual(session.serverHeartBeat, 0)
        self.assertEqual(session.state, StompSession.CONNECTED)
        self.assertEqual(session._versions, [StompSpec.VERSION_1_0, StompSpec.VERSION_1_1])
        self.assertEqual(session.version, StompSpec.VERSION_1_1)
        session.disconnect('4711')
        session.close()
        self.assertEqual(session.state, StompSession.DISCONNECTED)

        session = StompSession(version=StompSpec.VERSION_1_1, check=False)
        frame = session.connect(login='', passcode='', versions=[StompSpec.VERSION_1_1], heartBeats=(1, 2))
        self.assertEqual(frame, commands.connect('', '', {}, [StompSpec.VERSION_1_1], heartBeats=(1, 2)))
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SERVER_HEADER: 'moon', StompSpec.SESSION_HEADER: '4711', StompSpec.VERSION_HEADER: StompSpec.VERSION_1_1, StompSpec.HEART_BEAT_HEADER: '3,4'}))
        self.assertEqual(session.clientHeartBeat, 4)
        self.assertEqual(session.serverHeartBeat, 3)
        session.disconnect()
        session.close()
        self.assertEqual(session.clientHeartBeat, 0)
        self.assertEqual(session.serverHeartBeat, 0)

        session.connect(login='', passcode='', versions=[StompSpec.VERSION_1_0, StompSpec.VERSION_1_1])
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SESSION_HEADER: '4711'}))
        self.assertEqual(session.clientHeartBeat, 0)
        self.assertEqual(session.serverHeartBeat, 0)
        session.disconnect()
        session.close()

        session.connect(login='', passcode='', versions=[StompSpec.VERSION_1_0, StompSpec.VERSION_1_1])
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SESSION_HEADER: '4711', StompSpec.HEART_BEAT_HEADER: '3,4'}))
        self.assertEqual(session.clientHeartBeat, 0)
        self.assertEqual(session.serverHeartBeat, 0)
        session.disconnect()
        session.close()

    def test_session_subscribe(self):
        session = StompSession(check=False)
        headers = {'bla2': 'bla3'}
        frame, token = session.subscribe('bla1', headers, receipt='4711')
        self.assertEqual((frame, token), commands.subscribe('bla1', headers, '4711', version=StompSpec.VERSION_1_0))

        self.assertEqual(token, (StompSpec.DESTINATION_HEADER, 'bla1'))
        self.assertEqual(token, commands.message(StompFrame(StompSpec.MESSAGE, dict([token, (StompSpec.MESSAGE_ID_HEADER, '4711')]))))

        headersWithId1 = {StompSpec.ID_HEADER: 'bla2', 'bla3': 'bla4'}
        frame, tokenWithId1 = session.subscribe('bla2', headersWithId1)
        self.assertEqual((frame, tokenWithId1), commands.subscribe('bla2', headersWithId1, version=StompSpec.VERSION_1_0))
        self.assertEqual(tokenWithId1, (StompSpec.ID_HEADER, 'bla2'))
        self.assertEqual(tokenWithId1, commands.message(StompFrame(StompSpec.MESSAGE, dict([(StompSpec.SUBSCRIPTION_HEADER, 'bla2'), (StompSpec.DESTINATION_HEADER, 'bla2'), (StompSpec.MESSAGE_ID_HEADER, '4711')]))))

        headersWithId2 = {StompSpec.ID_HEADER: 'bla3', 'bla4': 'bla5'}
        session.subscribe('bla2', headersWithId2)

        subscriptions = list(session.replay())
        self.assertEqual(subscriptions, [('bla1', headers, '4711', None), ('bla2', headersWithId1, None, None), ('bla2', headersWithId2, None, None)])
        self.assertEqual(list(session.replay()), [])

        context = object()
        session.subscribe('bla2', headersWithId2, context=context)
        self.assertEqual(list(session.replay()), [('bla2', headersWithId2, None, context)])
        session.subscribe('bla2', headersWithId2)
        self.assertRaises(StompProtocolError, session.subscribe, 'bla2', headersWithId2)
        self.assertEqual(list(session.replay()), [('bla2', headersWithId2, None, None)])
        session.subscribe('bla2', headersWithId2)
        session.disconnect()
        session.close(flush=False)
        self.assertEqual(list(session.replay()), [('bla2', headersWithId2, None, None)])
        session.subscribe('bla2', headersWithId2)
        session.close(flush=True)
        self.assertEqual(list(session.replay()), [])

        subscriptionsWithoutId1 = [('bla1', headers, None, None), ('bla2', headersWithId2, None, None)]

        s = [session.subscribe(dest, headers_) for dest, headers_, _, _ in subscriptions]
        session.unsubscribe(s[1][1])
        self.assertEqual(list(session.replay()), subscriptionsWithoutId1)

        subscriptionWithId2 = [('bla2', headersWithId2, None, None)]

        s = [session.subscribe(dest, headers_) for dest, headers_, _, _ in subscriptionsWithoutId1]
        session.unsubscribe(s[0][1])
        self.assertEqual(list(session.replay()), subscriptionWithId2)

        session.disconnect()

        session = StompSession(check=False)
        session.connect(login='', passcode='')
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SESSION_HEADER: 'hi'}))

        session.subscribe('bla1', headers)
        self.assertRaises(StompProtocolError, lambda: session.unsubscribe((StompSpec.ID_HEADER, 'blub')))
        self.assertRaises(StompProtocolError, lambda: session.unsubscribe(('bla', 'blub')))

        frame, token = session.subscribe('bla2', headersWithId1)
        session.subscribe('bla2', headersWithId2)
        session.unsubscribe(token)
        self.assertRaises(StompProtocolError, lambda: session.unsubscribe(token))

        session = StompSession(version=StompSpec.VERSION_1_1, check=False)
        session.connect(login='', passcode='')
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SERVER_HEADER: 'moon', StompSpec.SESSION_HEADER: '4711', StompSpec.VERSION_HEADER: StompSpec.VERSION_1_1}))

        self.assertRaises(StompProtocolError, lambda: session.subscribe('bla1', headers))
        self.assertRaises(StompProtocolError, lambda: session.unsubscribe((StompSpec.DESTINATION_HEADER, 'bla1')))
        frame, token = session.subscribe('bla2', headersWithId1)
        session.subscribe('bla2', headersWithId2)
        session.unsubscribe(token)
        self.assertRaises(StompProtocolError, lambda: session.unsubscribe(token))

        subscriptions = list(session.replay())
        self.assertEqual(subscriptions, subscriptionWithId2)

        session.subscribe('bla2', headersWithId2)
        session.close(flush=True)
        self.assertEqual(list(session.replay()), [])

    def test_session_disconnect(self):
        session = StompSession(StompSpec.VERSION_1_1)
        session.connect(login='', passcode='')
        session.connected(StompFrame(StompSpec.CONNECTED, {StompSpec.SESSION_HEADER: 'hi'}))
        headers = {StompSpec.ID_HEADER: 4711}
        session.subscribe('bla', headers)
        frame = session.disconnect(receipt='4711')
        self.assertEqual(frame, commands.disconnect(receipt='4711'))
        self.assertEqual(session.state, session.DISCONNECTING)
        session.close(flush=False)
        self.assertEqual(session.state, session.DISCONNECTED)
        self.assertEqual(list(session.replay()), [('bla', headers, None, None)])
        self.assertEqual(list(session.replay()), [])

        self.assertRaises(StompProtocolError, session.disconnect)

    def test_session_nack(self):
        session = StompSession(version=StompSpec.VERSION_1_1, check=False)
        frame_ = lambda h: StompFrame(StompSpec.MESSAGE, h, version=StompSpec.VERSION_1_1)
        for headers in [
            {StompSpec.MESSAGE_ID_HEADER: '4711', StompSpec.SUBSCRIPTION_HEADER: 'bla'},
            {StompSpec.MESSAGE_ID_HEADER: '4711', StompSpec.SUBSCRIPTION_HEADER: 'bla', 'foo': 'bar'}
        ]:
            self.assertEqual(session.nack(frame_(headers)), commands.nack(frame_(headers)))

        headers = {StompSpec.MESSAGE_ID_HEADER: '4711', StompSpec.SUBSCRIPTION_HEADER: 'bla'}
        self.assertEqual(session.nack(frame_(headers), receipt='4711'), commands.nack(frame_(headers), receipt='4711'))

        self.assertRaises(StompProtocolError, session.nack, frame_({}))
        self.assertRaises(StompProtocolError, session.nack, frame_({StompSpec.MESSAGE_ID_HEADER: '4711'}))
        self.assertRaises(StompProtocolError, session.nack, frame_({StompSpec.SUBSCRIPTION_HEADER: 'bla'}))

        session = StompSession(version=StompSpec.VERSION_1_1)
        self.assertRaises(StompProtocolError, lambda: session.nack(frame_({StompSpec.MESSAGE_ID_HEADER: '4711', StompSpec.SUBSCRIPTION_HEADER: 'bla'})))

    def test_session_transaction(self):
        session = StompSession(check=False)

        transaction = session.transaction()
        headers = {StompSpec.TRANSACTION_HEADER: transaction, StompSpec.RECEIPT_HEADER: 'bla'}
        frame = session.begin(transaction, receipt='bla')
        self.assertEqual(frame, commands.begin(transaction, receipt='bla'))
        self.assertEqual(frame, StompFrame(StompSpec.BEGIN, headers))
        headers.pop(StompSpec.RECEIPT_HEADER)
        self.assertRaises(StompProtocolError, session.begin, transaction)
        frame = session.abort(transaction)
        self.assertEqual(frame, commands.abort(transaction))
        self.assertEqual(frame, StompFrame(StompSpec.ABORT, headers))
        self.assertRaises(StompProtocolError, session.abort, transaction)
        self.assertRaises(StompProtocolError, session.commit, transaction)

        transaction = session.transaction(4711)
        headers = {StompSpec.TRANSACTION_HEADER: '4711'}
        frame = session.begin(transaction)
        self.assertEqual(frame, commands.begin(transaction))
        self.assertEqual(frame, StompFrame(StompSpec.BEGIN, headers))
        frame = session.commit(transaction)
        self.assertEqual(frame, commands.commit(transaction))
        self.assertEqual(frame, StompFrame(StompSpec.COMMIT, headers))
        self.assertRaises(StompProtocolError, session.commit, transaction)
        self.assertRaises(StompProtocolError, session.abort, transaction)

        session = StompSession()
        self.assertRaises(StompProtocolError, session.begin, 4711)
        self.assertRaises(StompProtocolError, session.abort, None)
        self.assertRaises(StompProtocolError, session.commit, None)

if __name__ == '__main__':
    unittest.main()
