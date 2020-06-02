import time
import base64
import pathlib
import re

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, open_path_in_system_file_manager, install_requirement

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")

def decode_image(src, name):
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")
    img = base64.urlsafe_b64decode(data)
    filename = "{}.{}".format(name, ext)
    with open(filename, "wb") as f:
        f.write(img)
    return filename


class PhysicalBlocksExtension(AdapterNode):
    NODE_ID = "eim/node_physical_blocks"
    HELP_URL = "https://adapter.codelab.club/extension_guide/physical_blocks/"
    DESCRIPTION = "在一张桌子上对实物进行编程"
    REQUIREMENTS = ["opencv-contrib-python"]

    def __init__(self):
        super().__init__()

    def _install_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            import cv2
        except ModuleNotFoundError:
            self.pub_notification(f'try to install {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} installed!')
        import cv2
        global cv2

    def _ids_with_xy(self, corners, ids):
        sort_ids = []
        try:
            if len(ids):
                for i in range(len(ids)):
                    c = corners[i][0]
                    x = c[:, 0].mean()
                    y = c[:, 1].mean()
                    sort_ids.append((ids[i][0], x, y))
        except:
            pass
        return sort_ids

    def _sort_with_x(self, ids_with_xy):
        return sorted(ids_with_xy, key=lambda x: x[1] + 3 * x[2])  # x + 10y 多排问题， y会极大使数字变大

    def analyse_marker(self, filename):
        frame = cv2.imread(filename)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        ids_with_xy = self._ids_with_xy(corners, ids)
        return [i[0] for i in self._sort_with_x(ids_with_xy)]  # i[0] -> marker id

    def extension_message_handle(self, topic, payload):
        content = payload.get("content", None)  # video积木可能为空
        if content and (type(content) == str) and ("data:image" in content):
            codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"
            imgdata = content
            name = codelab_adapter_dir / 'physical_blocks'
            filename = decode_image(content, name) # 图片保存到本地 ~/codelab_adapter/physical_blocks.png
            sorted_ids = self.analyse_marker(filename)  # todo object
            payload["content"] = [str(i) for i in sorted_ids]  # {"a": sorted_ids}
            logger.debug(f'marker ids to send: {payload["content"]}')
            message = {"payload": payload}
            self.publish(message)

    def run(self):
        self._install_requirement_or_import()
        while self._running:
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        node = PhysicalBlocksExtension()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        if node._running:
            node.terminate()  # Clean up before exiting.