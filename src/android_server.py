import zmq
import subprocess
# from zmq.asyncio import Context
from zmq import Context

port = 38777
context = Context.instance()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

def execute(cmd, encoding='UTF-8', timeout=None, shell=True):
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    output, error = proc.communicate(timeout=timeout)
    # rstrip('\n') may be more accurate, actually nothing may be better
    output = output.decode(encoding).rstrip()
    error = error.decode(encoding).rstrip()
    rc = proc.returncode
    return (output, rc, error)

while True:
        message = socket.recv_json()  # python dict
        print(f"android server Received request: {message}")
        if message:
            topic, data = (message["topic"], message["data"])
            output, rc, error = execute(data)
            print(output)
            socket.send_json(output)