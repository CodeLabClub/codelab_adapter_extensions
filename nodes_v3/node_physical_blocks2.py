import time
import base64
import pathlib
import re
import itertools
import io

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, open_path_in_system_file_manager, install_requirement

import cv2 # opencv-contrib-python
import numpy as np

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")

'''
作为单独进程调试，使用print

cython build，目前支持windows mac，使用windows电脑商业方案即可。linux对opencv处理复杂，未来考虑

linux无法使用了？

第二代 100 个 block

第三代 1000个？

兼容性

逐渐淘汰 2/3

liuqing linux 不能使用最新的。单独给源码
'''

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
    # np_data = np.fromstring(decoded_data, np.uint8)
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
    angle = np.arccos(cos_angle)
    # angle2=angle*360/2/np.pi
    angle2 = angle * 360 / 2 / np.pi
    #变为角度
    if b[1] < 0:
        return -1 * angle2
    else:
        return angle2


class PhysicalBlocksExtension(AdapterNode):
    '''
    todo 积木
        获取当前 marker 列表(从左到右 从上到下)
        获取marker的位置，默认是中心点坐标
            获取某个积木在试图中的位置
        获取某个积木的旋转角（用两个点的坐标来计算吗）
    key value
    '''
    NODE_ID = "eim/node_physical_blocks2"
    HELP_URL = "https://adapter.codelab.club/extension_guide/physical_blocks/"
    DESCRIPTION = "在一张桌子上对实物进行编程"
    # REQUIREMENTS = ["opencv-contrib-python"]
    WEIGHT = 99.9
    VERSION = "2.1.0"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)  # logger=logger

    def _get_marker_corners_ids(self, img):
        frame = img
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250) # 50
        # aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        # aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_1000)
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            frame, aruco_dict, parameters=parameters)
        return corners, ids, rejectedImgPoints

    def _sort_with_center_xy(self, markers_info):
        # markers_info is dict, items[1] value
        # x + 10y 多排问题， y会极大使数字变大
        return sorted(
            markers_info.items(),
            key=lambda items: items[1]["center_x"] + 3 * items[1]["center_y"])

    def _get_center_xy(self, img, corner):
        x = corner[:, 0].mean()  # 中心点
        y = corner[:, 1].mean()
        return self._to_scrtach_coordinate_system(img, x, y)

    def _to_scrtach_coordinate_system(self, img, x, y):
        '''
        img 480/360
        todo 
            检测图片信息
            720/540
            960/720
            1080/810
        '''
        height, width, channels = img.shape
        self.logger.info(f"width:{width}; height:{height}")
        return ((x - width/2)*(480/width), (-1 * y + height/2)*(360/height))

    def get_markers_info(self, img, content):
        corners, ids, _ = self._get_marker_corners_ids(img)  # 所有信息
        try:
            ids = list(itertools.chain.from_iterable(ids)) # 摊平
        except:
            ids = []
        logger.debug(f'all table ids: {ids}')
        markers_info = {}
        _markers_count = {}
        # for marker_id in ids:
        for i in range(len(ids)):
            # 两个角点的坐标，求夹脚
            marker_id = int(ids[i])
            index = ids.index(marker_id)
            target_corner = corners[index]
            '''
            # print(f"{marker_id} {target_corner}")
                33 [[[313. 202.]
                [338. 213.]
                [327. 238.]
                [302. 226.]]]
            '''
            # x1 = target_corner[:, 0].mean()
            # y1 = target_corner[:, 1].mean()
            x1, y1 = target_corner[:, 0][0]  # 左上角的点，第1个
            x1_scratch, y1_scratch = self._to_scrtach_coordinate_system(img, x1, y1)
            # todo 四个点都应该放进来
            # target_corner[:, 1][0] # 右上角的点，第2个
            marker_id = str(marker_id) # 当有多个的时候
            _markers_count[marker_id] = 1
            if marker_id in markers_info:
                _markers_count[marker_id] += 1
                marker_id = f"{marker_id}-{_markers_count[marker_id]}"
            markers_info[marker_id] = {}
            markers_info[marker_id]["x"] = float(x1_scratch)
            markers_info[marker_id]["y"] = float(y1_scratch)

            # 中心点, todo 转化为scratch坐标系
            center_x, center_y = self._get_center_xy(img, target_corner)
            markers_info[marker_id]["center_x"] = float(center_x)
            markers_info[marker_id]["center_y"] = float(center_y)

            # angle , 复合数据，非独立，放在python里计算
            x1, y1 = target_corner[:, 0][0]  # 左上角的点，第1个
            x2, y2 = target_corner[:, 1][0]  # 右上角的点，第2个
            a = [1, 0]
            b = [x2 - x1, y2 - y1]
            markers_info[marker_id]["angle"] = vector_angle(a, b)
            # {33: {'x': 59.0, 'y': 6.0, 'center_x': 236.5, 'center_y': 252.0, 'angle': 22.24901811204658}}
            
        if markers_info:
            marker_ids_xy = [
                str(i[0]) for i in self._sort_with_center_xy(markers_info)
            ]
            markers_info["sorted_ids"] = marker_ids_xy
        else:
            markers_info["sorted_ids"] = []
        return markers_info

    def _handle(self, imgdata, message_id, content):
        codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"
        name = codelab_adapter_dir / 'physical_blocks'
        # 图片保存到本地 ~/codelab_adapter/physical_blocks.png
        # filename = decode_image(imgdata, name) # todo 优化，不要保存
        img = decode_image(imgdata, name)

        markers_info = self.get_markers_info(img, content)  # 格式说明, 顺序 从左到右从上到下
        message = self.message_template()
        message["payload"]["content"] = markers_info
        message["payload"]["message_id"] = message_id
        self.logger.debug(f"markers_info: {markers_info}")
        self.publish(message)

    def extension_message_handle(self, topic, payload):
        content = payload.get("content", None)  # video积木可能为空
        # 使用 dict 处理多种信息
        if content and type(content) == dict and ("data:image" in content.get(
                'imgdata', "")):
            # if content and (type(content) == str) and ("data:image" in content):
            imgdata = content['imgdata']
            message_id = payload.get('message_id', -1) # 可能没有
            # 获取整个列表
            self._handle(imgdata, message_id, content)
        else:
            payload["content"] = "image data error"
            self.publish({"payload": payload})

    def run(self):
        while self._running:
            time.sleep(0.5)


def main(**kwargs):
    try:
        node = PhysicalBlocksExtension(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        if node._running:
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()