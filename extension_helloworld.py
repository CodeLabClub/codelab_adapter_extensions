import time, threading, subprocess
from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class HelloworldExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)

    def run(self):
        while True:
            message = self.read()
            if message["topic"] == "eim":
                subprocess.call("say {}".format(message["data"]),shell=True)

export = HelloworldExtension

