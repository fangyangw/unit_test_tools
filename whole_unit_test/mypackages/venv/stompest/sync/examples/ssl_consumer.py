import ssl
from stompest.config import StompConfig
from stompest.protocol import StompSpec
from stompest.sync import Stomp

context = ssl.create_default_context()
# Disable cert validation for demo only
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

CONFIG = StompConfig('ssl://localhost:61612', sslContext=context)
QUEUE = '/queue/test'

if __name__ == '__main__':
    client = Stomp(CONFIG)
    client.connect()
    client.subscribe(QUEUE, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
    while True:
        frame = client.receiveFrame()
        print('Got %s' % frame.info())
        client.ack(frame)
    client.disconnect()
