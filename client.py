##############################################################################
############  TURN (Traversal Using Relays around NAT) VERSION 1  ############
##############################################################################
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, threads

import sys
import threading


class ClientProtocol(DatagramProtocol):
    def __init__(self):
        # State variable to manage the flow of events
        self.state = 'initial'
        self.peer_address = None
        self.relay_address = None
        self.print_lock = threading.Lock()

    def startProtocol(self):
        with self.print_lock:
            print('Connecting to the server...')
        # Send registration message to the server
        self.transport.write(b'0', (sys.argv[1], int(sys.argv[2])))

    def toAddress(self, data):
        # Helper function to convert address information from data
        ip, port = data.decode('utf-8').split(':')
        return ip, int(port)

    def handleInitial(self, host):
        # Handle the initial connection state
        self.state = 'waiting_for_peer'
        with self.print_lock:
            print('Connected to the server, waiting for peer...')

    def handleWaitingForPeer(self, datagram, host):
        # Handle the waiting for peer state
        self.state = 'connecting_to_peer'
        self.peer_address = self.toAddress(datagram)
        self.relay_address = host
        # Send initialization message to the peer
        self.transport.write(b'init', self.peer_address)
        with self.print_lock:
            print(f'Sent init to {self.peer_address[0]}:{self.peer_address[1]}')

    def handleConnectingToPeer(self):
        # Handle the connecting to peer state
        self.state = 'connected'
        host = self.transport.getHost().host
        port = self.transport.getHost().port
        msg = f'Message from {host}:{port}'
        # Relay message to the peer through the server
        self.transport.write(msg.encode('utf-8'), self.peer_address)
        with self.print_lock:
            print(f'Relaying through {self.relay_address[0]}:{self.relay_address[1]}')
            print("Enter a message (type 'exit' to quit):")

    def datagramReceived(self, datagram, host):
        # Handle incoming datagrams based on the current state
        if self.state == 'initial':
            self.handleInitial(host)
        elif self.state == 'waiting_for_peer':
            self.handleWaitingForPeer(datagram, host)
        elif self.state == 'connecting_to_peer':
            self.handleConnectingToPeer()
        elif self.state == 'connected':
            self.handleMessage(datagram)

    def handleMessage(self, datagram):
        # Handle incoming messages from the peer
        with self.print_lock:
            print('Received:', datagram.decode('utf-8'))
            if datagram.lower() == b'peer has exited the conversation. conversation closed.':
                # Stop the reactor if the peer has exited
                reactor.stop()

    def sendMessage(self, message):
        # Send a message to the peer if connected
        if self.state == 'connected' and self.transport:
            self.transport.write(message.encode('utf-8'), self.relay_address)
        else:
            with self.print_lock:
                print('Peer not connected yet or the transport is not available. Cannot send message.')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./client RENDEZVOUS_IP RENDEZVOUS_PORT")
        sys.exit(1)

    # Instantiate the ClientProtocol and listen for UDP connections
    protocol = ClientProtocol()
    reactor.listenUDP(0, protocol)

    def message_sending_loop():
        # Continuously prompt the user for input and send messages
        while True:
            message = input()
            protocol.sendMessage(message)
            if message.lower() == 'exit':
                # Stop the reactor if 'exit' is entered
                reactor.callFromThread(reactor.stop)
                break

    # Run the message sending loop in a separate thread
    reactor.callInThread(message_sending_loop)
    # Start the reactor to handle network events
    reactor.run()




##############################################################################
############  TURN (Traversal Using Relays around NAT) VERSION 1  ############
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
#         self.relay_address = None
#         self.print_lock = threading.Lock()

#     def startProtocol(self):
#         with self.print_lock:
#             print('Connecting to the server...')
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
#             self.relay_address = host
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
#                 print(f'Relaying through {self.relay_address[0]}:{self.relay_address[1]}')
#                 # print(f'Received: {msg}')
#                 print("Enter a message (type 'exit' to quit):")
#         else:
#             self.handleMessage(datagram)

#     def handleMessage(self, datagram):
#         with self.print_lock:
#             print('Received:', datagram.decode('utf-8'))
#             if datagram.lower() == b'peer has exited the conversation. conversation closed.':
#                 reactor.stop()

#     def sendMessage(self, message):
#         if self.peer_connect and self.transport:
#             self.transport.write(message.encode('utf-8'), self.relay_address)
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
#             protocol.sendMessage(message)
#             if message.lower() == 'exit':
#                 reactor.callFromThread(reactor.stop)  
#                 # reactor.stop()  # Stop the reactor and exit the program
#                 break

#     reactor.callInThread(message_sending_loop)
#     reactor.run()




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
