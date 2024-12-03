#API for communicating with UI
from torrent import Torrent
from constants import PEER_ID, PEER_IP, PEER_PORT
import os
import shutil
import requests
from client import Downloader
from strategy import TitOrTat
from server import Server
from threading import Thread
import time

class Client:
    def __init__(self):
        self.torrents = {}
        self.downloaders = {}
        self.download_threads = []
        self.strategy = TitOrTat()
        self.server = Server(self.torrents, PEER_PORT, self.strategy)
        self.server_thread = None

    def make_dir(self, dir, file_paths):
        os.makedirs(dir, exist_ok=True)

        for file_path in file_paths:
            shutil.copy(file_path, dir)
        return dir

    def create_torrent(self, dir):
        torrent = Torrent.create_torrent_file(dir)
        self.torrents[torrent.info_hash] = torrent
        return torrent
    
    def add_torrent(self, torrent_file):
        torrent = Torrent(torrent_file)
        self.torrents[torrent.info_hash] = torrent
        return torrent
    
        
    def download(self, info_hash):
        torrent = self.torrents[info_hash]
        peers = requests.get(torrent.announce, params={'info_hash':torrent.info_hash, 'peer_id':self.server.peer_id, 'port':self.server.port, 'event':'started'}).json()
        # peers = [
        #     {'peer_id' :'DlcCX7j*$6!A,]%WF?qu', 'ip':'127.0.0.1', 'port':8000},
        # ]
        # print(peers)

        self.downloaders[info_hash] =  Downloader(torrent, peers, TitOrTat())
        print("Starting download")
        self.download_threads.append(Thread(target=self.downloaders[info_hash].start).start())

    def get_downloading_torrents(self):
        return [val.torrent for val in self.downloaders.values()]
    
    def run_server(self):
        self.server_thread = Thread(target=self.server.start).start()

    def stop(self, info_hash):
        self.downloaders[info_hash].pause()

    def resume(self, info_hash):
        self.downloaders[info_hash].resume()
    
    def remove(self, info_hash):
        self.downloaders[info_hash].stop()
        del self.downloaders[info_hash]



if __name__ == '__main__':
    client = Client()
    info_hash = client.create_torrent('downloads')
    client.run_server()
    time.sleep(1)
    client.download(client.add_torrent('downloads.torrent').info_hash)
    client.get_downloading_torrents()
    time.sleep(0.5)
    