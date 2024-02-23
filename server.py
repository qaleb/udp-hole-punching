##############################################################################
#################  TURN (Traversal Using Relays around NAT)  #################
##############################################################################
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import sys
import logging

class RelayServerProtocol(DatagramProtocol):
    def __init__(self):
        self.peers = {}  # Dictionary to store the mapping of peer_id to address

    def datagramReceived(self, datagram, address):
        try:
            message = datagram.decode('utf-8')
            parts = message.split(':')

            if len(parts) == 2:
                # Registering a new peer
                peer_id, peer_address = parts[0], (address[0], int(parts[1]))
                logging.info(f'Registration from Peer {peer_id}: {peer_address}')
                self.peers[peer_id] = peer_address
                self.transport.write(b'ok', address)

            elif len(parts) == 3:
                # Sending a message to a peer
                target_peer_id, source_peer_id, message_text = parts
                target_peer_address = self.peers.get(target_peer_id)

                if target_peer_address:
                    self.transport.write(message_text.encode('utf-8'), target_peer_address)
                    logging.info(f'Message relayed from Peer {source_peer_id} to Peer {target_peer_id}')

                else:
                    logging.warning(f"Target Peer {target_peer_id} not found")

        except Exception as e:
            logging.error(f"Error processing datagram: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./server.py PORT")
        sys.exit(1)

    port = int(sys.argv[1])

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run the server
    reactor.listenUDP(port, RelayServerProtocol())
    logging.info(f'Relay Server Listening on *:{port}')
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
