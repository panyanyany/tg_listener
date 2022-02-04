import logging

from scrapy.commands import ScrapyCommand

from util.sys_util import ProcessList, kill_current_process

logger = logging.getLogger(__name__)


class SingletonCommand(ScrapyCommand):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def __init_subclass__(cls, **kwargs):
        name = cls.__module__.split('.')[-1]

        old_init = cls.run

        def run(self, *args, **kwargs):
            if not ProcessList.is_singleton(name):
                logger.info('already running: %s', name)
                kill_current_process()
            old_init(self, *args, **kwargs)

        cls.run = run
