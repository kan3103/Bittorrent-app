import requests


def send_started_request(tracker_url,info_hash, peer_id, port, downloaded=0, uploaded=0, left=0):

    params = {
        "info_hash": info_hash, 
        "peer_id": peer_id,      
        "port": port,            
        "uploaded": uploaded,    
        "downloaded": downloaded,  
        "left": left,            
        "event": "started"       
    }
    response = requests.get(tracker_url, params=params)
    return response.status_code, response.text


def send_stopped_request(tracker_url,info_hash, peer_id, port):

    params = {
        "info_hash": info_hash,
        "peer_id": peer_id,
        "port": port,
        "event": "stopped"  
    }
    response = requests.get(tracker_url, params=params)
    return response.status_code, response.text


def send_completed_request(tracker_url,info_hash, peer_id, port, downloaded, uploaded):

    params = {
        "info_hash": info_hash,
        "peer_id": peer_id,
        "port": port,
        "downloaded": downloaded,
        "uploaded": uploaded,
        "left": 0,           
        "event": "completed"  
    }
    response = requests.get(tracker_url, params=params)
    return response.status_code, response.text
