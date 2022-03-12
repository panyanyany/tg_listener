import logging

logger = logging.getLogger(__name__)


class Cancelable:
    running = False

    def start(self):
        self.running = True

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False
