#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
abspath = os.path.abspath(os.path.dirname(__file__))
os.chdir(abspath)
import logging
import logging.config
import ConfigParser
from Queue import Queue
from threading import Lock, Thread
import re
import time
from argparse import ArgumentParser

sys.path.append(os.path.join(abspath, "libs"))
import utils
from daemon import Daemon

# init logging facility
logging.config.fileConfig("conf/logging.cfg")


class Tasker(object):
    def __init__(self, *args, **kwargs):
        for n, v in kwargs.iteritems():
            setattr(self, n, v)


class Config(object):

    def __init__(self, config_file):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_file)
        return

    def get_configs(self):
        self.pid_file = self.config.get("main", "pid_file")
        self.wait_time = self.config.getint("main", "wait_time")
        self.scan_task_interval = self.config.getint("main",
                                                     "scan_task_interval")

        taskers = self.config.get("taskers", "keys")
        self.taskers = dict()
        for tasker in re.split(r"\s*,\s*", taskers):
            self.taskers[tasker] = self.get_tasker("tasker_%s" % tasker)
        return

    def get_tasker(self, tasker_name):
        tasker = Tasker(size=self.config.getint(tasker_name, "size"),
                        max_workers=self.config.getint(tasker_name,
                                                       "max_workers"))
        return tasker


class Handler(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        return

    def human_readable(self, size):
        self.logger.info("%d -> %s" % (size, utils.approximate_size(size)))


class Skeleton(object):
    def __init__(self, config_file):
        self.logger = logging.getLogger(self.__class__.__name__)
        config = Config(config_file)
        config.get_configs()
        self.config = config
        self.lock = Lock()
        self.queues = dict()

    def generate_task(self, tasker_name, tasker):
        while True:
            try:
                queue = self.queues.get(tasker_name)
                self.logger.info("old %s queue size: %d" % (tasker_name,
                                                            queue.qsize()))
                queue.put(tasker.size)
                self.logger.info("new %s queue size: %d" % (tasker_name,
                                                            queue.qsize()))
            except Exception as error:
                self.logger.exception("%s %s" % (tasker_name, error))
            finally:
                time.sleep(self.config.scan_task_interval)
        return

    def consume_task(self, n, tasker_name, tasker):
        while True:
            handler = Handler()
            queue = self.queues.get(tasker_name)
            if queue.empty():
                time.sleep(self.config.wait_time)
                continue
            try:
                while not queue.empty():
                    size = queue.get()
                    self.lock.acquire()
                    handler.human_readable(size)
                    self.lock.release()
            except Exception as error:
                self.logger.exception('Thread-%d: error %s' % (n, error))
            finally:
                del(handler)

    def do_work(self):
        for tasker_name, tasker in self.config.taskers.items():
            self.queues[tasker_name] = Queue()

            # Spwan generate_task thread
            t = Thread(target=self.generate_task, args=(tasker_name, tasker))
            t.setDaemon(True)
            t.start()

            # Spwan consume_task thread
            for n in range(tasker.max_workers):
                t = Thread(target=self.consume_task,
                           args=(n, tasker_name, tasker))
                t.setDaemon(True)
                t.start()

        while True:
            # Round robin and Sleep some seconds.
            time.sleep(self.config.scan_task_interval)
        return


class SkeletonDaemon(Daemon):
    def run(self, config_file):
        skeleton = Skeleton(config_file)
        skeleton.do_work()
        return


if __name__ == "__main__":
    logger = logging.getLogger("main")
    config_file = "conf/main.cfg"
    config = Config(config_file)
    PIDFILE = config.config.get("main", "pid_file")
    daemon = SkeletonDaemon(PIDFILE)

    prog = "daemon_skeleton"
    parser = ArgumentParser(prog=prog, description="Daemon Skeleton")
    parser.add_argument("action",
                        choices=("start",
                                 "stop",
                                 "restart",
                                 "status",
                                 "foreground"))
    args = parser.parse_args()
    if args.action == "start":
        logger.info("start")
        try:
            daemon.start(config_file)
        except Exception as error:
            logger.exception("%s cant be started" % prog)
    elif args.action == "stop":
        logger.info("stop")
        print("Stopping %s ..." % prog)
        daemon.stop()
    elif args.action == "restart":
        logger.info("restart")
        print("Restaring %s ..." % prog)
        daemon.restart()
    elif args.action == "status":
        logger.info("status")
        try:
            pf = file(PIDFILE, "r")
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            print("%s is running as pid %s" % (prog, pid))
        else:
            print("%s is not running." % prog)
    elif args.action == "foreground":
        logger.info("foreground")
        print("Staring %s in foreground" % prog)
        worker = Skeleton(config_file)
        worker.do_work()
