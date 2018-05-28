import subprocess, threading, time
# from zmq.asyncio import Context
import zmq
from zmq import Context

port = 38778
context = Context.instance()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

port_sensor = 38779
context_sonsor = Context.instance()
socket_sonsor = context_sonsor.socket(zmq.REQ)
socket_sonsor.bind("tcp://*:%s" % port_sensor)


def execute(cmd, encoding='UTF-8', timeout=None, shell=True):
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    output, error = proc.communicate(timeout=timeout)
    # rstrip('\n') may be more accurate, actually nothing may be better
    output = output.decode(encoding).rstrip()
    error = error.decode(encoding).rstrip()
    rc = proc.returncode
    return (output, rc, error)

def bg_task():
    i = 0
    while True:
        socket_sonsor.send_json({"hello":f"world{i}"})
        time.sleep(1)
        message = socket_sonsor.recv_json()
        print("sensor pipe recv:",message)
        print(message)
        i += 1

bg_thread = threading.Thread(target = bg_task)
bg_thread.daemon = True
bg_thread.start()

while True:
        message = socket.recv_json()  # python dict
        print(f"android server Received request: {message}")
        if message:
            topic, data = (message["topic"], message["data"])
            output, rc, error = execute(data)
            print(output)
            socket.send_json(output)
