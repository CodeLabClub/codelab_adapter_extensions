import time
import zmq

from codelab_adapter.core_extension import Extension
from codelab_adapter import settings



class BlenderExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)
        self.TOPIC = "eim/blender"

    def run(self):
        # connect req
        port = 38785
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect ("tcp://localhost:%s" % port)

        while self._running:
            message = self.read()
            topic = message.get("topic")
            if topic == self.TOPIC:
                socket.send_json(message)
                print("send to blender server {}".format(message))
                result = socket.recv_json().get("output")

                message2scratch = {}
                message2scratch["topic"] = self.TOPIC
                message2scratch["payload"] = result
                message2scratch["messageID"] = message["messageID"]
                self.publish(message2scratch)
                # print("result: {}".format(result))
        socket.close()
        context.term()

# {"topic":"eim/blender","payload":"bpy.data.objects['Cube'].location.x += 1"}
export = BlenderExtension
