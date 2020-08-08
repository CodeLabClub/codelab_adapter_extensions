from microbit import *  

class Servo:
    def __init__(self, pin):
        self.pin = pin
        self.pin.set_analog_period(20)
        self.status = 0
        self.angle(0)

    def angle(self, d=None):
        if d is None:
            return self.status
        else:
            self.pin.write_analog(int(1023 * (0.5 + d/90) / 20))
            self.status = d

uart.init(115200)
display.scroll("welcome!", wait=False, loop=False)
TOPIC = "eim/usbMicrobit"

servo = Servo(pin2)
def get_sensors():
    a = button_a.is_pressed()
    b = button_b.is_pressed()
    x = accelerometer.get_x()
    y = accelerometer.get_y()
    z = accelerometer.get_z()
    pin_one_analog_input = pin1.read_analog()
    pin_two_analog_input = pin2.read_analog()
    gesture = accelerometer.current_gesture()

    dic = {
        "topic": TOPIC,
        "payload": {
            "button_a": a,
            "button_b": b,
            "x": x,
            "y": y,
            "z": z,
            "pin_one_analog_input": pin_one_analog_input,
            "pin_two_analog_input": pin_two_analog_input,
            "gesture": gesture
        }
    }
    return dic

def get_topic_and_data(b):
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
        display.show(str("!"))
        return

def on_callback_req(topic, python_code):
    try:
        exec(python_code)
        err = ""
    except Exception as e:
        err = str(e)

    result = get_sensors()
    result["err"] = err
    uart.write(bytes(str(result)+"\n", 'utf-8'))

r_merge = b''
while True:
    r = uart.readline()
    if r:
        r_merge += r
        if r_merge.startswith(b'{') and r_merge.endswith(b'\r\n'):
            d = get_topic_and_data(r_merge)
            if d:
                topic, python_code = d
                on_callback_req(topic, python_code)
            r_merge = b''
