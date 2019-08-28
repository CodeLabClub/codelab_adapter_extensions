from codelab_adapter.core_extension import ControllerExtension
from codelab_adapter.utils import get_server_file_path


class HAControllerExtension(ControllerExtension):
    '''
    use to control HA server
    '''

    def __init__(self):
        super().__init__()
        self.server_extension_id = "eim/HA_gateway"
        self.EXTENSION_ID = f"{self.server_extension_id}/control"  # default eim
        self.server_file = get_server_file_path("HA_server.py")


export = HAControllerExtension