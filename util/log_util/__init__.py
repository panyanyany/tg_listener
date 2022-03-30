import glob
import logging
import logging.config
import logging.handlers
import os
import sys
import types
from datetime import datetime, timedelta
from pathlib import Path

import yaml
import codecs

from concurrent_log_handler import ConcurrentRotatingFileHandler

THIS_DIR = os.path.dirname(__file__)


class MyAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """

    def process(self, msg, kwargs):
        msg = msg.replace('\n', '\n' + ' ' * 4)
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

    def __init__(self, ignore_names=None, *args, **kwargs):
        super(ContextFilter, self).__init__(*args, **kwargs)
        self.ignore_names = set(ignore_names or [])
        self.wildcard_ignore_names = []
        for name in self.ignore_names:
            if name.endswith('*'):
                self.wildcard_ignore_names.append(name[:-1])

    def filter(self, record: logging.LogRecord):
        if record.name in self.ignore_names:
            return False
        for wildcard_name in self.wildcard_ignore_names:
            if record.name.startswith(wildcard_name):
                return False
        record.lvlname = self.LVLNAMES[record.levelno]
        # record.message = record.message.replace('\n', '\n' + ' '*4)
        return True


def set_write_method(self):
    def write(self, s):
        repl = '\n' + ' ' * 4
        s = s.replace('\n', repl)
        if s.endswith(repl):
            s = s[:-4]
        return self.write.origin_write(s)

    setattr(write, 'origin_write', self.write)
    bound_method = types.MethodType(write, self)
    setattr(self, 'write', bound_method)
    return


class IndentDi(object):
    pass
    # def emit(self, record):
    #     try:
    #         if not hasattr(self.stream.write, 'origin_write'):
    #             set_write_method(self.stream)
    #         super().emit(record)
    #     except (KeyboardInterrupt, SystemExit):
    #         raise
    #     except:
    #         self.handleError(record)


class ConsoleHandler(IndentDi, logging.StreamHandler): pass


class TimedFileHandler(IndentDi, logging.FileHandler):
    target_filename = None
    TIME_FORMAT = '%Y%m%d-%H%M%S'
    time_format = '%Y%m%d-%H%M%S'
    durations = ['Y', 'm', 'd', 'H', 'M', 'S']
    with_pid = False

    def __init__(self, filename, duration=None, mode='a', encoding=None, delay=False, max_age=3 * 24 * 60,
                 with_pid=True):
        """
        Open the specified file and use it as the stream for logging.
        """
        # Issue #27493: add support for Path objects to be passed in
        filename = os.fspath(filename)
        # keep the absolute path, otherwise derived classes which use this
        # may come a cropper when the current directory changes
        self.baseFilename = os.path.abspath(filename)
        self.with_pid = with_pid

        # time
        assert duration in self.durations
        du_part = []
        for du in self.durations:
            du_part.append('%' + du)
            if du == 'd' and du != duration:
                du_part.append('-')
            if du == duration:
                break
        self.time_format = ''.join(du_part)

        file_dir = os.path.dirname(self.baseFilename)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        self.max_age = max_age
        base_filename, ext = os.path.splitext(self.baseFilename)
        self.clean_old_files(base_filename)

        # filename = '{base_filename}_{time}_{pid}{ext}'
        name_parts = [
            base_filename,
        ]
        name_parts.append(
            datetime.now().strftime(self.time_format)
        )

        # pid
        if with_pid:
            name_parts.append(
                str(os.getpid())
            )
        self.target_filename = '_'.join(name_parts) + ext

        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            # We don't open the stream, but we still need to call the
            # Handler constructor to set level, formatter, lock etc.
            logging.Handler.__init__(self)
            self.stream = None
        else:
            logging.StreamHandler.__init__(self, self._open())

    def _open(self):
        return open(self.target_filename, self.mode, encoding=self.encoding)

    def emit(self, record):
        """
        Emit a record.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        if self.stream is None:
            self.stream = self._open()
            if os.path.exists(self.baseFilename):
                os.remove(self.baseFilename)

        # print('-' * 10, self.with_pid)
        if not self.with_pid:
            # print('*' * 20, os.path.islink(self.baseFilename), os.path.exists(self.baseFilename), self.baseFilename)
            if os.path.exists(self.baseFilename):
                os.remove(self.baseFilename)
            elif os.path.islink(self.baseFilename):
                os.remove(self.baseFilename)
            os.symlink(self.target_filename, self.baseFilename)
        super().emit(record)

    def clean_old_files(self, base_filename):
        results = glob.glob(base_filename + '*')
        results.sort()
        for path in results:
            name_suffix = path.replace(base_filename, '')
            parts = name_suffix.split('_')
            if len(parts) < 2:
                # invalid format
                continue
            timed_part = parts[1].split('.')[0]
            try:
                dt = datetime.strptime(timed_part, self.time_format).astimezone()
                oldest_time = datetime.now().astimezone() - timedelta(minutes=self.max_age)
                if dt < oldest_time:
                    os.remove(path)
            except Exception as e:
                print(e)


class DebugRotatingFileHandler(IndentDi, logging.handlers.BaseRotatingHandler):
    """
    Handler for logging to a set of files, which switches from one file
    to the next when process start
    """

    def __init__(self, filename, mode='a', backupCount=0, encoding=None, delay=False):
        """
        Open the specified file and use it as the stream for logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes and backupCount to allow the file to rollover at
        a predetermined size.

        Rollover occurs whenever the current log file is nearly maxBytes in
        length. If backupCount is >= 1, the system will successively create
        new files with the same pathname as the base file, but with extensions
        ".1", ".2" etc. appended to it. For example, with a backupCount of 5
        and a base file name of "app.log", you would get "app.log",
        "app.log.1", "app.log.2", ... through to "app.log.5". The file being
        written to is always "app.log" - when it gets filled up, it is closed
        and renamed to "app.log.1", and if files "app.log.1", "app.log.2" etc.
        exist, then they are renamed to "app.log.2", "app.log.3" etc.
        respectively.

        If maxBytes is zero, rollover never occurs.
        """
        # If rotation/rollover is wanted, it doesn't make sense to use another
        # mode. If for example 'w' were specified, then if there were multiple
        # runs of the calling application, the logs from previous runs would be
        # lost if the 'w' is respected, because the log file would be truncated
        # on each run.
        super().__init__(filename, mode, encoding, delay)
        self.backupCount = backupCount
        self.pid = None  # os.getpid()

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename,
                                                        i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):
        """
        only rollover on start up
        """
        if not self.pid:
            self.pid = os.getpid()
            return 1
        return 0


class ConcurrentDebugRotatingFileHandler(IndentDi, ConcurrentRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pid = None

    def _shouldRollover(self):
        """
        only rollover on start up
        """
        if not self.pid:
            self.pid = os.getpid()
            return True
        return False


class Config:
    already_setup = False


# setup logging
def setup(ignore_names=None, filename='logs/routines.log', rotate=False, max_age=3 * 24 * 60):
    if Config.already_setup:
        return
    log_cfg_file_path = os.path.join(THIS_DIR, 'logging.yml')
    with codecs.open(log_cfg_file_path, 'r', encoding='utf8') as fp:
        config = yaml.safe_load(fp.read())

    # 为本项目配置单独的 logger, 参考：https://realpython.com/python-logging/
    # logger = logging.getLogger(name)

    # handler = logging.FileHandler('logs/routines.log')
    file_dir = os.path.dirname(filename)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if rotate:
        if sys.platform == 'win32':
            # 并发日志，主要是在 windows 下，防止日志被其他进程锁住导致报错。
            handler = ConcurrentDebugRotatingFileHandler(filename, backupCount=6, encoding='utf8')
        else:
            handler = DebugRotatingFileHandler(filename, backupCount=6, encoding='utf8')
    else:
        # handler = logging.FileHandler(filename, encoding='utf8')
        if sys.platform == 'win32':
            with_pid = True
            duration = 'S'
        else:
            with_pid = False
            duration = 'd'
        handler = TimedFileHandler(filename, duration=duration, encoding='utf8', max_age=max_age, with_pid=with_pid)

    # to file
    file_formater = logging.Formatter(
        config['formatters']['tofile']['format'],
        config['formatters']['tofile']['datefmt'],
    )
    handler.setFormatter(file_formater)
    handler.addFilter(ContextFilter(ignore_names=ignore_names))

    # to console
    console_formater = logging.Formatter(
        config['formatters']['tocons']['format'],
        config['formatters']['tocons']['datefmt'],
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formater)
    console_handler.addFilter(
        ContextFilter(ignore_names=ignore_names + ['scrapy.statscollectors'
                                                   # , 'scrapy.core.engine' 这个不要屏蔽，否则不会在控制台输出错误信息
            , 'scrapy.utils.log'
            , 'scrapy.middleware']))

    # 注意！如果有其他模块已经调用过 basicConfig，则后续的调用都是无效的！
    # https://stackoverflow.com/a/53553516/4683349
    logging.basicConfig(level=logging.DEBUG, handlers=[])
    # 覆盖其他模块的 basicConfig 调用
    # https://stackoverflow.com/questions/11548674/logging-info-doesnt-show-up-on-console-but-warn-and-error-do
    logging.root.setLevel(logging.DEBUG)
    for h in logging.root.handlers:
        logging.root.removeHandler(h)
    logging.root.addHandler(handler)
    logging.root.addHandler(console_handler)

    # 避免让后来的人覆盖 ---- 走自己的路，让别人无路可走
    logging.root.removeHandler = lambda e: e
    logging.root.addHandler = lambda e: e

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception: %s %s" % (exc_type.__name__, exc_value),
                      exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    Config.already_setup = True
    # 避免重复输出
    # logging.root.addHandler(handler)

    # return logger

    # if debug:
    #     config['handlers']['file_handler']['class'] = 'util.log_util.DebugRotatingFileHandler'
    # logging.config.dictConfig(config)
    # besides `LOG_ENABLED = False` in settings.py, another way to disable default Handler of scrapy
    # make sure scrapy could not set root handler in runtime
    # logging.root.addHandler = lambda e: e


class CallbackFilter(logging.Filter):
    """
    A logging filter that checks the return value of a given callable (which
    takes the record-to-be-logged as its only parameter) to decide whether to
    log a record.
    """

    def __init__(self, callback):
        self.callback = callback

    def filter(self, record):
        if self.callback(record):
            return 1
        return 0


def set_independent_levels(module_name, levels, rotated=False):
    # print(sys.argv)
    # filename = sys.argv[1]
    filepath = "logs/{}.{}.log".format(module_name, logging.getLevelName(levels[0]))
    for level in levels:
        set_independent_log(level, filepath, rotated=rotated)


def set_independent_log(level, filename, rotated=False):
    if rotated:
        handler = DebugRotatingFileHandler(filename, backupCount=3)
    else:
        handler = logging.FileHandler(filename)

    # formatter
    formater = logging.Formatter("%(asctime)s|%(levelname)s|> %(message)s", datefmt="%Y-%m-%d %H:%M:%S%z")
    # logging.Formatter.converter = custom_time

    handler.setFormatter(formater)

    # level
    handler.setLevel(logging.DEBUG)

    # 只保留 levels 信息
    def filter_level(record: logging.LogRecord):
        return record.levelno == level

    handler.addFilter(ContextFilter(ignore_names=[], allow_3rd=False))
    handler.addFilter(CallbackFilter(filter_level))

    logging.root.addHandler(handler)


def setup2(module_name):
    # 重置默认的 level，否则 debug, info 都打印不出来
    logging.basicConfig(level=logging.DEBUG, handlers=[])
    set_independent_levels(module_name, [logging.DEBUG])
    set_independent_levels(module_name, [logging.INFO])
    set_independent_levels(module_name, [logging.ERROR, logging.CRITICAL])


default_ignore_names = [
    'peewee*',
    'urllib3*',
    'PIL*',
    # 'scrapy.utils.log*',
    # 'util.*',
    'py.warnings*'
]


def setup3(cmd_level=1, max_age=3 * 24 * 60, ignore_names=None, rm_parents=0):
    """
    :param cmd_level:
        level 1: python lps/cli.py xxx: logs/lps/cli.log
        level 2: python lps/cli.py xxx: logs/lps/cli/xxx.log
    :param max_age:
    :param rm_parents: logs/lps/cli.log --> logs/cli/xxx.log
    :return:
    """
    args = sys.argv[:cmd_level]
    project_root = Path(__file__).parent.parent.parent

    for i, arg in enumerate(args):
        if arg.endswith('.py'):
            # 如果直接在 IDE 里运行, 会出现绝对路径, 比如：
            # /Users/xxx/Library/Caches/pypoetry/virtualenvs/yyy-xp3-MCh4-py3.9/bin/python /private/var/www/xxx/yyy/scripts/listen_chain.py
            # 所以需要把文件的绝对路径转为相对路径，方便后面生成日志路径
            if str(project_root) in arg:
                arg = arg.replace(str(project_root), '').lstrip('/')
            args[i] = arg[:-3]

    dir_path = '/'.join(args)
    parts = dir_path.split('/')

    if len(parts) >= rm_parents:
        parts = parts[rm_parents:]
    dir_path = '/'.join(parts)

    name = os.path.basename(dir_path)

    logfile = Path(__file__).parent.parent.parent.joinpath(
        'logs/{dir_path}/{name}.log'.format(dir_path=dir_path, name=name))
    if not logfile.parent.exists():
        logfile.parent.mkdir(parents=True)
    logging.info('logfile: %s', logfile)
    logging.basicConfig(level=logging.DEBUG, handlers=[])
    setup(ignore_names=ignore_names or default_ignore_names, filename=str(logfile),
          rotate=False,
          max_age=max_age)
