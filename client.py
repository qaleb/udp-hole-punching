##############################################################################
#################  TURN (Traversal Using Relays around NAT)  #################
##############################################################################
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import sys
import uuid  # For generating unique peer IDs
import logging

class ClientProtocol(DatagramProtocol):
    def __init__(self):
        self.peer_id = str(uuid.uuid4())  # Generate a unique peer ID
        self.server_address = (sys.argv[1], int(sys.argv[2]))

    def startProtocol(self):
        # Register with the relay server
        self.transport.write(f'{self.peer_id}:{self.server_address[1]}'.encode('utf-8'), self.server_address)

    def datagramReceived(self, datagram, _):
        try:
            message = datagram.decode('utf-8')
            logging.info(f'Message received: {message}')

        except Exception as e:
            logging.error(f"Error processing datagram: {e}")

    def sendMessage(self, target_peer_id, message_text):
        # Send a message to a target peer through the relay server
        message = f'{target_peer_id}:{self.peer_id}:{message_text}'
        self.transport.write(message.encode('utf-8'), self.server_address)
        logging.info(f'Message sent to Peer {target_peer_id}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./client.py RELAY_SERVER_IP RELAY_SERVER_PORT")
        sys.exit(1)

    relay_server_ip = sys.argv[1]
    relay_server_port = int(sys.argv[2])

    protocol = ClientProtocol()
    reactor.listenUDP(0, protocol)
    reactor.callLater(1, protocol.sendMessage, 'TargetPeerID', 'Hello, this is a message')

    # Run the client
    reactor.run()






##############################################################################
################  STUN (Session Traversal Utilities for NAT)  ################
##############################################################################
# from twisted.internet.protocol import DatagramProtocol
# from twisted.internet import reactor, threads

# import sys
# import threading

# class ClientProtocol(DatagramProtocol):
#     def __init__(self):
#         self.server_connect = False
#         self.peer_init = False
#         self.peer_connect = False
#         self.peer_address = None
#         self.print_lock = threading.Lock()

#     def startProtocol(self):
#         with self.print_lock:
#             print('Connected to the server, waiting for peer...')
#         self.transport.write(b'0', (sys.argv[1], int(sys.argv[2])))

#     def toAddress(self, data):
#         ip, port = data.decode('utf-8').split(':')
#         return ip, int(port)

#     def datagramReceived(self, datagram, host):
#         if not self.server_connect:
#             self.server_connect = True
#             with self.print_lock:
#                 print('Connected to the server, waiting for peer...')
#         elif not self.peer_init:
#             self.peer_init = True
#             self.peer_address = self.toAddress(datagram)
#             self.transport.write(b'init', self.peer_address)
#             with self.print_lock:
#                 print(f'Sent init to {self.peer_address[0]}:{self.peer_address[1]}')
#         elif not self.peer_connect:
#             self.peer_connect = True
#             host = self.transport.getHost().host
#             port = self.transport.getHost().port
#             msg = f'Message from {host}:{port}'
#             self.transport.write(msg.encode('utf-8'), self.peer_address)
#             with self.print_lock:
#                 print(f'Received: {msg}')
#                 print("Enter a message (type 'exit' to quit):")
#         else:
#             self.handleMessage(datagram)

#     def handleMessage(self, datagram):
#         with self.print_lock:
#             print('Received:', datagram.decode('utf-8'))

#     def sendMessage(self, message):
#         if self.peer_connect and self.transport:
#             self.transport.write(message.encode('utf-8'), self.peer_address)
#         else:
#             with self.print_lock:
#                 print('Peer not connected yet or the transport is not available. Cannot send message.')


# if __name__ == '__main__':
#     if len(sys.argv) < 3:
#         print("Usage: ./client RENDEZVOUS_IP RENDEZVOUS_PORT")
#         sys.exit(1)

#     protocol = ClientProtocol()
#     t = reactor.listenUDP(0, protocol)

#     def message_sending_loop():
#         while True:
#             message = input()
#             if message.lower() == 'exit':
#                 break
#             protocol.sendMessage(message)

#     reactor.callInThread(message_sending_loop)
#     reactor.run()
