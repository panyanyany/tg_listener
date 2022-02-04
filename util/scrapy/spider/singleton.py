# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
from scrapy.exceptions import CloseSpider

from util.sys_util import ProcessList, kill_current_process
import logging

logger = logging.getLogger(__name__)


class Singleton(scrapy.Spider):
    def __init_subclass__(cls, **kwargs):
        name = cls.__module__.split('.')[-1]

        old_fn = cls.start_requests

        def new_fn(self):
            if not ProcessList.is_singleton(name):
                logger.info('already running: %s', name)
                kill_current_process()
            return old_fn(self)

        cls.start_requests = new_fn
