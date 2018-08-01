---
layout: post
title: Nova resize
date: 2017-09-27 12:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack senlin docker image]
---

* content
{:toc}

### 介绍

   主要介绍senlin 组件通过docker容器化部署的，镜像制作．






### Openstack-senlin deploy

#### 1. 基于docker.io/centos启动容器

> 使用docker.io/centos启动容器

```

docker run -it docker.io/centos

```

>在启动的容器中执行以下安装

```

a) yum install python-pip gcc python-devel MySQL-python git -y

　在执行前需要添加epel源，python-pip没有在centos源里面

b) 拷贝已经download的本地依赖pip 包, senlin python-openstacksdk的requirements.txt到容器，执行依赖安装(

pip install --no-index --find-links=[file://]<DIR> -r requirements.txt

c)手动安装MySQLdb模块

```

#### ２. 在启动的容器中添加senlin信息

```

a) 创建senlin 用户( useradd  -d /var/lib/senlin -s /sbin/nologin senlin)

b) groupmod -g 970 senlin

c) usermod -u 970 senlin

d) chown -R senlin.senlin /var/lib/senlin

e) mkdir /etc/senlin

    mkdir /var/log/senlin

e) chgrp senlin /etc/senlin

f) chown senlin /var/log/senlin

g)  yum clean all

h） rm -rf /var/cache/yum/*

j) 删除拷贝过来的pip依赖包以及依赖文件

k)清理yum仓库信息

mkdir /etc/yum.repos.d/repo

mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/repo

```

### 3．构建senlin/base镜像

```

1) 退出容器

2) docker commit 容器名称(执行依赖包安装的容器) senlin/base

```

### 4．安装senlin源码

```

1) 基于senlin/base启动容器

2) git clone -b Development https://github.com/eayunstack/python-senlinclient

    git clone -b Development https://github.com/eayunstack/python-openstacksdk

    git clone -b Development https://github.com/eayunstack/senlin

3) 分别在senlin python-openstacksdk目录中执行python setup.py install

```

### 5．创建新版本容器镜像

```

1) 退出容器

2) docker commit 容器名称(执行senlin源码安装容器)　eayunstack_senlin_base_1705

```

### 6．容器封装服务

> 构建Dockerfile文件

```

FROM eayunstack_senlin_base_170705

COPY ./service.sh /usr/bin/

USER senlin

CMD ["sh", "/usr/bin/service.sh"]

```

> 构建容器启动时执行的服务启动文件service.sh，并且添加执行权限

```

#!/bin/bash

# pass arguments to Shell Script through docker run



if [ "$DAEMON" = "senlin-api" ];then

    senlin-api --config-file /etc/senlin/senlin.conf

elif [ "$DAEMON" = "senlin-engine" ];then

    senlin-engine --config-file /etc/senlin/senlin.conf

elif [ "$DAEMON" = "senlin-manage" ];then

    senlin-manage db_sync

fi

```

> 执行容器build封装，使用构建的Dockerfile 与service.sh

```

docker build -t eayunstack/senlin-base .

```

#### ７. 导出镜像

```

 docker save --output eayunstack_senlin_base.latest.170705 eayunstack/senlin-base

```

#### 8．fuel节点执行ansilble安装

```

 ansible-playbook -vvv site.yml 2>&1 |tee fabian.log

```




