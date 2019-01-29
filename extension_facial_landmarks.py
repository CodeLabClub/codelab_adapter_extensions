import sys
sys.path.append("/usr/local/lib/python3.6/site-packages")

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
# 调度程序，拿到脸部程序输出的数据，每次一行
import subprocess
import json
import time

# import sys
# sys.stdout.flush()


class FaceExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        '''
        run 会被作为线程调用
        当前插件功能:
            往scratch不断发送信息
        '''
        cmd = "/usr/local/bin/python3 /Users/wuwenjie/mylab/codelabclub/ai/real-time-facial-landmarks/video_facial_landmarks.py --shape-predictor /Users/wuwenjie/mylab/codelabclub/ai/real-time-facial-landmarks/shape_predictor_68_face_landmarks.dat"
        # cmd = "ls"
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while self._running:
            try:
                out = process.stdout.readline().strip()
                out_json = json.loads(out)
                # out_json = {"shape_data":{"hello":[1,2,3,[4,5]]}}
                print(out_json)
            except:
                continue
            message = {"topic": "eim", "message": out_json.get("shape_data")} # 就是原始数据本身
            self.publish(message)
            # time.sleep(1)
            '''
            todo
                [x] eim能发送和解析json
                    字符串模式和json模式，自动
                [x] 添加一个前端json scratch3 extension 与python交互
                    [x] 1. 处理取得python的数据，list dict ，eim保持数据类型
                    2. 发送前端颜色数据，也需要json
            '''
        subprocess.Popen.kill(process)


export = FaceExtension
