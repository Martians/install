# coding=utf-8

from common.init import *
import common.hosts as hosts


def kill(name, str=False):
    command = "ps aux | grep redis | grep -v grep |awk '{{print $2}}'| xargs kill -9".format(name)
    if str:
        return command
    else:
        return hosts.execute(command, err=False)
