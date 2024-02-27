##############################################################################
#################  TURN (Traversal Using Relays around NAT)  #################
##############################################################################

# Import necessary modules
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, threads
import sys
import threading

# Define the client protocol for handling communication
class ClientProtocol(DatagramProtocol):
    def __init__(self):
        # Initialization of protocol states and necessary variables
        self.server_connect = False  # Flag indicating connection to the server
        self.peer_init = False  # Flag indicating initiation of peer connection
        self.peer_connect = False  # Flag indicating connection to the peer
        self.peer_address = None  # Peer's address
        self.relay_address = None  # Relay's address
        self.print_lock = threading.Lock()  # Lock for thread-safe printing

    def startProtocol(self):
        # Method called when the protocol is started
        with self.print_lock:
            print('Connecting to the server...')
        # Send initial message to server upon connection
        self.transport.write(b'0', (sys.argv[1], int(sys.argv[2])))

    def toAddress(self, data):
        # Helper method to convert received data to an IP address and port
        ip, port = data.decode('utf-8').split(':')
        return ip, int(port)

    def datagramReceived(self, datagram, host):
        # Method called when a datagram is received
        if not self.server_connect:
            # Handle server connection
            self.server_connect = True
            with self.print_lock:
                print('Connected to the server, waiting for peer...')
        elif not self.peer_init:
            # Handle peer initiation
            self.peer_init = True
            self.peer_address = self.toAddress(datagram)
            self.relay_address = host
            # Send initiation message to peer
            self.transport.write(b'init', self.peer_address)
            with self.print_lock:
                print(f'Sent init to {self.peer_address[0]}:{self.peer_address[1]}')
        elif not self.peer_connect:
            # Handle peer connection
            self.peer_connect = True
            host = self.transport.getHost().host
            port = self.transport.getHost().port
            msg = f'Message from {host}:{port}'
            # Send message to peer
            self.transport.write(msg.encode('utf-8'), self.peer_address)
            with self.print_lock:
                print(f'Relaying through {self.relay_address[0]}:{self.relay_address[1]}')
                # print(f'Received: {msg}')
                print("Enter a message (type 'exit' to quit):")
        else:
            # Handle incoming messages from the peer
            self.handleMessage(datagram)

    def handleMessage(self, datagram):
        # Method to handle incoming messages from the peer
        with self.print_lock:
            print('Received:', datagram.decode('utf-8'))
            if datagram.lower() == b'peer has exited the conversation. conversation closed.':
                # Stop the reactor and exit the program when the peer exits
                reactor.stop()

    def sendMessage(self, message):
        # Method to send messages to the peer
        if self.peer_connect and self.transport:
            self.transport.write(message.encode('utf-8'), self.relay_address)
        else:
            with self.print_lock:
                print('Peer not connected yet or the transport is not available. Cannot send message.')

# Entry point of the program
if __name__ == '__main__':
    # Check if the required command-line arguments are provided
    if len(sys.argv) < 3:
        print("Usage: ./client RENDEZVOUS_IP RENDEZVOUS_PORT")
        sys.exit(1)

    # Instantiate the client protocol
    protocol = ClientProtocol()
    # Listen on a random UDP port with the protocol
    t = reactor.listenUDP(0, protocol)

    # Define a thread for handling user input and sending messages
    def message_sending_loop():
        while True:
            message = input()
            protocol.sendMessage(message)
            if message.lower() == 'exit':
                reactor.callFromThread(reactor.stop)  # Stop the reactor and exit the program
                # reactor.stop()  # Alternative: Stop the reactor directly
                break

    # Start the message sending thread
    reactor.callInThread(message_sending_loop)
    # Start the reactor to run the program
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
