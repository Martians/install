#!/bin/bash
###########################################
# 总体
1. 每个使用场景下(物理机)，定义一个 config.sh文件，~/.docker_config（Example：config/example）
    1. 定义本地IP、网络状况：后续显示帮助、在本机网卡上新建网络
    2. 分配的IP：新建的容器，将被分配的IP信息，预制了 enum 类型的几种常用Host
    3. 目录位置，Http、Proxy的Host宿主机上配置
2. Volume基本都没怎么配置

# Image
## 是否使用BaseImage
1. 使用之后可以加快后续构建过程，提前进行了yum update，并预装了一些软件；
2. 缺点是造成系统占用的空间稍微变大，但可以忽略不计
    1. config/handle.sh：如果使用base，会根据需要创建出来
    2. build/initialize.sh：如果使用了全局配置，这里可以减少一些操作（目前没做）

## 使用的仓库
1. REPO_MASK：定义在本机配置中，只有在这里定义的模式，才能生效
    1. 最终repo不会超出这里的范围
    2. 这里相当于一个全局的配置点
2. REPO：定义在每个服务启动脚本中，表明该服务期望用什么样的仓库

## Systemd

#################################################################################################
##时 目录结构
1. 0_config/
    ├── config.sh
    ├── default.sh
    ├── depend.sh
    ├── example
    │   ├── config_desktop.sh
    │   └── config_notebook.sh
    ├── macro.sh
    ├── usage.md
    └── utility.sh
    1. config.sh 是一个调度文件，将多个配置整合在一起
    2. utility.sh 提供了一些公共函数，其他项目也可以用

2. server/ 
    ├── base
    │   ├── dns.sh
    │   ├── host.sh
    │   ├── http.sh
    │   ├── ntp.sh
    │   ├── proxy.sh
    │   ├── sshd.sh
    │   └── systemd.sh
    ├── command
    │   ├── clean.sh
    │   ├── create.sh
    │   ├── dangling.sh
    │   ├── prepare.sh
    │   └── README.md
    ├── database
    │   ├── hive.sh
    │   ├── mariadb.sh
    │   └── postgres.sh
    ├── generate.sh
    ├── more.sh
    └── test.sh

    1. 保存用户交互的脚本，每个脚本会根据需要创建出 Image、Docker
    2. 常用的选项是 sh server/base/httpsh 0/1：0代表重建虚拟机；1代表重建Image
    3. 级联启动，如果服务中配置了 REPO，

3. build/
    ├── advance.sh
    ├── clean.sh
    ├── common.sh
    ├── hadoop
    │   ├── generate.sh
    │   ├── hive_hadoop_client.sh
    │   ├── hive.sh
    │   ├── mariadb.sh
    │   └── postgres.sh
    ├── handle.sh
    ├── initialize.sh
    ├── repo.sh
    ├── server
    │   ├── config.sh
    │   ├── dns.sh
    │   ├── http.sh
    │   ├── ntp_client.sh
    │   ├── ntp.sh
    │   ├── proxy.sh
    │   ├── sshd.sh
    │   ├── start_dns.sh
    │   ├── start_http.sh
    │   ├── start_ntp.sh
    │   ├── start_proxy.sh
    │   ├── start_sshd.sh
    │   ├── start_systemd.sh
    │   └── systemd.sh
    └── system.sh
    1. 最外层的文件，是全局执行用到的一些机器配置设置
    2. 内层每个目录下，包含了Image的服务配置脚本、服务启动脚本

## 调用堆栈
    ```server/base/http.sh1
    1. 设置配置
        1. 配置Server特有的宏，NAME、PORT等
        2. 调用初始化脚本，读取各种配置
    
    2. 启动依赖：
        1. 根据repo的设置，repo + repo_mask，启动Http、Proxy
        2. 进行网络初始化设置
    
    3. 创建Image，create_image
        1. Server对应的Image，将预设的参数设置进去
        1. 如果BaseImage没有创建 ，就先创建出来
    
    4. 创建Docker，create_docker
        1. Server对应的Docker
    
    5. 分配Network
        1. Server对应的Network
    
    6. 显示Server情况
        1. Server当前网络、占用端口
        1. Server的用法
    ```

## 代码问题
    1. 使用了create_image，所有的参数都不能为空，否则会解析错误
        2. 考虑使用一个wrapper，即使没有提供的参数，设置为0，进行 exist 判断后传入
    2. 每个Server的显示部分，看是否能够整合在一起
    3. 