import os
import queue
import time

from codelab_adapter_client import AdapterNode
import yeelight
from yeelight import transitions

def cmd_run(cmd):
    os.system(cmd)


class YeeLightController:
    def __init__(self):
        self.bulbs = yeelight.discover_bulbs()

    def get_bulb(self, index):
        ip_addr = self.bulbs[index].get('ip')
        bulb = yeelight.Bulb(ip_addr)
        return bulb

    def turn_on(self, index):
        bulb = self.get_bulb(index)
        result = bulb.turn_on()
        return result

    def turn_off(self, index):
        bulb = self.get_bulb(index)
        result = bulb.turn_off()
        return result

    def set_rgb(self, index, r, g, b):
        bulb = self.get_bulb(index)
        result = bulb.set_rgb(r, g, b)
        return result

    def set_brightness(self, index, brightness):
        bulb = self.get_bulb(index)
        result = bulb.set_brightness(brightness)
        return result

    def set_temperature(self, index, temp):
        bulb = self.get_bulb(index)
        result = bulb.set_color_temp(temp)
        return result

    def set_flow(self, index, flow_preset, count=0):
        bulb = self.get_bulb(index)
        flow = yeelight.Flow(
            count=count,
            transitions=flow_preset,
        )
        result = bulb.start_flow(flow)
        return result


class YeelightNode(AdapterNode):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/yeelight"  # default: eim
        self.q = queue.Queue(maxsize=1)
        self.bulb_ctl = YeeLightController()

    def extension_message_handle(self, topic, payload):
        self.logger.info(topic)
        self.logger.info(payload)
        self.q.put(payload)

    def exit_message_handle(self, topic, payload):
        self.terminate()

    def run(self):
        while self._running:
            time.sleep(0.1)
            if not self.q.empty():
                payload = self.q.get()
                self.logger.info(f'python: {payload}')
                message_id = payload.get("message_id")
                python_code = payload["content"]
                try:
                    output = eval(python_code, {"__builtins__": None}, {
                        "yeelight": yeelight,
                        "bulb_ctl": self.bulb_ctl,
                        "transitions": transitions
                    })
                except Exception as e:
                    output = e
                payload["content"] = str(output)
                message = {"payload": payload}
                self.publish(message)


if __name__ == "__main__":
    try:
        node = YeelightNode()
        node.receive_loop_as_thread()  # run extension_message_handle, noblock(threaded)
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.
