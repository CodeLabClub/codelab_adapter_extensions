from microbit import *
import radio
import gc
import machine

__version__ = "0.4"

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

# https://microbit-micropython.readthedocs.io/en/v1.0.1/radio.html
# https://microbit-challenges.readthedocs.io/en/latest/tutorials/radio.html#putting-it-together
radio.on()
radio.config(channel=1)
radio.config(power=7)

uart.init(115200)
# display.scroll("welcome!", wait=False, loop=False)
display.show(Image.HAPPY)
# TOPIC = "eim/usbMicrobit"

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
    details = radio.receive_full()
    # msg, rssi, timestamp = details
    dic = {
        # "topic": TOPIC,
        "payload": {
            "button_a": a,
            "button_b": b,
            "x": x,
            "y": y,
            "z": z,
            "pin_one_analog_input": pin_one_analog_input,
            "pin_two_analog_input": pin_two_analog_input,
            "gesture": gesture,
            "radio_data": details
        }
    }
    return dic

def get_msgid_and_data(b):
    if gc.mem_free() < 2000:
        gc.collect()
    try:
        b = b.strip()
        json_str = str(b, 'utf-8')
        json = eval(json_str)
        # :todo check key data, msgid
        msgid = str(json.get('msgid'))
        data = str(json.get("payload"))
        return msgid, data
    except Exception as e:
        display.show(str("!"))
        return "err", str(e)

def on_callback_req(msgid, python_code):
    try:
        output = eval(python_code)
    except Exception as e:
        output = str(e)

    result = get_sensors() # payload
    result["output"] = output
    result["msgid"] = msgid
    result["version"] = __version__
    uart.write(bytes(str(result)+"\n", 'utf-8'))

r_merge = b''
while True:
    if gc.mem_free() < 2000:
        gc.collect()
    # r = uart.readline(1024)
    r = uart.readline()
    if r:
        r_merge += r
        if r_merge.startswith(b'{') and r_merge.endswith(b'\r\n'):
            d = get_msgid_and_data(r_merge)
            if d:
                if d[0] == "err":
                    result = {"payload":"input error"}
                    result["output"] = d[1]
                    uart.write(bytes(str(result)+"\n", 'utf-8'))
                    machine.reset()
                else:
                    msgid, python_code = d
                    on_callback_req(msgid, python_code)
            r_merge = b''