import numpy as np
import zmq

def analyze_frames(port, topic, event):
    context = zmq.Context()
    with context.socket(zmq.SUB) as socket:
        socket.connect(f"tcp://localhost:{port}")
        topic_filter = topic.encode('utf-8')
        socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
        socket.setsockopt(zmq.SUBSCRIBE, ''.encode('utf-8'))
        i = 0
        while True:
            topic = socket.recv_string()
            data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
            if isinstance(data, str):
                break


            i+=1
