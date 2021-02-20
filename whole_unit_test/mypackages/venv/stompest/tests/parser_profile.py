import itertools
from random import choice, randrange
from string import printable

from stompest._backwards import binaryType
from stompest.protocol import StompFrame, StompParser, StompSpec
from stompest.protocol.frame import StompHeartBeat

N = 10000
BLOCK_LENGTH = 1000
BODY_BLOCKS = 1
HEADER_LENGTH = 10
SLICE = 4096

def createRange(n):
    j = 0
    while j < n:
        yield j
        j += 1

TEXT_BLOCK = ''.join(choice(printable) for _ in createRange(BLOCK_LENGTH)).encode()
textFrame = StompFrame(
    command='MESSAGE'
    , headers=dict(('some key %d' % j, 'some value %d' % j) for j in createRange(HEADER_LENGTH))
    , body=BODY_BLOCKS * TEXT_BLOCK
    , version=StompSpec.VERSION_1_1
)
BINARY_BLOCK = memoryview(bytearray(randrange(256) for _ in createRange(BLOCK_LENGTH))).tobytes()
binaryFrame = StompFrame(
    command='MESSAGE'
    , headers={StompSpec.CONTENT_LENGTH_HEADER: (BODY_BLOCKS * BLOCK_LENGTH)}
    , body=BODY_BLOCKS * BINARY_BLOCK
)
heartBeatFrame = StompHeartBeat()

def testText():
    pass

def main():
    parser = StompParser(version=StompSpec.VERSION_1_2)
    frame = binaryType(binaryFrame) + binaryType(textFrame) + binaryType(heartBeatFrame)
    for _ in createRange(N):
        for j in itertools.count():
            packet = frame[j * SLICE:(j + 1) * SLICE]
            if not packet:
                break
            parser.add(packet)
        while parser.canRead():
            parser.get()

if __name__ == '__main__':
    import cProfile
    import pstats
    cProfile.run('main()', 'parserstats')
    pstats.Stats('parserstats').strip_dirs().sort_stats('cumtime').print_stats()
