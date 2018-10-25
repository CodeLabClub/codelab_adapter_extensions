import sys;sys.path.append("/usr/local/lib/python3.6/site-packages")
from furl import furl
from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class ThirdPartyLibraryExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        f = furl('http://www.google.com/?one=1&two=2')
        f.args['three'] = '3'
        self.logger.info(f.url)
        while self._running:
            message = self.read()
            self.logger.debug("message:%s",str(message))

export = ThirdPartyLibraryExtension
