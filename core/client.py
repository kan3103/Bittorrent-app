from threading import Thread, Lock
from constants import PROTOCOL_NAME, PEER_ID, PIECE_SIZE, BLOCK_SIZE
from messages import HandshakeMessage, InterestedMessage, RequestMessage, BitfieldMessage, Message, UnchokeMessage
import socket
import hashlib
import os
import time

def recv_all(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:  # Connection closed
            raise ConnectionError("Socket connection closed before all data was received")
        data += packet
    return data


class Downloader:
    def __init__(self, torrent, peers, strategy):
        self.torrent = torrent
        self.pieces = {index: [] for index in range(len(self.torrent.pieces))}
        self.peers = peers  # TODO: get peers from tracker
        self.downloaded_pieces = [] # list of pieces index that have been downloaded
        self.strategy = strategy
        self.sources = {} # key: conn, value: list of pieces index
        self.piece_lock = [Lock() for _ in range(len(self.torrent.pieces))]
        self.running = True
        self.cancled = False

    def start(self):
        conn_threads = []
        for peer in self.peers:
            thread = Thread(target=self.connect_to_peer, args=(peer['peer_id'], peer['ip'], peer['port']))
            thread.start()
            conn_threads.append(thread)
        for t in conn_threads:
            t.join()
        
        # pieces = {k : v for k, v in sorted(self.pieces.items(), key=lambda item: len(item[1]))}
        self.pieces = sorted(self.pieces.items(), key=lambda item: len(item[1]))
        # key: conn, value: list of pieces index
        for piece_index, conns in self.pieces:   #piece = [conn1, conn2, ...]
            if len(conns) > 0:
                for conn in conns:
                    conn.sendall(InterestedMessage().encode())
                    msg_rcv = conn.recv(5)
                    msg = Message.decode(msg_rcv[4:])
                    if isinstance(msg, UnchokeMessage):
                        self.sources[conn].append(piece_index)
                
        downloading_threads = []
        os.makedirs(os.path.dirname('test/haha'), exist_ok=True)

        for peer, pieces in self.sources.items():
            thread = Thread(target=self.download_pieces, args=(peer, pieces))
            thread.start()
            downloading_threads.append(thread)
        
        for t in downloading_threads:
            t.join()
        if len(self.downloaded_pieces) == len(self.torrent.pieces):
            print("Download completed, you downloaded the whole file")
        else:
            print("Download failed. Some pieces are missing")

        print(self.torrent.files_info)
    
    def connect_to_peer(self,peer_id, ip, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connecting to {ip}:{port}")
        client.connect((ip, port))
        self.strategy.init_downloaded_from(ip)
        handshake_rcv, bitfield_rcv = self.send_handshake(client)
        # if handshake_rcv.info_hash != self.torrent.info_hash or handshake_rcv.peer_id != peer_id:
        #     print("Handshake failed")
        #     client.close()
        #     return
        self.sources[client] = []
        for index, byte in enumerate(bitfield_rcv.bitfield):
            if byte == 1:
                self.pieces[index].append(client)

    def send_handshake(self, conn):
        conn.sendall(HandshakeMessage(PROTOCOL_NAME, self.torrent.info_hash, PEER_ID).encode())
        status = conn.recv(1)
        if status == 0xFF:
            print("Handshake failed")
            conn.close()
            return
        handshake_rcv = conn.recv(49 + len(PROTOCOL_NAME))
        bitfield_rcv = conn.recv(5 + len(self.pieces))
        handshake_msg = Message.decode(handshake_rcv)
        bitfield_msg = Message.decode(bitfield_rcv[4:])
        return handshake_msg, bitfield_msg
    
    def request_piece(self, conn, piece_index):
        with self.piece_lock[piece_index]:
            piece = b''
            begin = 0
            print(f"request for piece {piece_index} from {conn.getpeername()}")
            while begin < PIECE_SIZE:
                conn.sendall(RequestMessage(piece_index, begin, BLOCK_SIZE).encode())
                length = int.from_bytes(conn.recv(4), 'big')
                # msg_rcv = conn.recv(length)
                msg_rcv = recv_all(conn, length) # make sure we receive all data, instead of recv
                if msg_rcv == b'':
                    break
                piece += Message.decode(msg_rcv).block
                begin += BLOCK_SIZE
                
            print(f"received piece {piece_index}, size {len(piece)}")
            piece_hash = hashlib.sha1(piece).digest()
            if self.torrent.pieces[piece_index] == piece_hash:
                print(f"Piece {piece_index} is correct")
                self.write_to_file(piece_index, piece)
                return True
            else:
                return False

    def download_pieces(self, conn, pieces):
        for piece_index in pieces:
            while not self.running:
                if self.cancled:
                    return
            if self.request_piece(conn, piece_index):
                self.downloaded_pieces.append(piece_index)
                ip, port = conn.getpeername()
                self.strategy.inc_peer_downloaded(ip)

    def pause(self):
        self.running = False
    
    def resume(self):
        self.running = True

    def stop(self):
        self.running = False
        self.cancled = True
        for conn in self.sources.keys():
            conn.close()
        self.sources = {}
        self.pieces = {index: [] for index in range(len(self.torrent.pieces))}
        self.downloaded_pieces = []
    
    
    def write_to_file(self, piece_index, piece):
        dir_name = 'test/'
        # dir_name = ''  # If you want to change the directory

        # Calculate the position of the current piece in the file sequence
        file_position = piece_index * PIECE_SIZE

        file_index = 0
        # Find the correct file based on file size
        while file_position >= self.torrent.files_info[file_index]['length']:
            file_position -= self.torrent.files_info[file_index]['length']
            file_index += 1

        data_written = 0
        start = 0
        while file_index < len(self.torrent.files_info):
            # Open the appropriate file in append binary mode
            file_path = dir_name + self.torrent.files_info[file_index]['path']
            
            with open(file_path, 'ab') as f:
                # Seek to the correct position in the file
                f.seek(file_position)
                
                # Calculate how much data we can write in this file (taking into account remaining space)
                remaining_file_space = self.torrent.files_info[file_index]['length'] - file_position
                write_size = min(len(piece) - data_written, remaining_file_space)
                
                # Write the data to the file
                written = f.write(piece[start:start + write_size])
                data_written += written
                
                # Update the downloaded bytes for the file
                self.torrent.files_info[file_index]['downloaded'] += written
                
                # Update the start position for the next chunk
                start += written

            # If all the data has been written, break out of the loop
            if data_written == len(piece):
                break
            
            # Otherwise, move to the next file
            file_index += 1
            file_position = 0  # Reset file position for the new file
