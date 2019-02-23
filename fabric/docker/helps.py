# coding=utf-8

from invoke import task
from common import *
import system
from docker import network as net

def sshd(c, name, host='127.0.0.1', sshd=False):
    if sshd:
        color('ssh clean cache [client side]:')
        print('''    rm ~/.ssh/known_hosts -f
or,
    echo "StrictHostKeyChecking=no" > ~/.ssh/config
    echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
''')
    else:
        print('''\nenter host:
        docker exec -it {name} /bin/bash
        ssh root@{host}'''.format(host=host, name=name))


def result(c, name, port=False, **kwargs):
    """ docker建立成功后，显示结果
            1. docker 内部，网卡名称是 eth1
    """
    if port:
        result = c.run('sudo netstat -antp | grep ":{port}[\t\ ]" --color'
                       .format(port=port), hide='out', echo=False).stdout.strip()
        string = '''show host port:
{result}'''.format(result=result)
        color_re(string, ':({port})[\t\ ]'.format(port=port))

        print('''\nbrower:
        docker exec -it {name} /bin/bash
        http://{local}:{port}'''.format(name=name, local=net.config.local, port=port))

    else:
        result = c.run('docker exec {name} ip addr show eth1 | grep inet | grep [0-9.].*/ --color'
                    .format(name=name), hide='out', echo=False).stdout.strip()

        string = '''show host address:
        {result}'''.format(result=result)

        if not color_re(string, '([0-9.].*)/'):
            color("show host address, but not find!")


def proxy(c, name):
    print('        docker exec -it {name} tail -f /var/log/apt-cacher-ng/*'.format(name=name))