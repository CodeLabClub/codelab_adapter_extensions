import time
import os
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement

class KanoMotionExtension(AdapterNode):
    NODE_ID = "eim/node_motionSensor"
    HELP_URL = "https://adapter.codelab.club/extension_guide/extension_kano_motion/"  # Documentation page for the project
    VERSION = "1.0"  # extension version
    DESCRIPTION = "kano motion sensor"
    ICON_URL = ""
    REQUIRES_ADAPTER = ""  # ">= 3.2.0"
    REQUIREMENTS = ["kano-community-sdk"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            from communitysdk import list_connected_devices, MotionSensorKit
        except ModuleNotFoundError:
            self.pub_notification(f'正在安装 {" ".join(requirement)}...')
            # 只有 local python 下才可用，adapter内置的python无法使用pip（extension）
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} 安装完成')
        from communitysdk import list_connected_devices, MotionSensorKit
        global list_connected_devices, MotionSensorKit

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'eim message:{payload}')
        self.publish({"payload": payload})

    def _publish(self, content):
        message = self.message_template()
        message["payload"]["content"] = content
        self.publish(message)

    def proximity_loop(self, msk):
        # asyncio thread
        if msk != None:

            def on_gesture(gestureValue):
                # print('Gesture detected:', gestureValue)
                self._publish({"gesture": gestureValue})

            info = 'Motion Sensor 已连接'
            self.pub_notification(info)
            # print(info)
            msk.set_mode('gesture')
            msk.on_gesture = on_gesture
        else:
            error = "未发现 Motion Sensor"
            self.pub_notification(error)

    def run(self):
        '''
        run as thread
        '''
        self._import_requirement_or_import()

        devices = list_connected_devices()  # hack后
        msk_filter = filter(lambda device: isinstance(device, MotionSensorKit),
                            devices)
        msk = next(msk_filter, None)  # Get first Motion Sensor Kit
        self.proximity_loop(msk)
        while self._running:
            time.sleep(1)

    def terminate(self, **kwargs):
        super().terminate(**kwargs)
        os._exit(0)


def main(**kwargs):
    try:
        node = KanoMotionExtension(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    finally:
        if node._running:
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()