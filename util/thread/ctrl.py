import signal
import sys
from time import sleep

import attr


@attr.s
class ThreadStatus:
    running = attr.ib(default=True)


class WithStatus:
    status: ThreadStatus


class CancelableSleep(WithStatus):
    def sleep(self, secs: int):
        for i in range(1, secs):
            if self.status.running:
                sleep(1)

    def handle_singal(self):
        def handler(sig, frame):
            print('You pressed Ctrl-C!', sig)
            # 告诉 self.sleep 下一秒醒来
            self.status.running = False
            sys.exit(1)

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        if sys.platform.startswith('win'):
            signal.signal(signal.SIGBREAK, handler)
