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

def run_bg_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    while True:
        line = process.stdout.readline().strip()
        if not line:
            break
        yield line

'''
# 如何处理流 io stream
b'  "Invensense ICM ACC": {'
b'    "values": ['
b'      0.0543060302734375,'
b'      0.43017578125,'
b'      9.862152099609375'
b'    ]'
b'  }'
b'}'
b'{'
b'  "Invensense ICM ACC": {'
b'    "values": ['
b'      0.0367584228515625,'
b'      0.3934783935546875,'
b'      9.853363037109375'
b'    ]'
b'  }'
b'}'

'''

def bg_task():
    # 发送传感器数据
    cmd = "termux-sensor -s Invensense ICM ACC" # 陀螺仪 -d 100 100ms
    # master/websocket_blockly2sensor_server.py
    output = run_bg_cmd(cmd)
    i = 0
    for output in output:
     # 一直在变化的怎么办 类似于top
        if b'values' in output:
            # 开始积累往下三行 缓冲
            # 设置计数器
            # next line
            i = 1
            continue
        if i == 1:
            x = float(output.split(b",")[0])
            print("x",x)
            # next line
            i = 2
            continue
        if  i == 2:
            y = float(output.split(b",")[0])
            print("y",y)
            # next line
            i = 3
            continue
        if  i == 3:
            z = float(output.split(b",")[0])
            print("z",z)
            i=0
            # 每次在这里发布
            socket_sonsor.send_json({"x":x,"y":y,"z":z})
            message = socket_sonsor.recv_json()
            print("sensor pipe recv:",message)
            continue

        # socket_sonsor.send_json({"hello":f"world{i}"})
        # message = socket_sonsor.recv_json()
        # print("sensor pipe recv:",message)
        # print(message)
        # i += 1

bg_thread = threading.Thread(target = bg_task)
bg_thread.daemon = True
bg_thread.start()

cmd_map = {
        "android/say":"termux-tts-speak {}",
        "android/vibrate":"termux-vibrate -d {}",
        "android/telephony_call":"termux-telephony-call  {}",
        "android/torch":"termux-torch  {}",
        # 两个参数
        "android/sms_send":"termux-sms-send -n {} {}",
        }

while True:
        message = socket.recv_json()  # python dict
        print(f"android server Received request: {message}")
        if message:
            topic, data = (message["topic"], message["payload"])
            if "android" not in topic:
                continue
            # todo 在此凑出cmd
            if topic == "android/sms_send":
                cmd = cmd_map[topic].format(data.get("number",10010),data.get("payload",'hello'))
            else:
                cmd = cmd_map[topic].format(data)
            output, rc, error = execute(cmd)
            print(output)
            socket.send_json(output)
