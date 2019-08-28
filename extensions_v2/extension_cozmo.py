from codelab_adapter.core_extension import ControllerExtension
from codelab_adapter.utils import get_server_file_path

class CozmoControllerExtension(ControllerExtension):
    '''
    use to control CozmoNode(server)
    '''

    def __init__(self):
        super().__init__()
        self.server_extension_id = "eim/cozmo"
        self.EXTENSION_ID = f"{self.server_extension_id}/control"  # default eim
        self.server_file = get_server_file_path("cozmo_server.py")


export = CozmoControllerExtension
