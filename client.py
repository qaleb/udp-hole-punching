#!/usr/bin/env python3
"""UDP hole punching client."""
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import sys


class ClientProtocol(DatagramProtocol):
    """
    Client protocol implementation.

    The clients register with the rendezvous server.
    The rendezvous server returns connection details for the other peer.
    The client initializes a connection with the other peer and sends a
    message.
    """

    def startProtocol(self):
        """Register with the rendezvous server."""
        self.server_connect = False
        self.peer_init = False
        self.peer_connect = False
        self.peer_address = None
        self.transport.write(b'0', (sys.argv[1], int(sys.argv[2])))

    def toAddress(self, data):
        """Return an IPv4 address tuple."""
        ip, port = data.decode('utf-8').split(':')
        return (ip, int(port))

    def datagramReceived(self, datagram, host):
        """Handle incoming datagram messages."""
        if not self.server_connect:
            self.server_connect = True
            self.transport.write(b'ok', (sys.argv[1], int(sys.argv[2])))
            print('Connected to the server, waiting for peer...')

        elif not self.peer_init:
            self.peer_init = True
            self.peer_address = self.toAddress(datagram)
            self.transport.write(b'init', self.peer_address)
            print('Sent init to %s:%d' % self.peer_address)

        elif not self.peer_connect:
            self.peer_connect = True
            host = self.transport.getHost().host
            port = self.transport.getHost().port
            msg = 'Message from %s:%d' % (host, port)
            self.transport.write(msg.encode('utf-8'), self.peer_address)

        else:
            print('Received:', datagram.decode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./client RENDEZVOUS_IP RENDEZVOUS_PORT")
        sys.exit(1)

    protocol = ClientProtocol()
    t = reactor.listenUDP(0, protocol)
    reactor.run()
