import logging
import os
import shlex
import signal
import sys
from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Union, AnyStr, List, Tuple

import psutil

logger = logging.getLogger(__name__)


class ProcessInfo:
    scrapy_command = ''
    cmdline = []
    ppid = ''
    ctime = 0
    name = ''

    def __init__(self, scrapy_command='', pid=0, cmdline=None, ppid=0, ctime=0, name=None):
        self.scrapy_command = scrapy_command
        self.pid = pid
        self.ppid = ppid
        self.cmdline = cmdline
        self.ctime = ctime
        self.name = name


class ProcessFilter:
    def __init__(self, names):
        self.names = names

    def needed(self, name):
        name = name.lower()
        for my_name in self.names:
            if sys.platform == 'win32':
                my_name = my_name + '.exe'
            if name == my_name:
                return True
        return False


class ProcessList:
    @classmethod
    def get_parents(cls):
        pid = os.getpid()
        proc = psutil.Process(pid)

        error_cnt = 0
        parents = []
        while proc.ppid() > 0:
            try:
                proc = psutil.Process(proc.ppid())
                pinfo = proc.as_dict(attrs=['name', 'cmdline', 'pid', 'ppid'])
                process_info = ProcessInfo(
                    pid=pinfo['pid'],
                    cmdline=pinfo['cmdline'],
                    ppid=pinfo['ppid'],
                    name=pinfo['name'],
                )
                parents.append(process_info)
            except Exception as e:
                error_cnt += 1
                if error_cnt >= 3:
                    break
        return parents

    @classmethod
    def get_processes(cls, only_scrapy=True) -> [ProcessInfo]:
        if only_scrapy:
            proc_filter = ProcessFilter(['scrapy'])
        else:
            proc_filter = ProcessFilter(['scrapy', 'python', 'pipenv', 'bash', 'chrome'])
        processes = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'ppid', 'create_time'])
                if not pinfo['cmdline']:
                    continue
                cmdline = pinfo['cmdline']
                if len(cmdline) < 2:
                    continue
                if sys.platform == 'win32':
                    """
                        {'cmdline': ['C:\\Users\\Administrator\\.virtualenvs\\video_scrapy-slnG20Le\\Scripts\\scrapy.exe', 'monitor'], 'pid': 2128, 'name': 'scrapy.exe'}
                        {'cmdline': ['C:\\Users\\Administrator\\AppData\\Roaming\\Python\\Python36\\Scripts\\pipenv.exe', 'run', 'scrapy', 'monitor'], 'pid': 2424, 'name': 'pipenv.exe'}
                        {'cmdline': ['c:\\users\\administrator\\.virtualenvs\\video_scrapy-slng20le\\scripts\\python.exe', 'C:\\Users\\Administrator\\.virtualenvs\\video_scrapy-slnG20Le\\Scripts\\scrapy.exe', 'monitor'], 'pid': 3128, 'name': 'python.exe'}
                        {'cmdline': ['c:\\users\\administrator\\appdata\\local\\programs\\python\\python36\\python.exe', 'C:\\Users\\Administrator\\AppData\\Roaming\\Python\\Python36\\Scripts\\pipenv.exe', 'run', 'scrapy', 'monitor'], 'pid': 7372, 'name': 'python.exe'}
                    """
                    if not proc_filter.needed(cmdline[0].split(os.sep)[-1]):
                        continue
                    scrapy_command = cmdline[1]
                else:
                    """
                        {'cmdline': ['/Users/pyy/.virtualenvs/video_scrapy-GFobINVM/bin/python3', '/Users/pyy/.virtualenvs/video_scrapy-GFobINVM/bin/scrapy', 'monitor'], 'pid': 98895, 'name': 'python3'}
                    """
                    # print(cmdline[1])
                    if not proc_filter.needed(cmdline[1].split(os.sep)[-1]):
                        continue
                    scrapy_command = cmdline[2]
                processes.append(
                    ProcessInfo(scrapy_command=scrapy_command,
                                pid=pinfo['pid'],
                                cmdline=cmdline,
                                ppid=pinfo['ppid'],
                                ctime=pinfo['create_time'],
                                )
                )
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                logger.error('get process info: %s', e)
        return processes

    @classmethod
    def is_uploading(cls):
        processes = cls.get_processes()
        for process in processes:
            if 'batch_upload' == process.scrapy_command:
                return True
        return False

    @classmethod
    def is_crawling(cls):
        processes = cls.get_processes()
        for process in processes:
            if 'batch_crawl' == process.scrapy_command:
                return True
        return False

    @classmethod
    def is_delogoing(cls):
        processes = cls.get_processes()
        for process in processes:
            if 'delogo' == process.scrapy_command:
                return True
        return False

    @classmethod
    def is_collecting(cls):
        processes = cls.get_processes()
        for process in processes:
            if 'collect_info' == process.scrapy_command:
                return True
        return False

    @classmethod
    def is_monitoring(cls):
        processes = cls.get_processes()
        pid = os.getpid()
        ppid = os.getppid()
        # logger.info('getpid ===== %s, ppid=%s', pid, ppid)
        for process in processes:
            # logger.info('command = %s, %s, %s', process.scrapy_command, process.pid, process.ppid)
            if process.pid not in (pid, ppid) and 'monitor' == process.scrapy_command:
                return True
        return False

    @classmethod
    def is_singleton(cls, cmd=''):
        cur_proc = psutil.Process()
        for proc in psutil.process_iter():
            try:
                if cur_proc.pid == proc.pid:
                    continue
                if cur_proc.cmdline() == proc.cmdline():
                    return False
            except Exception as e:
                pass
        return True


def myexec(cmd, cwd=None, timeout=None, shell=None, wait=True, env=None, start_new_session=False,
           universal_newlines=None, bufsize=-1) -> Union[Popen, Tuple[AnyStr, AnyStr]]:
    if sys.platform == 'win32':
        args = cmd
    else:
        if shell:
            args = cmd
        else:
            args = shlex.split(cmd)
    cwd = cwd or os.getcwd()
    cwd = os.path.abspath(Path(cwd))

    if env is None:
        env = os.environ.copy()
    env['PYTHONPATH'] = cwd  # 不加这个，会出现找不到 module: video_scrapy 的错误
    # logger.info('----- shell: %s', env.get('COMSPEC'))

    # logger.debug(cmd)
    # logger.info(args + [cwd])
    # logger.info('env=%s', '\n\t'.join(list(map(lambda e: e[0] + '=' + e[1], sorted(env.items(), key=lambda t: t[0])))))

    p = Popen(args, stderr=PIPE, stdout=PIPE, cwd=cwd, env=env, shell=shell, start_new_session=start_new_session,
              universal_newlines=universal_newlines, bufsize=bufsize)
    if not wait:
        return p

    try:
        out, err = p.communicate(timeout=timeout)
    except TimeoutExpired:
        if sys.platform == 'win32':
            p.kill()
        else:
            # proc = psutil.Process(p.pid)
            # logger.debug('kill process: %s', p.pid)
            # for child in proc.children(recursive=True):
            #     logger.debug('\tfound child: %s, ppid=%s', child.pid, child.ppid())
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        return '', 'TimeoutExpired'
    if not universal_newlines:
        out = out.decode('utf8', errors='ignore')
        err = err.decode('utf8', errors='ignore')
    return out, err


def kill_current_process(kill_till='bash.exe'):
    if sys.platform == 'win32':
        # if kill_till:
        #     parents = ProcessList.get_parents()
        #     parents_till_bash = []
        #     found = False
        #     for p in parents:
        #         parents_till_bash.append(p)
        #         if p.name == kill_till:
        #             found = True
        #             break
        #
        #     if found:
        #         parents_till_bash.reverse()
        #         for p in parents_till_bash:
        #             logger.info('killing %s: %s', p.name, p.cmdline)
        #             os.system("taskkill /f /pid %s" % p.pid)
        #     os.system("taskkill /f /pid %s" % os.getpid())
        #
        # else:
        #     os.system("taskkill /f /pid %s" % os.getpid())
        # os.system("taskkill /f /pid %s" % os.getpid())
        cmd = "taskkill /f /pid %s" % os.getpid()
        # logger.info(cmd)
        out, err = myexec(cmd, shell=True, wait=True)
        # logger.info('%r, out=%s, err=%s', cmd, out, err)
    os.kill(os.getpid(), signal.SIGABRT)


def kill_sub_processes(pid):
    try:
        proc = psutil.Process(pid)
    except Exception as e:
        logger.warning('get process to kill failed: %s', e)
        return
    # logger.debug('kill process: %s', pid)
    pids = [pid]
    for child in proc.children(recursive=True):
        # logger.debug('\tfound child: %s, ppid=%s', child.pid, child.ppid)
        pids.append(child.pid)

    for pid in pids:
        try:
            if sys.platform == 'win32':
                myexec('taskkill /f /pid %s' % pid, shell=True, wait=True)
            else:
                # os.killpg(os.getpgid(pid), signal.SIGTERM)
                os.kill(pid, signal.SIGKILL)
        except Exception as e:
            logger.error('kill child failed: %s, pid=%s', e, pid)
