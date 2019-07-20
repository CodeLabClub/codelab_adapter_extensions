from io import StringIO
import contextlib
import sys
# import subprocess
# import webbrowser
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

import traceback
def get_traceback():
    fp = StringIO()
    traceback.print_exc(file=fp)
    message = fp.getvalue()
    return message

import serial
from serial.tools.list_ports import comports

def find_devices(ids = [(0x1A86, 0x7523), ]):
    devs = []
    for port in comports():
        # self.logger.error(port)
        if (port.vid, port.pid) in ids:
            devs.append(port.device)
            # self.logger.error(port.device)
    return devs

import json

from mp.mpfshell import MpFileShell

class MpfshellExtension(Extension):

    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.topic = "eim/mpfshell/"
        self.cache = { } # mpfshell class cache

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def open_device(self, mpfs_name, dev_name):
        self.logger.info("open_device : {}".format(dev_name))
        try:
            # data = json.loads(message.get('data'))
            if dev_name is None or len(dev_name) < 1:
                result = find_devices()
                if len(result) is 0:
                    self.logger.info("serial not found!")
                    return "serial not found!"
                else:
                    self.logger.info(result[-1])
                dev_name = result[-1]
            
            if mpfs_name not in self.cache:
                self.cache[mpfs_name] = MpFileShell(True, True, True, True)

            # self.logger.error(self.mpfs._MpFileShell__is_open())
            if self.cache[mpfs_name]._MpFileShell__is_open() is False:

                with self.stdoutIO() as s:
                    self.cache[mpfs_name].do_o(str(dev_name))
                    
                output = s.getvalue()
            else:
                output = 'Already connected'

        except Exception as e:
            output = str(e)
            self.logger.error(get_traceback())
        return output

    def exec_pycode(self, mpfs_name, mpy_code):
        self.logger.info("exec_pycode : {}".format(mpy_code))
        try:
            
            # self.logger.error(self.cache[mpfs_name]._MpFileShell__is_open())
            if mpfs_name in self.cache and self.cache[mpfs_name]._MpFileShell__is_open() is True:

                with self.stdoutIO() as s:
                    self.cache[mpfs_name].do_e(str(mpy_code))
                    
                output = s.getvalue()
            else:
                output = 'device not connected'

        except Exception as e:
            output = str(e)
            self.logger.error(get_traceback())
        return output

    def run(self):
        try:
            while self._running:
                try:
                    message  = self.read() # python code
                    # self.logger.debug(message)
                    topic = message.get("topic")
                    if self.TOPIC in topic:
                        data = message.get('payload')
                        obj = topic.split('/')
                        mpfs_name = 'default' if len(obj) < 4 else obj[3]
                        self.logger.debug(mpfs_name)
                        if 'open' in topic:
                            message = {
                                "topic": topic, 
                                "payload": str(self.open_device(mpfs_name, data)).rstrip()
                            }
                            self.publish(message)
                        if 'exec' in topic:
                            message = {
                                "topic": topic, 
                                "payload": str(self.exec_pycode(mpfs_name, data)).rstrip()
                            }
                            self.publish(message)
                        if 'isconnected' in topic:
                            message = {
                                "topic": topic,
                                "payload": str(self.cache[mpfs_name]._MpFileShell__is_open())
                            }
                            self.publish(message)
                        if 'close' in topic:
                            self.cache[mpfs_name].do_close(None)
                            message = {
                                "topic": topic,
                                "payload": str(self.cache[mpfs_name]._MpFileShell__is_open())
                            }
                            self.publish(message)
                except Exception as e:
                    self.logger.error(get_traceback())
        except Exception as e:
            self.logger.error(get_traceback())
        finally:
            # delete
            for mpfs in self.cache:
                mpfs.do_q(None)

export = MpfshellExtension