import binascii
import itertools
import logging
import select # @UnresolvedImport
import unittest

from stompest._backwards import binaryType, makeBytesFromSequence
from stompest.error import StompConnectionError
from stompest.protocol import StompFrame, StompSpec
from stompest.sync.transport import StompFrameTransport

from stompest.tests import mock

logging.basicConfig(level=logging.DEBUG)

HOST = 'fakeHost'
PORT = 61613

class StompFrameTransportTest(unittest.TestCase):
    def _generate_bytes(self, stream):
        for byte in stream:
            yield byte

    def _get_receive_mock(self, stream):
        transport = StompFrameTransport(HOST, PORT)
        connected = transport._connected = mock.Mock()
        connected.return_value = True
        socket = transport._socket = mock.Mock()
        stream = self._generate_bytes(stream)
        socket.recv = mock.Mock(wraps=lambda size: makeBytesFromSequence(itertools.islice(stream, size)))
        return transport

    def _get_send_mock(self):
        transport = StompFrameTransport(HOST, PORT)
        connected = transport._connected = mock.Mock()
        connected.return_value = True
        transport._socket = mock.Mock()
        return transport

    def test_send(self):
        frame = StompFrame(StompSpec.MESSAGE)

        transport = self._get_send_mock()
        transport.send(frame)
        self.assertEqual(1, transport._socket.sendall.call_count)
        args, _ = transport._socket.sendall.call_args
        self.assertEqual(binaryType(frame), args[0])

    def test_send_not_connected_raises(self):
        frame = StompFrame(StompSpec.MESSAGE)

        transport = self._get_send_mock()
        transport._connected.return_value = False
        self.assertRaises(StompConnectionError, transport.send, frame)
        self.assertEqual(0, transport._socket.sendall.call_count)

    def test_receive(self):
        headers = {'x': 'y'}
        body = b'testing 1 2 3'
        frame = StompFrame(StompSpec.MESSAGE, headers, body)
        transport = self._get_receive_mock(binaryType(frame))
        frame_ = transport.receive()
        self.assertEqual(frame, frame_)
        self.assertEqual(1, transport._socket.recv.call_count)

        self.assertRaises(StompConnectionError, transport.receive)
        self.assertEqual(transport._socket, None)

    def test_receive_not_connected_raises_and_removes_socket(self):
        transport = self._get_receive_mock(b'Hi')
        transport._connected.return_value = False
        self.assertRaises(StompConnectionError, transport.receive)
        self.assertEqual(None, transport._socket)

    def test_receive_multiple_frames_extra_newlines(self):
        headers = {'x': 'y'}
        body = b'testing 1 2 3'
        frame = StompFrame(StompSpec.MESSAGE, headers, body)

        transport = self._get_receive_mock(b'\n\n' + binaryType(frame) + b'\n' + binaryType(frame) + b'\n')
        frame_ = transport.receive()
        self.assertEqual(frame, frame_)
        frame_ = transport.receive()
        self.assertEqual(frame, frame_)
        self.assertEqual(1, transport._socket.recv.call_count)

        self.assertRaises(StompConnectionError, transport.receive)
        self.assertEqual(transport._socket, None)

    def test_receive_binary(self):
        body = binascii.a2b_hex('f0000a09')
        headers = {StompSpec.CONTENT_LENGTH_HEADER: str(len(body))}
        frame = StompFrame(StompSpec.MESSAGE, headers, body)

        transport = self._get_receive_mock(binaryType(frame))
        frame_ = transport.receive()
        self.assertEqual(frame, frame_)
        self.assertEqual(1, transport._socket.recv.call_count)

        self.assertRaises(StompConnectionError, transport.receive)
        self.assertEqual(transport._socket, None)

    def test_receive_multiple_frames_per_read(self):
        body1 = b'boo'
        body2 = b'hoo'
        headers = {'x': 'y'}
        frameBytes = binaryType(StompFrame(StompSpec.MESSAGE, headers, body1)) + binaryType(StompFrame(StompSpec.MESSAGE, headers, body2))

        transport = self._get_receive_mock(frameBytes)

        frame = transport.receive()
        self.assertEqual(StompSpec.MESSAGE, frame.command)
        self.assertEqual(headers, frame.headers)
        self.assertEqual(body1, frame.body)
        self.assertEqual(1, transport._socket.recv.call_count)

        frame = transport.receive()
        self.assertEqual(StompSpec.MESSAGE, frame.command)
        self.assertEqual(headers, frame.headers)
        self.assertEqual(body2, frame.body)
        self.assertEqual(1, transport._socket.recv.call_count)

        self.assertRaises(StompConnectionError, transport.receive)
        self.assertEqual(transport._socket, None)

    @mock.patch('select.select')
    def _test_can_connect_eintr_retries_connection(self, select_call):
        select_call.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        transport = self._get_receive_mock(b'test')
        def raise_eintr_once(*args): # @UnusedVariable
            select_call.side_effect = None
            raise select.error(4, 'Interrupted system call')
        select_call.side_effect = raise_eintr_once

        transport.canRead()
        self.assertEqual(2, select_call.call_count)

if __name__ == '__main__':
    unittest.main()
