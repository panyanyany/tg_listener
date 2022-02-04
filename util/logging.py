import logging


class MyAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        msg = msg.replace('\n', '\n'+' '*4)
        return msg, kwargs


class ContextFilter(logging.Filter):
    """
    [doc](https://docs.python.org/2/howto/logging-cookbook.html#using-filters-to-impart-contextual-information)
    """
    LVLNAMES = {
        logging.DEBUG: 'DBG',
        logging.INFO: 'INF',
        logging.WARNING: 'WRN',
        logging.ERROR: 'ERR',
        logging.CRITICAL: 'CRT',
    }

    def filter(self, record):

        record.lvlname = self.LVLNAMES[record.levelno]
        # record.message = record.message.replace('\n', '\n' + ' '*4)
        return True


class IndentDi(object):
    def emit(self, record):
        try:
            msg = self.format(record)
            msg = msg.replace("\n", "\n" + ' '*4)
            self.stream.write(msg + '\n')
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class ConsoleHandler(IndentDi, logging.StreamHandler): pass


class RotatingFileHandler(IndentDi, logging.handlers.TimedRotatingFileHandler): pass
