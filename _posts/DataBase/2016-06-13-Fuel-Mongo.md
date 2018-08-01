---
layout: post
title: "Fuel新增Mongo角色"
date: 2016-06-13 10:15:03
description: ""
category: "DataBase"
tags: [Fuel新增Mongo角色]
---

* content
{:toc}

# Fuel Mongo节点升级
Fuel mongo节点升级分为两个步骤: 

* Fuel新增mongo节点角色
* Mongo复制集环境调整






## Fuel 新增Mongo节点角色

环境准备

1. 服务器上架

2. 服务器网络连接与交换机vlan配置正常（Mongodb主要使用PXE与管理网络)

Fuel 增加Mongo节点角色

1. 登录IDRAC，配置服务器RAID阵列信息

2. 启动服务器，服务器通过PXE启动，启动完成后，登录fuel ui,在fuel界面能够看到新发现的节点信息

3. 登录fuel 终端Shell环境执行如下命令，将新发现的节点添加mongo 角色

```
fuel env 　　查看fuel 的环境id
fuel node    查看节点信息，可以看到新增的两台服务器没有添加角色roles
fuel --env-id=1 node set --node-id=11 --role=mongo (其中--env-id=1为fuel env查询到的id, --node-id=11为fuel node查询时获取到的没有添加角色的id信息，执行此命令后，为该id将添加mongo角色)

```

4. 返回到fuel ui界面可以看到Telemetry-MongoDB中已经添加了一台mongo角色

5. 返回到fuel 终端Shell环境，执行3)步骤添加剩余一台服务器到mongo角色

6. 返回fuel ui界面查看Telemetry-MongoDB变成了３台mongo角色，其中两台为等待增加状态

7. 配置等待增加两台服务器的网络配置进入到节点页面，为服务器配置网络，并进行双网卡绑定，配置完成后，返回节点列表

8. 可根据需要对两台服务器进行磁盘配置，配置分区大小(这里保持默认),配置完成后，返回节点列表

9. 开始部署mongo节点，点击部署变更，此时可看到新增的mongo节点处于安装centos阶段，centos安装完成后会自动进行openstack安装阶段,在安装openstack阶段，可以通过shell登录安装openstack节点，查看puppet.log,`tailf /var/log/puppet.log`


> 备注：Mongo节点安装完成后，可进行mongo相关的检测，如查看mongo服务状态，能否正常登录mongo节点等
　　

## Mongo复制集环境调整

删除新增两台mongo节点集群配置

>通过Shell终端登录到新增的Mongo节点，通过执行命令删除mongo集群配置

- 登录两个节点中的主节点，删除从节点，并且删除集群配置信息

```
mongo -uadmin -pxxxx x.x.x.x:27017/admin  （使用admin账户登录到admin数据库，被登录的数据库必须为PRIMARY）
Last login: Thu Jun  2 11:10:23 2016 from 172.16.101.4
[root@node-22 ~](mongo)# mongo -uadmin 172.16.101.11:27017/admin -pxxxx
MongoDB shell version: 2.6.5
connecting to: 172.16.101.11:27017/admin
ceilometer:PRIMARY> 
ceilometer:PRIMARY> rs.status();   (查看现有集群配置)
{
	"set" : "ceilometer",
	"date" : ISODate("2016-06-02T06:08:42Z"),
	"myState" : 1,
	"members" : [
		{
			"_id" : 0,
			"name" : "172.16.101.8:27017",
			"health" : 1,
			"state" : 2,
			"stateStr" : "SECONDARY",
			"uptime" : 10534,
			"optime" : Timestamp(1464847703, 271),
			"optimeDate" : ISODate("2016-06-02T06:08:23Z"),
			"lastHeartbeat" : ISODate("2016-06-02T06:08:42Z"),
			"lastHeartbeatRecv" : ISODate("2016-06-02T06:08:42Z"),
			"pingMs" : 0,
			"syncingTo" : "172.16.101.11:27017"
		},
		{
			"_id" : 1,
			"name" : "172.16.101.11:27017",
			"health" : 1,
			"state" : 1,
			"stateStr" : "PRIMARY",
			"uptime" : 150458,
			"optime" : Timestamp(1464847703, 271),
			"optimeDate" : ISODate("2016-06-02T06:08:23Z"),
			"electionTime" : Timestamp(1464837188, 1),
			"electionDate" : ISODate("2016-06-02T03:13:08Z"),
			"self" : true
		}
	],
	"ok" : 1
}
ceilometer:PRIMARY> rs.remove("172.16.8.8:27017") (删除集群SECOND节点）
2016-06-02T15:05:42.439+0800 DBClientCursor::init call() failed
2016-06-02T15:05:42.441+0800 Error: error doing query: failed at src/mongo/shell/query.js:81
2016-06-02T15:05:42.442+0800 trying reconnect to 172.16.8.13:27017 (172.16.8.13) failed
2016-06-02T15:05:42.443+0800 reconnect 172.16.8.13:27017 (172.16.8.13) ok


ceilometer:PRIMARY> show dbs; (查询数据库)
admin        0.078GB
ceilometer   0.953GB
local       22.067GB
ceilometer:PRIMARY> use local;　（切换到local数据库）
switched to db local

ceilometer:PRIMARY> db.dropDatabase();　（删除local数据库，删除集群信息）

ceilometer:PRIMARY>quit() 

```

第二台新增mongo节点（从集群中删除的节点）删除local数据库中的集群配置信息

```
编辑/etc/mongodb.conf　注释掉以下两行
#replSet = ceilometer
#keyFile = /etc/mongodb.key

重启mongod服务
systemctl restart mongod
systemctl status mongod　（查看mongod服务已启动）

登录mongo数据库
mongo -uadmin 172.16.101.11:27017/admin -pxxxx

切换至local并删除数据库，删除数据库中集群信息
> use local;
> db.dropDatabase()
> quit()

编辑/etc/mongodb.conf将注释掉的两行，取消注释
replSet = ceilometer
keyFile = /etc/mongodb.key
```

配置原有mongo节点成为集群中的主数据库

```
拷贝新增节点下的mongodb.key至原有mongo节点/etc/目录下
scp x.x.x.x:/etc/mongodb.key /etc/

修改mongodb.key权限及属主,必须拥有如下权限及属主
[root@node-9 ~](mongo)# ls -l /etc/mongodb.key 
-rw------- 1 mongodb root 1004 6月   1 11:24 /etc/mongodb.key

停止mongod服务使用systemctl stop mongod

修改/etc/mongodb.conf文件，增加如下两行配置
replSet = ceilometer
keyFile = /etc/mongodb.key

启动mongodb数据库服务，如果启动中存在问题，需查看/var/log/mongod.log文件，进行错误排除

登录数据库，进行初始化
mongo -uadmin 172.16.101.11:27017/admin -pxxxx
＞　rs.initiate();  （初始化数据库，完成该步骤，节点会成为集群中的主节点）
ceilometer:PRIMARY>use ceilometer;
ceilometer:PRIMARY>db.meter.count();　（查询ceilometer数据库中的数据总数，确认数据没有丢失）
ceilometer:PRIMARY>quit()
```

重启其它两个mongod服务，此时两台服务器的数据库处于单节点模式下，未进行任何初始化与集群添加，登录后数据库中以">"标识，集群中的登录后会以
"ceilometer:PRIMARY>"标识

主节点上添加Mongo服务

```
mongo -uadmin 172.16.101.11:27017/admin -pxxxx
ceilometer:PRIMARY> rs.add("172.16.101.12:27017");
{ "down" : [ "172.16.8.12:27017" ], "ok" : 1 }
ceilometer:PRIMARY> rs.add("172.16.8.13:27017");
{ "down" : [ "172.16.8.12:27017" ], "ok" : 1 }
ceilometer:PRIMARY>rs.status(); （查看集群状态，能够看到集群中存在三个节点，且另外两个节点会从主节点进行数据同步，等待一段时间后，数据同步完成）

```

配置mongo集群节点优先级

```
cfg =rs.conf() 　（获取配置信息）
cfg.members[0].priority = 3 (配置每个成员优先级，这里将原mongo节点ip所在的id设置成为３，成为集群中优先级最高的）
rs.reconfig(cfg) （应用配置生效）
```

重启controller节点上ceilometer服务
`systemctl restart openstack-ceilometer-collector openstack-ceilometer-api`

查看/var/log/ceilometer/api.log　与/var/log/ceilometer/collector.log 日志，看是否存在错误


ceilometer查询与数据存储检测

```
ceilometer sample-list -m cpu_util -l 10 （查询数据能够提供查询）
ceilometer sample-list -m bandwidth -l 10 (查询数据，并进行数据时间对比，查看数据是否在1分钟前进行了数据收集与存储）
登录数据库查看数据量总数，是否增长
```
备注：在mongo复制集调整过程中，一定要注意使用已存在的mongo节点作为主节点，否则mongo同步将会丢失数据.
