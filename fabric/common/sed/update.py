# coding=utf-8

from common.sed.config import *
from common.sed.append import *


def grep_data(c, key, data=None, file=None, **kwargs):
    c, file = local.init(c, file)

    """ 多行处理时，将\n转换为其他字符
    """
    def multi(data):
        head = ''
        if data and data.count('\n'):
            data = data.replace('\n', local.multi)
            head = "sed ':a; N; s/\\n/{}/g; ta;' |".format(local.multi)
        return data, head
    data, head = multi(data)

    # 传入的grep新选项，覆盖默认选项
    options = local.grep_option(**kwargs)
    options['head'] = head

    command = grep_param(key, data, options)
    result, command = grep(c, 'grep_data', command, file, options)

    output = result.stdout.strip('\n')
    print("[grep_data]: {command} {file}, line: [{output}]".format(command=command, file=local.file(file), output=output))
    return True if len(output) else False


def update(c, key, data, file=None,
           check=None, **kwargs):
    """ kwargs:
            grep: grep时相关参数
            sed:  sed时相关参数
    """
    c, file = local.init(c, file)
    check = local.check(check)

    # if check.get("pre") and \
    #    grep_data(c, key, **kwargs):
    #     print("update, item [{}] already exist".format(grep_param(key, data, **kwargs)))
    #     return 1

    options = local.sed_option(**kwargs)
    command = sed_param(key, data, options)
    result, command = sed(c, 'update', command, file, options)
    return result.ok


if __name__ == '__main__':
    enable = False

    def test_grep_data():
        initial("grep", """
UsePAM yes
# one logical cluster from joining another.
data_file_directories:
    - /mnt/disk1
    - /mnt/disk2
    - /mnt/disk3
""")
        if enable or True:
            output("key value not exist")
            check(grep_data(c, 'UsePAM', 'no'), False)

            output("key value exist")
            check(grep_data(c, 'UsePAM', 'yes'), True)

            output("key value exist, value multi line")
            check(grep_data(c, 'data_file_directories', '''
    - /mnt/disk1
    - /mnt/disk2
    - /mnt/disk3''', grep={'sep': ':'}), True)

            output("key value exist, print 1")
            check(grep_data(c, 'UsePAM', 'yes', grep={'show': 3}), True)

            output("key value exist, print 0")
            check(grep_data(c, 'UsePAM', 'yes', grep={'show': 0}), True)

    def test_update():
        initial("update", """
UsePAM yes

    # Ex: "<ip1>,<ip2>,<ip3>"LOCAL_JMX=yes
    - seeds: 192.168.10.1
    
# Setting listen_address to 0.0.0.0 is always wrong.
# ss
listen_address: 192.168.10.1

data_file_directories: 
    - /mnt/disk1
    - /mnt/disk2
    - /mnt/disk3
""")

        if enable or True:
            local.grep(**{'sep': ': '});

            output("data not exist")
            check(update(c, 'listen_address', '100000'))

            output("data not exist, need prefix to find only one")

            output("data not exist, key not the head")
            output("data not exist, key not the head")

            output("data not exist, key is multi line")

            output("data exist, ignore")

    # test_grep_data()
    test_update()