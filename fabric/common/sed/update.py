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

    local.grep_out = result.stdout.strip('\n')
    print("[grep_data]: {command} {file}, line: [{output}]"
          .format(command=command, file=local.file(file), output=local.grep_out))
    return True if len(local.grep_out) else False


def update(c, key, data, file=None, **kwargs):
    """ kwargs:
            grep: grep时相关参数
            sed:  sed时相关参数
    """
    c, file = local.init(c, file)
    display = data.count('\n')

    """ grep：
            半精确超找：key 和 value之间之只有 sep，即只查找自己插入的数据；
            这是默认行为，除非修改 local.grep_update
    """
    if grep_data(c, key, data, **kwargs):
        print("update, item [{}] already exist".format(grep_param(key, data, local.grep_option(**kwargs))))
        return False

    options = local.sed_option(**kwargs)
    (command, search, expect) = sed_param(key, data, options)
    result = sed(c, 'update', command, file, options)

    dump(c, key, search, display)

    count = len(local.result.split('\n'))
    if count > display + 1:
        print('[update], item [{}], ambiguous count [{}], result:\n{}'
              .format(expect, count, local.result))
        return False
    elif count == 0:
        print('[update], item [{}], success'
              .format(expect, count, local.result))
        return False
    elif not local.result:
        print('[update], search [{}] not find'
              .format(search, local.result))
        return False
    else:
        return True


if __name__ == '__main__':
    enable = True

    def test_grep_data():
        initial("grep", """
UsePAM yes
# one logical cluster from joining another.
data_file_directories:
    - /mnt/disk1
    - /mnt/disk2
    - /mnt/disk3
""")
        if enable:
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
    
# Setting listen_address:   0.0.0.0 is always wrong.
# log: true
server: daemon

rpc_address: 10.10.10.19
listen_address: 192.168.10.1

data_file_directories: 
    - /mnt/disk1
    - /mnt/disk2
    - /mnt/disk3
""")

        """ 修改默认选项
        """
        local.grep(**{'sep': ': '})

        enable = False
        if enable:
            output("find key")
            check(update(c, 'rpc_address', '192.168.0.1'), True)
            match('''rpc_address: 192.168.0.1''')

            output("key not exist")
            check(update(c, 'not_exist_key', '1.1.1.1'), False)

            output("key + data already exist, no need insert")
            check(update(c, 'rpc_address', '10.10.10.19'), False)

            output("multi key exist")
            check(update(c, 'listen_address', '1.1.1.1'), False)

            output("multi key, need locate to exactly only 1")
            check(update(c, 'listen_address', '100000', sed={'prefix': '^'}), True)

            ###############################################################
            output("key not from line start")
            check(update(c, '- seeds', '100000', sed={'prefix': ''}), True)
            match('''    - seeds: 100000''')

            output("data have multi line, already exist")
            check(update(c, 'data_file_directories', '''
    - /mnt/disk1
    - /mnt/disk2
    - /mnt/disk3'''), False)

            output("data have multi line, insert success")
            check(update(c, 'data_file_directories', '''
    - /mnt/diska
    - /mnt/diskb'''), True)
            match("""
data_file_directories: 
    - /mnt/diska
    - /mnt/diskb""")

            output("key data already exist multi line, insert, first delete some line, not support now")
            ##############################################################
            output("cancel comment")
            """ grep时，查找是否存在非#开头的：如果找到不需要替换了
                sed的search时：查找是否存在#开头的，找到后需要替换
            """
            check(update(c, 'log', 'true', grep={'prefix': '^[^#]*'},
                         sed={'prefix': '^.*'}), True)
            match("""log: true""")

            # output("cancel comment, already exist")
            # check(update(c, 'log', 'true', grep={'prefix': '^[^#]*'},
            #              sed={'prefix': '^.*'}), True)
            #
        output("add comment")
        check(update(c, '# server', 'daemon', grep={'prefix': '^'},
                     sed={'prefix': '^.*'}), True)
        match("""log: true""")

    # test_grep_data()
    test_update()