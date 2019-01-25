'''
cozmo server : zmq rep

usage:
    python cozmo_server.py

ref:
    https://github.com/anki/cozmo-python-sdk/blob/master/examples/apps/remote_control_cozmo.py#L335
'''
import time
# time.sleep(7) # 树莓派开机等待
import zmq
from zmq import Context

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

port = 38777
context = Context.instance()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

quit_code = "quit!"

def cozmo_program(robot: cozmo.robot.Robot):
    # import IPython;IPython.embed()
    while True:
        python_code = socket.recv_json().get("python_code")
        print("cozmo server", python_code)
        if not python_code:
            continue

        if python_code == "quit!":
            socket.send_json({"result": "quit!"})
            break
        else:
            try:
                # 单一入口，传递源码
                # 为了安全性, 做一些能力的牺牲, 放弃使用exec
                output = eval(
                    python_code,
                    {"__builtins__": None},
                    {
                        # "anki_vector": anki_vector,
                        "robot": robot,
                        "cozmo": cozmo
                    })
                # exec(python_code) # 安全性问题
            except Exception as e:
                output = e
        socket.send_json({"result": str(output)})


if __name__ == '__main__':
    # while True: 用于树莓派
    cozmo.run_program(cozmo_program)
