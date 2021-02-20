import unittest

from stompest._backwards import binaryType, textType
from stompest.error import StompFrameError
from stompest.protocol import commands, StompFrame, StompParser, StompSpec
from stompest.protocol.frame import StompHeartBeat

class StompParserTest(unittest.TestCase):
    def test_frame_parse_succeeds(self):
        frame = StompFrame(
            StompSpec.SEND,
            {'foo': 'bar', 'hello ': 'there-world with space ', 'empty-value':'', '':'empty-header', StompSpec.DESTINATION_HEADER: '/queue/blah'},
            b'some stuff\nand more'
        )

        parser = StompParser()
        parser.add(binaryType(frame))
        self.assertEqual(parser.get(), frame)
        self.assertIsNone(parser.get())

    def test_duplicate_headers(self):
        command = StompSpec.SEND
        rawFrame = '%s\nfoo:bar1\nfoo:bar2\n\nsome stuff\nand more\x00' % (command,)

        parser = StompParser()
        parser.add(rawFrame.encode())
        parsedFrame = parser.get()
        self.assertIsNone(parser.get())

        self.assertEqual(parsedFrame.command, command)
        self.assertEqual(parsedFrame.headers, {'foo': 'bar1'})
        self.assertEqual(parsedFrame.rawHeaders, [('foo', 'bar1'), ('foo', 'bar2')])
        self.assertEqual(parsedFrame.body, b'some stuff\nand more')

    def test_invalid_command(self):
        messages = [b'RECEIPT\nreceipt-id:message-12345\n\n\x00', b'NACK\nsubscription:0\nmessage-id:007\n\n\x00']
        parser = StompParser(StompSpec.VERSION_1_0)
        parser.add(messages[0])
        self.assertRaises(StompFrameError, parser.add, messages[1])
        self.assertEqual(parser.get(), StompFrame(StompSpec.RECEIPT, rawHeaders=(('receipt-id', 'message-12345'),)))
        self.assertFalse(parser.canRead())
        self.assertIsNone(parser.get())
        parser = StompParser(StompSpec.VERSION_1_1)
        parser.add(messages[1])
        self.assertEqual(parser.get(), StompFrame(command='NACK', rawHeaders=(('subscription', '0'), ('message-id', '007')), version=StompSpec.VERSION_1_1))

    def test_reset_succeeds(self):
        frame = StompFrame(
            command=StompSpec.SEND,
            headers={'foo': 'bar', 'hello ': 'there-world with space ', 'empty-value':'', '':'empty-header', StompSpec.DESTINATION_HEADER: '/queue/blah'},
            body=b'some stuff\nand more'
        )
        parser = StompParser()

        parser.add(binaryType(frame))
        parser.reset()
        self.assertIsNone(parser.get())
        parser.add(binaryType(frame)[:20])
        self.assertIsNone(parser.get())

    def test_frame_without_header_or_body_succeeds(self):
        parser = StompParser()
        parser.add(binaryType(commands.disconnect()))
        self.assertEqual(parser.get(), commands.disconnect())

    def test_frames_with_optional_newlines_succeeds(self):
        parser = StompParser()
        disconnect = commands.disconnect()
        frame = b'\n' + binaryType(disconnect) + b'\n'
        parser.add(2 * frame)
        for _ in range(2):
            self.assertEqual(parser.get(), disconnect)
        self.assertIsNone(parser.get())

    def test_frames_with_heart_beats_succeeds(self):
        parser = StompParser(version=StompSpec.VERSION_1_1)
        disconnect = commands.disconnect()
        frame = b'\n' + binaryType(disconnect) + b'\n'
        parser.add(2 * frame)
        frames = []
        while parser.canRead():
            frames.append(parser.get())
        self.assertEqual(frames, [StompHeartBeat(), disconnect, StompHeartBeat(), StompHeartBeat(), disconnect, StompHeartBeat()])
        self.assertIsNone(parser.get())

    def test_get_returns_None_if_not_done(self):
        parser = StompParser()
        self.assertEqual(None, parser.get())
        parser.add(StompSpec.CONNECT.encode())
        self.assertEqual(None, parser.get())

    def test_add_throws_FrameError_on_invalid_command(self):
        parser = StompParser()

        self.assertRaises(StompFrameError, parser.add, b'HELLO\n\n\x00')
        self.assertFalse(parser.canRead())
        parser.add(('%s\n\n\x00' % StompSpec.DISCONNECT).encode())
        self.assertEqual(StompFrame(StompSpec.DISCONNECT), parser.get())
        self.assertFalse(parser.canRead())

    def test_add_throws_FrameError_on_header_line_missing_separator(self):
        parser = StompParser()
        parser.add(('%s\n' % StompSpec.SEND).encode('utf-8'))
        self.assertRaises(StompFrameError, parser.add, b'no separator\n\n\x00')

    def test_colon_in_header_value(self):
        parser = StompParser()
        parser.add(('%s\nheader:with:colon\n\n\x00' % StompSpec.DISCONNECT).encode())
        self.assertEqual(parser.get().headers['header'], 'with:colon')

    def test_no_newline(self):
        headers = {'x': 'y'}
        body = b'testing 1 2 3'
        frameBytes = binaryType(StompFrame(StompSpec.MESSAGE, headers, body))
        self.assertTrue(frameBytes.endswith(b'\x00'))
        parser = StompParser()
        parser.add(frameBytes)
        frame = parser.get()
        self.assertEqual(StompSpec.MESSAGE, frame.command)
        self.assertEqual(headers, frame.headers)
        self.assertEqual(body, frame.body)
        self.assertEqual(parser.get(), None)

    def test_binary_body(self):
        body = b'\xf0\x00\x0a\x09'
        headers = {StompSpec.CONTENT_LENGTH_HEADER: textType(len(body))}
        frame = StompFrame(StompSpec.MESSAGE, body=body)
        frame.setContentLength()
        frameBytes = binaryType(frame)
        self.assertTrue(frameBytes.endswith(b'\x00'))
        parser = StompParser()
        for _ in range(2):
            for (j, _) in enumerate(frameBytes):
                parser.add(frameBytes[j:j + 1])
            frame = parser.get()
            self.assertEqual(StompSpec.MESSAGE, frame.command)
            self.assertEqual(headers, frame.headers)
            self.assertEqual(body, frame.body)
        self.assertEqual(parser.get(), None)

        frames = 2 * frameBytes
        split = len(frameBytes) - 1
        chunks = [frames[:split], frames[split:]]
        parser.add(chunks.pop(0))
        self.assertEqual(parser.get(), None)
        parser.add(chunks.pop(0))
        self.assertEqual(parser.get(), frame)
        self.assertEqual(parser.get(), frame)
        self.assertEqual(parser.get(), None)

        split = len(frameBytes) + 1
        chunks = [frames[:split], frames[split:]]
        parser.add(chunks.pop(0))
        self.assertEqual(parser.get(), frame)
        self.assertEqual(parser.get(), None)
        parser.add(chunks.pop(0))
        self.assertEqual(parser.get(), frame)
        self.assertEqual(parser.get(), None)

    def test_binary_body_invalid_eof(self):
        parser = StompParser()
        body = b'MESSAGE\ncontent-length:4\n\n\xf0\x00\n\t\x00'
        parser.add(body)
        self.assertEqual(binaryType(parser.get()), body)
        self.assertRaises(StompFrameError, parser.add, b'MESSAGE\ncontent-length:4\n\n\xf0\n\t\xff\x01\n\nCONNECT\n\x00') # \x00 behind invalid EOF
        parser.add(body)
        self.assertEqual(binaryType(parser.get()), body)
        self.assertRaises(StompFrameError, parser.add, b'MESSAGE\ncontent-length:4\n\n\xf0\n\t\xff\x01\x00') # \x00 just behind invalid EOF
        parser.add(body)
        self.assertEqual(binaryType(parser.get()), body)
        self.assertRaises(StompFrameError, parser.add, b'MESSAGE\ncontent-length:4\n\n\xf0\x00\n\t\x01') # \x00 before invalid EOF
        parser.add(body)
        self.assertEqual(binaryType(parser.get()), body)
        self.assertRaises(StompFrameError, parser.add, b'MESSAGE\ncontent-length:4\n\n\xf0\n\t\x00\x01') # \x00 just before invalid EOF
        parser.add(body)
        self.assertEqual(binaryType(parser.get()), body)

    def test_body_allowed_commands(self):
        head = binaryType(commands.disconnect()).rstrip(StompSpec.FRAME_DELIMITER.encode())
        for (version, bodyAllowed) in [
            (StompSpec.VERSION_1_0, True),
            (StompSpec.VERSION_1_1, False),
            (StompSpec.VERSION_1_2, False)
        ]:
            parser = StompParser(version)
            parser.add(head)
            parser.add(b'ouch!')
            try:
                parser.add(StompSpec.FRAME_DELIMITER.encode())
            except StompFrameError:
                if bodyAllowed:
                    raise
            except:
                raise
            else:
                if not bodyAllowed:
                    raise

    def test_strip_line_delimiter(self):
        queue = '/queue/test'
        frame = commands.send(queue)
        frameWithStripLineDelimiter = commands.send(queue + '\r')
        for (version, stripLineDelimiter) in [
            (StompSpec.VERSION_1_0, False),
            (StompSpec.VERSION_1_1, False),
            (StompSpec.VERSION_1_2, True)
        ]:
            parser = StompParser(version)
            parser.add(binaryType(frameWithStripLineDelimiter))
            self.assertEqual(parser.get(), frame if stripLineDelimiter else frameWithStripLineDelimiter)

        frameWithCarriageReturn = commands.send(queue + '\r', version=StompSpec.VERSION_1_2)
        parser = StompParser(StompSpec.VERSION_1_2)
        parser.add(binaryType(frameWithCarriageReturn))
        self.assertEqual(parser.get().headers[StompSpec.DESTINATION_HEADER], queue + '\r')

    def test_add_multiple_frames_per_read(self):
        body1 = b'boo'
        body2 = b'hoo'
        headers = {'x': 'y'}
        frameBytes = binaryType(StompFrame(StompSpec.MESSAGE, headers, body1)) + binaryType(StompFrame(StompSpec.MESSAGE, headers, body2))
        parser = StompParser()
        parser.add(frameBytes)

        frame = parser.get()
        self.assertEqual(StompSpec.MESSAGE, frame.command)
        self.assertEqual(headers, frame.headers)
        self.assertEqual(body1, frame.body)

        frame = parser.get()
        self.assertEqual(StompSpec.MESSAGE, frame.command)
        self.assertEqual(headers, frame.headers)
        self.assertEqual(body2, frame.body)

        self.assertIsNone(parser.get())

    def test_decode(self):
        key = b'fen\xc3\xaatre'.decode('utf-8')
        value = b'\xc2\xbfqu\xc3\xa9 tal?'.decode('utf-8')
        headers = {key: value}
        frameBytes = binaryType(StompFrame(command=StompSpec.DISCONNECT, headers=headers, version=StompSpec.VERSION_1_1))

        parser = StompParser(version=StompSpec.VERSION_1_1)
        parser.add(frameBytes)
        frame = parser.get()
        self.assertEqual(frame.headers, headers)

        parser = StompParser(version=StompSpec.VERSION_1_0)
        self.assertRaises(UnicodeDecodeError, parser.add, frameBytes)

    def test_unescape(self):
        frameBytes = ("""%s
\\n\\\\:\\c\t\\n

\x00""" % StompSpec.DISCONNECT).encode()

        for version in (StompSpec.VERSION_1_1, StompSpec.VERSION_1_2):
            parser = StompParser(version=version)
            parser.add(frameBytes)
            frame = parser.get()
            self.assertEqual(frame.headers, {'\n\\': ':\t\n'})

        parser = StompParser(version=StompSpec.VERSION_1_0)
        parser.add(frameBytes)
        self.assertEqual(parser.get(), StompFrame(command='DISCONNECT', rawHeaders=[('\\n\\\\', '\\c\t\\n')]))

        frameBytes = ("""%s
\\n\\\\:\\c\\t

\x00""" % StompSpec.DISCONNECT).encode()

        for version in (StompSpec.VERSION_1_1, StompSpec.VERSION_1_2):
            self.assertRaises(StompFrameError, StompParser(version=version).add, frameBytes)

        parser = StompParser(version=StompSpec.VERSION_1_0)
        parser.add(frameBytes)
        self.assertEqual(parser.get(), StompFrame(command='DISCONNECT', rawHeaders=[('\\n\\\\', '\\c\\t')]))

        frameBytes = ("""%s
\\n\\\\:\\c\t\\r

\x00""" % StompSpec.DISCONNECT).encode()

        parser = StompParser(version=StompSpec.VERSION_1_2)
        parser.add(frameBytes)
        frame = parser.get()
        self.assertEqual(frame.headers, {'\n\\': ':\t\r'})

    def test_dont_unescape_bad_characters(self):
        parser = StompParser(StompSpec.VERSION_1_2)
        frame = commands.send('*queue')
        parser.add(binaryType(frame))
        self.assertEqual(parser.get(), frame)
        for badCharacter in (b'\r', b'\n', b'\c', b'\\', b':', b'\\h'):
            self.assertRaises(StompFrameError, parser.add, binaryType(frame).replace(b'*', badCharacter))
        self.assertRaises(StompFrameError, parser.add, binaryType(commands.send('queue\\')))
        self.assertIsNone(parser.get())

    def test_keep_first_of_repeated_headers(self):
        parser = StompParser()
        parser.add(("""
%s
repeat:1
repeat:2

\x00""" % StompSpec.CONNECT).encode())
        frame = parser.get()
        self.assertEqual(frame.headers['repeat'], '1')

if __name__ == '__main__':
    unittest.main()
