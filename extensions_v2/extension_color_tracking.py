import subprocess
import time
from codelab_adapter.core_extension import ControllerExtension
from codelab_adapter.utils import get_server_file_path
from codelab_adapter.utils import get_python3_path


class ColorTrackingControllerExtension(ControllerExtension):
    '''
    use to control HA server
    '''

    def __init__(self):
        super().__init__()
        self.server_extension_id = "eim/ColorTracking"
        self.EXTENSION_ID = f"{self.server_extension_id}/control"  # default eim
        self.server_file = get_server_file_path("color_tracking_server.py")

    def run(self):
        python3_path = get_python3_path()
        camera = 1 # 0: mac 1: usb
        cmd = f'{python3_path} {self.server_file} --camera {camera}' # 0
        self.server = subprocess.Popen(cmd,shell=True)  # 发送ctrl c，但使用消息意味着可以分布式
        while self._running:
            time.sleep(0.1)

export = ColorTrackingControllerExtension