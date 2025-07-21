from flask import Flask, jsonify, request
from behavior import behavior
import threading
import os
import base64
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('num', metavar ='N', 
                    type = str,
                    help ='drone number')

args = parser.parse_args()


app = Flask(__name__)

name = args.num
port = int("51" + args.num)

print(name)





toggle = False

source_lock = threading.Lock()


info = {
    'target': {
        'target_id': "",
        'endpoint': "",
    },
    'id': name,
    'swarm_feed': {}
}

behavior_thread = threading.Thread(target=behavior, args=(info,))
behavior_thread.start()

@app.route("/action", methods=["POST"])
def change_action():
    data = request.get_json()
    target_id = data.get('target_id')
    endpoint = data.get('endpoint')

    target = {
        'target_id': target_id,
        'endpoint': endpoint
    }

    info['target'] = target
    return jsonify({"msg": "Action changed successfully"})



@app.route("/frame/<source_id>", methods=["POST"])
def receive_frame(source_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'frame' not in data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        frame_data = data['frame']
        metadata = data.get('metadata', {})
        
        # Validate base64 data
        # try:
        #     # Remove data URL prefix if present
        #     if frame_data.startswith('data:image'):
        #         frame_data = frame_data.split(',')[1]
            
        #     # Verify it's valid base64
        #     base64.b64decode(frame_data)
        # except Exception:
        #     return jsonify({'error': 'Invalid base64 frame data'}), 400
        
        # Update source information
        with source_lock:
            info['swarm_feed'][source_id] = {
                'latest_frame': frame_data,
                'last_update': datetime.now().isoformat(),
                'metadata': metadata,
                'frame_count': info['swarm_feed'].get(source_id, {}).get('frame_count', 0) + 1
            }
        
        return jsonify({
            'status': 'success',
            'source_id': source_id,
            'frame_count': info['swarm_feed'][source_id]['frame_count'],
            'timestamp': info['swarm_feed'][source_id]['last_update']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify(info)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=port, threaded=True)