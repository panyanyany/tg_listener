from time import sleep


class ThreadStatus:
    running = True


class WithStatus:
    status: ThreadStatus


class CancelableSleep(WithStatus):
    def sleep(self, secs):
        for i in range(1, secs):
            if self.status.running:
                sleep(1)
