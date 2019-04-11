from microbit import *  # sleep, uart, button_a, display
import random

# todo 使用exec 直接运行代码，realtalk风格

uart.init(115200)

display.scroll("codelab", wait=False, loop=False)

TOPIC = "eim/usbMicrobit"

'''
写成server风格: 响应式
  硬件内部: read-write
  client:  write-read

why:
  *  通信方式更简单（不需要协程！），易于拓展为蓝牙、wifi(socket)之类
  *  sensor_pub和actuator_sub一致
    *  发送传感器数据是对请求数据的回应 write 具体传感器数据值
    *  接收执行指令也是对请求数据的回应 write done
  *  由proxy控制rate
  *  理想情况下这种通信也用zmq，但出于现实原因，我们得使用蓝牙，wifi之类的，而且未必有zmq库

build:
    在python.microbit.org编译为hex，需要删除中文。
'''


def get_sensors():
    '''
    here: sensor pub message
    '''
    # while True:
    a = button_a.is_pressed()
    b = button_b.is_pressed()
    x = accelerometer.get_x()
    y = accelerometer.get_y()
    z = accelerometer.get_z()

    dic = {
        # "id": "microbit",
        "topic": TOPIC,
        "payload": {
            "button_a": a,
            "button_b": b,
            "x": x,
            "y": y,
            "z": z
        }
    }
    return dic

def get_topic_and_data(b):
    # 两种请求都使用一样的结构,只是topic不同
    try:
        b = b.strip()
        json_str = str(b, 'utf-8')
        json = eval(json_str)
        # :todo check key data, topic
        if not json.get('topic'):
            return
        topic = str(json.get('topic'))
        data = str(json.get("payload"))
        return topic, data
    except Exception as e:
        # 舍弃无效的数据
        display.show(str("!"))
        return


def on_callback_req(topic, python_code):
    '''
    对请求的响应
    '''
    try:
        exec(python_code)
        err = ""
    except Exception as e:
        err = str(e)

    result = get_sensors()
    result["err"] = err 
    # result["result"] = "test" # 额外塞入运行结果
    uart.write(bytes(str(result)+"\n", 'utf-8')) # 不断返回, 只此一处write


r_merge = b''

while True:
    r = uart.readline()  # readline不保证返回完整的一行，自行拼接，使用一个具体的例子思考 b'{"a": 1}'
    if r:
        r_merge += r
        if r_merge.startswith(b'{') and r_merge.endswith(b'\r\n'):
            # 如果拼出了完整的内容
            d = get_topic_and_data(r_merge)
            if d:
                # 如果数据有效
                topic, python_code = d
                on_callback_req(topic, python_code)
            r_merge = b''
