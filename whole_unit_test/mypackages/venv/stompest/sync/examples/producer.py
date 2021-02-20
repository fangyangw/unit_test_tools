from stompest.config import StompConfig
from stompest.sync import Stomp

CONFIG = StompConfig('tcp://localhost:61613')
QUEUE = '/queue/test'

if __name__ == '__main__':
    client = Stomp(CONFIG)
    client.connect()
    client.send(QUEUE, 'test message 1'.encode())
    client.send(QUEUE, 'test message 2'.encode())
    client.disconnect()
