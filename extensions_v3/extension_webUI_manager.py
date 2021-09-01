import time

from codelab_adapter.core_extension import Extension
from codelab_adapter_client.topic import GUI_TOPIC
from codelab_adapter_client.utils import open_path, is_win


class WebUI_Manager(Extension):
    NODE_ID = "adapter/WebUI_Manager"
    DESCRIPTION = "通过响应自定义消息扩展 WebUI"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extension_message_handle(self, topic, payload):
        content = payload["content"]
        if content == "openHostsDir":
            # unix/windows
            # unix /etc/hosts
            # windows C:\Windows\System32\drivers\etc
            if is_win():
                hosts_path = 'C:\Windows\System32\drivers\etc'
            else:
                hosts_path = '/etc'
            self.logger.debug(payload)
            open_path(hosts_path)

    def run(self):
        while self._running:
            time.sleep(0.5)


export = WebUI_Manager