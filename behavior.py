import time
import requests

def behavior(info):
    id = info['id']
    while True:
        target = info['target']

        if not target['target_id']:
            print("Processing my own feed.")
        else:
            target_id = target['target_id']
            if id == target_id:
                print(info['swarm_feed'])
            else:
                print(f"Sending feed over to {target_id}.")
                endpoint = target['endpoint']
                data = {'frame': 'Other frame', 'metadata': {"what":"testing"}}
                response = requests.post(f"{endpoint}/{id}", json=data)
        
        time.sleep(5)