import socket
import threading
import json
import os


PEER_FILE = "file_peers.json"

file_peers = {}

def load_peers():
    
    global file_peers
    if os.path.exists(PEER_FILE):
        with open(PEER_FILE, "r") as f:
            file_peers = json.load(f)
            print(f"Tải danh sách peer từ {PEER_FILE}: {file_peers}")
    else:
        print("Không tìm thấy tệp peer, bắt đầu với danh sách rỗng.")

def save_peers():
   
    with open(PEER_FILE, "w") as f:
        json.dump(file_peers, f, indent=4)
        print(f"Lưu danh sách peer vào {PEER_FILE}.")

def remove_peer(file_id, peer_info):
    if file_id in file_peers:
        if peer_info in file_peers[file_id]:
            file_peers[file_id].remove(peer_info)
            if not file_peers[file_id]:  
                del file_peers[file_id]
            save_peers()  
            return True
    return False

def handle_client(conn, addr):
  
    try:
        data = conn.recv(1024)
        if not data:
            return
        request = json.loads(data.decode('utf-8'))  
        action = request.get('action', 'add')
        file_id = request['file_id']
        peer_info = request['peer_info']

       
        if action == 'add':
            
            if file_id not in file_peers:
                file_peers[file_id] = []
            if peer_info not in file_peers[file_id]:
                file_peers[file_id].append(peer_info)
            save_peers()

            
            response = json.dumps(file_peers[file_id]).encode('utf-8')
            conn.sendall(response)

        elif action == 'remove':
           
            removed = remove_peer(file_id, peer_info)
            response = {"success": removed}
            conn.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"Lỗi khi xử lý client {addr}: {e}")
    finally:
        conn.close()

def start_tracker(host='127.0.0.1', port=8000):
    
    load_peers()  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tracker_socket:
        tracker_socket.bind((host, port))
        tracker_socket.listen()
        print(f"Tracker đang lắng nghe tại {host}:{port}")

        while True:
            conn, addr = tracker_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_tracker()
