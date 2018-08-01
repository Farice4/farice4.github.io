---
layout: post
title: "Mongo的基本使用"
date: 2015-07-13 12:00:05
description: ""
category: "DataBase"
tags: [Mongo的基本使用]

* content
{:toc}

---

   Mongo数据库介于关系与非关系数据库之间，无内存设置参数，Mongo使用os mmap 机制来缓存数据文件数据,自身目前不提供缓存机制。





#### Mongo的主要参数：
    * dbpath: 数据文件存放路劲，每个数据库会在其中创建一个子目录，用于防止同一个实例多次运行的mongod.lock也保存在次目录中。
	* logpath： 错误日志文件
	* logappend： 错误日志采用追加模式（默认是覆写模式）
	* bind_ip： 对外服务的绑定IP，一般设置为空
	* port： 对外服务端口。Web管理端口在这个port的基础上+1000
	* fork： 以后台Daemon形式运行服务
	* journal： 开启日志功能，在1.8版本后正式加入
	* syncdelay：系统同步刷新新磁盘的时间，单位为秒，默认60秒
	* maxConns：最大连接数
	* repairpath：执行repair是的临时目录。如果没有开启journal，异常down机后重启，必须执行repair操作
> mongod支持将参数写入到配置文件中，然后通过config参数引用此配置文件：（./mongod --config /etc/mongo.conf)

#### Mongo启动/停止

> 启动

```
./mongod --dbpath=/data/db --logpath=/data/log/r3.log --fork

```

> 停止

```
a)通过进程终止结束mongo运行
b)通过登录数据库执行命令终止运行
举例：
mongo  (登录数据库，默认test库)
use admin (切换到admin)
db.shutdownServer() （关闭数据库）
```

#### Mongo查询
条件查询： $lt,$lte,$gt,$gte

> 举例(范围查询，通过定义时间，匹配文件的查询结果)

```
start = new Date("01/01/2007")
db.users.find({registered} : {"$lt" : start}})

```

> 同时支持$or,$in，$not,$all,$size,$silice,$where

> limit(限制返回结果),举例：

```
db.c.find().limit(3)
```

> sort(排序,升序1,降序-1),举例：

```
db.c.find().sort({username : 1, age : -1}) (查询username升序查询，查询age降序查询)

db.stock.find({"desc" : "mp3"}.limit(50).sort({"price" : -1})) (通过限制与排序查询，经常在使用中用到)

```
#### 聚合

通过count快速查询集合中文档的数量：

```
> db.meter.count()
685752
> 
```

通过distinct找出给定键的所有不同的值。使用时必须指定集合和键。

group 做的聚合稍微复杂一些。先选定分组所依据的键，而后MongoDB就会将集合依据键值的不同分成若干组。然后可以通过聚合每一组内的文档，产生一个结果文档。（与SQL中的group by差不多）

通过完成器(finalizer)用以精简从数据库传到用户的数据。

> 查看mongo数据库状态

```
db.runCommand({"serverStatus" : 1})
```

> 通过mongostat 监控数据库

```
[root@mongo ~]# mongostat 
insert query update delete getmore command flushes mapped  vsize   res faults qr|qw ar|aw netIn netOut conn     time
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:25
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:26
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:27
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:28
    *0    *0     *0     *0       0     2|0       0 240.0M 804.0M 83.0M      0   0|0   0|0  133b    10k    4 22:41:29
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:30
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:31
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:32
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:33
    *0    *0     *0     *0       0     2|0       0 240.0M 804.0M 83.0M      0   0|0   0|0  133b    10k    4 22:41:34
insert query update delete getmore command flushes mapped  vsize   res faults qr|qw ar|aw netIn netOut conn     time
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:35
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:36
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:37
    *0    *0     *0     *0       0     1|0       0 240.0M 804.0M 83.0M      0   0|0   0|0   79b    10k    4 22:41:38
    *0    *0     *0     *0       0     2|0       0 240.0M 804.0M 83.0M      0   0|0   0|0  133b    10k    4 22:41:39

```

> Mongo 数据库备份

备份数据库通过`mongodump`备份

> Mongo 数据库恢复

恢复数据库通过`mongorestore`恢复

备份与恢复举例如下：

```
mongodump -d test -o backup (备份数据库test，备份到backup)
mongorestore -d foo --drop backup/test  (恢复数据库到foo,--drop恢复前检查，如果存在，就先删除，在进行恢复)
```

fsync 和锁
fsync命令强制服务器所有缓冲区写入磁盘。还可以选择上锁阻止对数据库的进一步写入，知道释放为止。

举例：

```
use admin
db.runCommand({"fsync" :1,"lock" : 1}); (锁定)


db.$cmd.sys.unlock.findOne();  (解锁)
db.currentOp   (确认已经解锁)
```
