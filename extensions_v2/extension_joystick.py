from codelab_adapter.core_extension import ControllerExtension
from codelab_adapter.utils import get_server_file_path


class JoystickControllerExtension(ControllerExtension):
    '''
    use to control VectorNode(server)
    '''

    def __init__(self):
        super().__init__()
        self.server_extension_id = "eim/joystick"
        self.EXTENSION_ID = f"{self.server_extension_id}/control"  # default eim
        self.server_file = get_server_file_path("joystick_server.py")


export = JoystickControllerExtension
