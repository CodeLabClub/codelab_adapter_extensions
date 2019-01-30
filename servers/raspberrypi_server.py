'''
pip3 install gpiozero pigpio pyzmq --user
# docs: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html
'''
import zmq
import os  # env
# GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR= "raspberrypi.local"# 192.168.1.3
os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
os.environ["PIGPIO_ADDR"] = "raspberrypi.local"
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# zmq socket
port = 38782
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

quit_code = "quit!"

def main():
    factory = PiGPIOFactory(host='raspberrypi.local') # 192.168.1.3
    led = LED(17, pin_factory=factory)

    while True:
        python_code = socket.recv_json().get("python_code")
        if not python_code:
            continue

        if python_code == "quit!":
            socket.send_json({"result": "quit!"})
            break
        else:
            try:
                # 单一入口，传递源码
                # 为了安全性, 做一些能力的牺牲, 放弃使用exec
                output = eval(python_code, {"__builtins__": None}, {
                    "led": led,
                    "factory": factory
                })
                # exec(python_code) # 安全性问题
            except Exception as e:
                output = e
        socket.send_json({"result": str(output)})

    socket.close()
    context.term()

if __name__ == '__main__':
    main()
