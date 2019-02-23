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
        self.TOPIC = "eim/mpfshell"
        
        try:
            from mp.mpfshell import MpFileShell

            self.mpfs = MpFileShell(True, True, True, True)

            self.logger.error(self.mpfs._MpFileShell__is_open()) # check state dont delete

        except Exception as e:
            self.logger.error(get_traceback())
            
        return 

        try:
            self.mpfs = MpFileShell(True, True, True, True)

            result = find_devices()
            if len(result) is 0:
                self.logger.error("serial not found!")
            else:
                self.logger.error(result[-1])
            
            self.logger.error(self.mpfs._MpFileShell__is_open())
            with self.stdoutIO() as s:
                self.logger.error(self.mpfs.do_o('ser:' + result[-1]))
            self.logger.error(s.getvalue())
            self.logger.error(self.mpfs._MpFileShell__is_open())
            
        except Exception as e:
            self.logger.error(get_traceback())
            

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def open_device(self, dev_name):
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
            
            # self.logger.error(self.mpfs._MpFileShell__is_open())
            if self.mpfs._MpFileShell__is_open() is False:

                with self.stdoutIO() as s:
                    self.mpfs.do_o(str(dev_name))
                    
                output = s.getvalue()
            else:
                output = 'Already connected'

        except Exception as e:
            output = str(e)
            self.logger.error(get_traceback())
        return output

    def exec_pycode(self, mpy_code):
        self.logger.info("exec_pycode : {}".format(mpy_code))
        try:
            
            # self.logger.error(self.mpfs._MpFileShell__is_open())
            if self.mpfs._MpFileShell__is_open() is True:

                with self.stdoutIO() as s:
                    self.mpfs.do_e(str(mpy_code))
                    
                output = s.getvalue()
            else:
                output = 'device not connected'

        except Exception as e:
            output = str(e)
            self.logger.error(get_traceback())
        return output

    def run(self):
        while self._running:
            try:
                message  = self.read() # python code
                # self.logger.debug(message)
                topic = message.get("topic")
                if self.TOPIC in topic:
                    data = message.get('payload')
                    if 'open' in topic:
                        message = {
                            "topic": topic, 
                            "payload": str(self.open_device(data)).rstrip()
                        }
                        self.publish(message)
                    if 'exec' in topic:
                        message = {
                            "topic": topic, 
                            "payload": str(self.exec_pycode(data)).rstrip()
                        }
                        self.publish(message)
                    if 'isconnected' in topic:
                        message = {
                            "topic": topic,
                            "payload": str(self.mpfs._MpFileShell__is_open())
                        }
                        self.publish(message)
                    if 'close' in topic:
                        
                        self.mpfs.do_q(None)
                        self.mpfs = MpFileShell(True, True, True, True)

                        message = {
                            "topic": topic,
                            "payload": str(self.mpfs._MpFileShell__is_open())
                        }
                        self.publish(message)
            except Exception as e:
                self.logger.error(get_traceback())
        self.mpfs.do_q(None)

export = MpfshellExtension