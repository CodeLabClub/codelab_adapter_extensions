import time
import base64
import pathlib
import re
import itertools
import io

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, open_path_in_system_file_manager, install_requirement

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


def decode_image(src, name):
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src,
                       re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")
    '''
    img = base64.urlsafe_b64decode(data) # todo 放在内存中 base64 to cv2
    filename = "{}.{}".format(name, ext)
    with open(filename, "wb") as f:
        f.write(img)
    return filename
    '''
    # img = cv2.imread(io.BytesIO(base64.urlsafe_b64decode(data)))
    decoded_data = base64.urlsafe_b64decode(data)
    np_data = np.fromstring(decoded_data, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    return img


'''
# https://blog.csdn.net/haveanybody/article/details/86494063
def base64_cv2(base64_str):
    #import numpy as np
    imgString = base64.b64decode(base64_str)
    nparr = np.fromstring(imgString,np.uint8)  
    image = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    return image
'''


def vector_angle(a, b):
    # 正负号
    # import numpy as np
    x = np.array(a)
    y = np.array(b)
    # 两个向量
    Lx = np.sqrt(x.dot(x))
    Ly = np.sqrt(y.dot(y))
    #相当于勾股定理，求得斜线的长度
    cos_angle = x.dot(y) / (Lx * Ly)
    #求得cos_sita的值再反过来计算，绝对长度乘以cos角度为矢量长度，初中知识。。
    # print(cos_angle)
    angle = np.arccos(cos_angle)
    # angle2=angle*360/2/np.pi
    angle2 = angle * 360 / 2 / np.pi
    #变为角度
    if b[1] < 0:
        return -1 * angle2
    else:
        return angle2
    # print(angle2)


class PhysicalBlocksExtension(AdapterNode):
    '''
    todo 积木
        获取当前 marker 列表(从左到右 从上到下)
        获取marker的位置，默认是中心点坐标
            获取某个积木在试图中的位置
        获取某个积木的旋转角（用两个点的坐标来计算吗）
    key value
    '''
    NODE_ID = "eim/node_physical_blocks"
    HELP_URL = "https://adapter.codelab.club/extension_guide/physical_blocks/"
    DESCRIPTION = "在一张桌子上对实物进行编程"
    REQUIREMENTS = ["opencv-contrib-python"]
    WEIGHT = 100

    def __init__(self):
        super().__init__() # logger=logger

    def _install_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            import cv2
        except ModuleNotFoundError:
            self.pub_notification(f'try to install {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} installed!')
        import cv2
        import numpy as np
        global cv2, np

    def _get_marker_corners_ids(self, img):
        frame = img
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        # aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100) #
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            frame, aruco_dict, parameters=parameters)
        return corners, ids, rejectedImgPoints

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

    def _sort_with_xy(self, ids_with_xy):
        return sorted(ids_with_xy,
                      key=lambda x: x[1] + 3 * x[2])  # x + 10y 多排问题， y会极大使数字变大

    def get_marker_angle(self, img, content):
        # 中心点的坐标
        marker_id = int(content.get("marker_id"))
        corners, ids, _ = self._get_marker_corners_ids(img)  # 丢到js里做分析？
        try:
            ids = list(itertools.chain.from_iterable(ids))
        except:
            ids = []
        logger.debug(f'all table ids: {ids}')
        if marker_id in ids:
            # 找到id
            index = ids.index(marker_id)
            target_corner = corners[index]
            x1, y1 = target_corner[:, 0][0]  # 左上角的点，第1个
            x2, y2 = target_corner[:, 1][0]  # 右上角的点，第2个
            # todo 求角度
            a = [1, 0]
            b = [x2 - x1, y2 - y1]
            return vector_angle(a, b)
            # return {"x1": float(x1), "y1": float(y1)}
        else:
            return "None"  # 角度不会是 负数

    def get_marker_position(self, img, content):
        marker_id = int(content.get("marker_id"))
        xy = content.get("xy")
        corners, ids, _ = self._get_marker_corners_ids(img)
        try:
            ids = list(itertools.chain.from_iterable(ids))
        except:
            ids = []
        logger.debug(f'all table ids: {ids}')
        if marker_id in ids:
            # 找到id
            # 两个角点的坐标，求夹脚
            index = ids.index(marker_id)
            target_corner = corners[index]
            # x1 = target_corner[:, 0].mean()
            # y1 = target_corner[:, 1].mean()
            x1, y1 = target_corner[:, 0][0]  # 左上角的点，第1个
            x1_scratch = x1 - 240
            y1_scratch = -1 * y1 + 180
            # target_corner[:, 1][0] # 右上角的点，第2个
            return {"x": float(x1_scratch), "y": float(y1_scratch)}[xy]
        return "None"

    def get_markers_id_list(self, img, content):
        corners, ids, _ = self._get_marker_corners_ids(img)
        ids_with_xy = self._ids_with_xy(corners, ids)
        marker_ids_xy = [str(i[0]) for i in self._sort_with_xy(ids_with_xy)]
        logger.debug(f'marker ids : {marker_ids_xy}')
        return marker_ids_xy

    def _handle(self, action, imgdata, message_id, content):
        action_map = {
            "get_markers_id_list": self.get_markers_id_list,
            "get_marker_position": self.get_marker_position,
            "get_marker_angle": self.get_marker_angle
        }
        codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"
        name = codelab_adapter_dir / 'physical_blocks'
        # 图片保存到本地 ~/codelab_adapter/physical_blocks.png
        # filename = decode_image(imgdata, name) # todo 优化，不要保存
        img = decode_image(imgdata, name)
        if action_map.get(action, None):
            result = action_map.get(action)(img, content)

            message = self.message_template()
            message["payload"]["content"] = result
            message["payload"]["message_id"] = message_id
            self.publish(message)

    def extension_message_handle(self, topic, payload):
        '''
        content 必须包含2个 key
            action
                get_markers_id_list
                get_marker_position 中心点
                get_marker_angle  角度
            imgdata
        '''
        content = payload.get("content", None)  # video积木可能为空
        # 使用 dict 处理多种信息
        if content and type(content) == dict and ("data:image" in content.get(
                'imgdata', "")):
            # if content and (type(content) == str) and ("data:image" in content):
            action = content['action']
            imgdata = content['imgdata']
            message_id = payload['message_id']
            self._handle(action, imgdata, message_id, content)
        else:
            payload["content"] = "image data error"
            self.publish({"payload":payload})

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