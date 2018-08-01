---
layout: post
title: Linux file system 修复
date: 2016-12-07 12:05:06
description: ""
keywords: Markdown,Jekyll
categories: Linux
tags: [Linux 文件系统]
---

* content
{:toc}
   
    计算机的文件系统是一种存储和组织计算机数据的方法，它使得对其访问和查找变得容易，文件系统使用文件和树形目录的抽象逻辑概念代替了硬盘和光盘等物理设备使用数据块的概念，用户使用文件系统来保存数据不必关心数据实际保存在硬盘（或者光盘）的地址为多少的数据块上，只需要记住这个文件的所属目录和文件名。

          




#### 文件系统分类

根据操作系统不同，对应的操作系统使用不同的文件系统，常见的操作系统包括Windows,Linux两类，分类如下：

* Windows操作系统

    FAT FAT32 NTFS

* Linux 操作系统

    EXT3 EXT4 XFS


#### Linux EXT文件系统修复

* 文件系统错误判定

> 文件系统错误，常表现在系统不能启动，在启动过程中卡死
> 进入操作系统后，出现大量i/o错误日志
> 在目录下无法写入文件，读取文件出现错误

* 文件系统修复

文件系统修复分为修复根分区(/)操作系统无法启动，修复根分区以外的分区（操作系统能够进行）

1. 操作系统无法进入，文件系统修复

```
a) 通过一个已存在的基础系统启动，将需要修复的系统挂载为第二块磁盘

/usr/libexec/qemu-kvm -enable-kvm -m 4096 -smp 2 -hda base.qcow2 -hdb images/eayunstack-mongo1.qcow2 -vnc 0.0.0.0:20 -redir tcp:8022::22  (其中的-redir tcp:8022::22 可以不添加)

b) 通过vncviewer连接qemu-kvm启动的物理机ip所在的20端口

vncviewer 10.10.10.158 20

c) 连接vncviewer后进入基础系统(输入基础系统的用户名与密码)

d) 查看基础系统的挂载情况 cat /etc/fstab 

以下分为两种情况：系统使用了lvm，系统未使用lvm
以lvm举例

f) 执行vgs,lvs得到系统的lvm分区情况，通过lvdisplay能够获得lvm详细分区信息,根据cat /etc/fstab查看的信息，排除本地磁盘，获取第二块磁盘挂载的分区，分区查看的命令一般常用如下:

fdisk -l   查询系统磁盘情况
pvdisplay  查询pv信息
vgs, vgdisplay   查询vg情况
lvs, lvdisplay   查询lv信息情况

根据以上命令获取需要修复的磁盘分区

fsck /dev/os/root   (fsck为修复命令，os 为vg名字，root为lv的名字)
执行fsck后，会进行查询，查询到有需要修复的坏块，需要根据提示输入y进行修复(如果有多个坏块需要修复，会提示多次输入y进行修复)
也可以执行:
fsck -y /dev/os/root (检测后直接进行修复)

备注: 如果有多个分区存在问题，需要对多个分区都进行文件系统修复

```

#### Linux XFS 文件系统修复

与上面步骤一样，先判断需要修复的文件系统类型，然后找到文件系统，执行如下命令进行修复：

xfs_repair /dev/os/root   (root分区为xfs文件系统)




参考资料：

[Linux file system](http://www.tldp.org/LDP/sag/html/filesystems.html)

[FilesystemTroubleshooting](https://help.ubuntu.com/community/FilesystemTroubleshooting)

[Linux Ext file system repair](http://www.thegeekstuff.com/2012/08/fsck-command-examples/)

