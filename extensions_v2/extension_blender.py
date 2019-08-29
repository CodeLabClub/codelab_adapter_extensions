from codelab_adapter.core_extension import ControllerExtension
from codelab_adapter.utils import get_server_file_path


class BlenderControllerExtension(ControllerExtension):
    '''
    use to control VectorNode(server)
    '''

    def __init__(self):
        super().__init__()
        self.server_extension_id = "eim/blender"
        self.EXTENSION_ID = f"{self.server_extension_id}/control"  # default eim
        # 分布式的节点，手动启动
        self.server_file = None


export = BlenderControllerExtension
