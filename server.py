##############################################################################
#################  TURN (Traversal Using Relays around NAT)  #################
##############################################################################
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import sys

class ServerProtocol(DatagramProtocol):
    def __init__(self):
        self.addresses = {}

    def addressString(self, address):
        ip, port = address
        if isinstance(ip, bytes):
            ip = ip.decode('utf-8')
        return f'{ip}:{port}'

    def notifyPeerExit(self, address):
        if address in self.addresses and self.addresses[address] is not None:
            peer_address = self.addresses[address]
            exit_message = b'Peer has exited the conversation. Conversation closed.'
            self.transport.write(exit_message, peer_address)
            print(f'Notified {peer_address[0]}:{peer_address[1]} about peer exit.')
            # Optionally, remove entries related to the exiting peer
            del self.addresses[address]
            del self.addresses[peer_address]

    def datagramReceived(self, datagram, address):
        if datagram == b'0':
            print(f'Registration from {address[0]}:{address[1]}')
            self.transport.write(b'ok', address)
            self.addresses[address] = None

            if len(self.addresses) >= 2:
                peer1, peer2 = list(self.addresses.keys())[:2]
                msg_0 = self.addressString(peer2)
                msg_1 = self.addressString(peer1)

                self.transport.write(msg_0.encode('utf-8'), peer1)
                self.transport.write(msg_1.encode('utf-8'), peer2)

                self.addresses[peer1] = peer2
                self.addresses[peer2] = peer1

                print('Linked peers')

        elif address in self.addresses and self.addresses[address] is not None:
            peer_address = self.addresses[address]
            self.transport.write(datagram, peer_address)
            print(f'Relayed message from {address[0]}:{address[1]} to {peer_address[0]}:{peer_address[1]}')

            # Check if the received message indicates peer exit
            if datagram.lower() == b'exit':
                self.notifyPeerExit(address)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./server.py PORT")
        sys.exit(1)

    port = int(sys.argv[1])
    reactor.listenUDP(port, ServerProtocol())
    print(f'Listening on *:{port}')
    reactor.run()




##############################################################################
################  STUN (Session Traversal Utilities for NAT)  ################
##############################################################################
#!/usr/bin/env python3
# """UDP hole punching server."""
# from twisted.internet.protocol import DatagramProtocol
# from twisted.internet import reactor

# import sys


# class ServerProtocol(DatagramProtocol):
#     """
#     Server protocol implementation.

#     Server listens for UDP messages. Once it receives a message it registers
#     this client for a peer link in the waiting list.

#     As soon as a second client connects, information about one client (public
#     IP address and port) is sent to the other and vice versa.

#     Those clients are now considered linked and removed from the waiting list.
#     """

#     def __init__(self):
#         """Initialize with empty address list."""
#         self.addresses = []

#     def addressString(self, address):
#         """Return a string representation of an address."""
#         ip, port = address
#         if isinstance(ip, bytes):
#             ip = ip.decode('utf-8')
#         return f'{ip}:{port}'

#     def datagramReceived(self, datagram, address):
#         """Handle incoming datagram messages."""
#         if datagram == b'0':
#             print(f'Registration from {address[0]}:{address[1]}')
#             self.transport.write(b'ok', address)
#             self.addresses.append(address)

#             if len(self.addresses) >= 2:
#                 msg_0 = self.addressString(self.addresses[1])
#                 msg_1 = self.addressString(self.addresses[0])

#                 self.transport.write(msg_0.encode('utf-8'), self.addresses[0])
#                 self.transport.write(msg_1.encode('utf-8'), self.addresses[1])

#                 self.addresses.pop(0)
#                 self.addresses.pop(0)

#                 print('Linked peers')


# if __name__ == '__main__':
#     if len(sys.argv) < 2:
#         print("Usage: ./server.py PORT")
#         sys.exit(1)

#     port = int(sys.argv[1])
#     reactor.listenUDP(port, ServerProtocol())
#     print(f'Listening on *:{port}')
#     reactor.run()
