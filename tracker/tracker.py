# pip install flask để tải 

from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

PEER_FILE = "file_peers.json"
file_peers = {}  # Dạng: {"info_hash1": [{"peer_id": "peer123", "port": 8080}, ...]}

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

def remove_peer(info_hash, peer_id, port):
    if info_hash in file_peers:
        peer_list = file_peers[info_hash]
        for peer in peer_list:
            if peer["peer_id"] == peer_id and peer["port"] == port:
                peer_list.remove(peer)
                if not peer_list:  
                    del file_peers[info_hash]
                save_peers()
                return True
    return False

@app.route("/peer", methods=["GET"])
def handle_event():
    info_hash = request.args.get("info_hash")
    peer_id = request.args.get("peer_id")
    port = request.args.get("port")
    event = request.args.get("event")
    
    if not event or not info_hash:
        return jsonify({"error": "event và info_hash là bắt buộc"}), 400

    if port:
        try:
            port = int(port)
        except ValueError:
            return jsonify({"error": "port phải là số nguyên"}), 400

    if event == "started":
        if not peer_id or not port:
            return jsonify({"error": "peer_id và port là bắt buộc cho sự kiện add"}), 400
        if info_hash not in file_peers:
            file_peers[info_hash] = []
        
        if not any(peer["peer_id"] == peer_id and peer["port"] == port for peer in file_peers[info_hash]):
            file_peers[info_hash].append({"peer_id": peer_id, "port": port})
            save_peers()
        return jsonify({"success": True, "peers": file_peers[info_hash]})

    elif event == "stopped":
        if not peer_id or not port:
            return jsonify({"error": "peer_id và port là bắt buộc cho sự kiện remove"}), 400
        removed = remove_peer(info_hash, peer_id, port)
        return jsonify({"success": removed})

    elif event == "status":
        return jsonify(file_peers)

    elif event == "completed":
        
        return jsonify({"success": True, "message": "Download completed"})

    elif event is None:
        
        return jsonify(file_peers)
    else:
        return jsonify({"error": "event không hợp lệ"}), 400

if __name__ == "__main__":
    load_peers()
    app.run(host="127.0.0.1", port=8000)
