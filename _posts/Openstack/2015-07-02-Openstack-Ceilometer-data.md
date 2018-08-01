---
layout: post
title: Openstack Ceilometer 数据处理
date: 2015-07-02 14:05:08
description: ""
keywords: Openstack,Ceilometer,开源软件、公有云
categories: Openstack 
tags: [Openstack Ceilometer Data]
---

* content
{:toc}

  本文主要介绍Ceilometer数据处理，包括数据收集、数据存储。





#### 1. Ceilometer 数据处理

![data_1](/assets/images/201507/data1.png)

> 功能名称及描述

    Collect      Meters数据收集    Ceillometer-agent-central Ceilometer-agent-compute Ceilometer-agent-notification Ceilometer-collector
	Transform    Meters数据转换
	Publish      Meters数据发布
	Store        Meters数据保存
	Read         Meters数据访问    Ceilometer-api
	Alarm        告警              ceilometer-alarm-notifier ceilometer-alarm-evuator

> 总体架构如下：

![jiegou](/assets/images/201507/jiegou.png)

#### 2. Meters 数据的收集

Ceilometer 有两种数据收集方式：

  * Poller: 
      * Compute agent 运行在每个compute节点上，以轮询方式通过调用Image的driver来获取资源使用统计数据。
	  * Central agent 运行在management server，以轮询方式通过openstack各个组件（Nova、cinder、Neutron、Swift等）的API收集资源使用统计数据。
  * Notification: Collector运行在一个或多个management server的数据收集程序，它监控各组件消息队列。队列中notification消息会被它处理并转化为计量消息，再发回系统中，计费消息会被直接保存到存储系统中。


![poll](/assets/images/201507/poll.png)

(除了监控以上对象外，还可监控Neutron的Bandwidth，以及hardware。)

#### 3. Meters数据处理
  
  Meters数据通过Pipeline处理，Meters数据经过Transformer和Publisher处理，最后达到Receiver。Recivers包括Ceilometer Collector和外部系统。

  Pipeline


![pipeline](/assets/images/201507/3-Pipeline.png)

> Ceilometer 根据配置文件pipeline.yaml来配置meters所使用的transformers和publishers，配置文件中的时间以秒为单位。

#### 4. Transformer转换器

  Transformer 即Sample转换器。常见的有（unit_conversion:单位转换器; rate_of_change:计算方式转换器，根据一定的计算规则来转换。

  * accumulator:累计器如下：

![accumulator](/assets/images/201507/accumulator.png)

#### 5. Publisher分发器

![publisher](/assets/images/201507/publisher.png)

> Publishers支持

    Notifier  notifier://?option1=value1&option2=value2 	samples 数据被发到 AMQP 系统，然后被 Ceilometer collecter 接收。默认的 AMQP Queue 是 metering_topic=metering。这默认的方式。  	
	RPC       rpc://?option1=value1&option2=value2 	        与notifier类似，同样经过 AMQP， 不过是同步操作，因此可能有性能问题。
    UDP 	  udp://<host>:<port>/ 	                        经过 UDP port 发出。默认的 UDP 端口是 4952
	File 	  file://path?option1=value1&option2=value2 	发送到文件保存

`Notifier配置项[publisher_notifier] metering_driver = messagingv2 metering_topic = metering`

`RPC配置项[publisher_rpc] metering_topic = metering`

`UDP配置项udp_port=4952`

> 可以在pipeline.yaml中为某个meter配置多个publisher。

#### 6. 数据保存

Ceilometer Collector 从AMQP接收到数据后，直接通过一个或多个分发器（dispatchers)将它保存到指定位置）。支持的分发器：
  * 文件分发器：保存到文件 - 添加配置项dispatcher = file 和 [dispatcher_file] 部分的配置项
  * HTTP 分发器：保存到外部的 HTTP target - 添加配置项 dispatcher = http
  * 数据库分发器：保存到数据库 - 添加配置项 dispatcher = database

![storage](/assets/images/201507/storagemodel.png)

> 支持的数据库包括（MongoDB,MySQL,PostgreSQL,HBase,DB2)
> Ceilometer支持配置多个分发器，将数据保存到多个目地位置。如在ceilometer.conf中配置：

```
[DEFAULT]
dispatcher = database
dispatcher = file

[dispatcher_file]
backup_count = 5
file_path = /var/log/ceilometer/ceilometer-samples
max_bytes = 100000
```

> 通过配置后在/var/log/ceilometer/ceilometer-samples文件中将受到类似samples数据

#### 7. 数据访问

外部通过ceilometer-api模块提供的Ceilometer REST API来访问保存在数据库中的数据。API分为V1和V2两个版本。

![fangwen](/assets/images/201507/fangwen.png)

> API Server默认在8777端口

#### 8. 告警

8.1 架构

  （1）ceilometer-alarm-evaluator 使用 Ceilometer REST API 获取 statistics 数据

  （2）ceilometer-alarm-evaluator 生成 alarm 数据， 并通过 AMQP 发给 ceilometer-alarm-notifer

  （3）ceilometer-alarm-notifer 会通过指定方式把 alarm 发出去。

![alarm](/assets/images/201507/alarm.png)

8.2 Heat与Ceilometer通过Ceilometer alarm进行交互实现Instance auto-scaling

示意图：

![jiaohu](/assets/images/201507/jiaohu1.png)

过程：

![jiaohu](/assets/images/201507/jiaohu2.png)

#### 9. 总体架构

![zongti](/assets/images/201507/zongti1.png)

![zongti](/assets/images/201507/zongti2.png)


参考文档：

<http://docs.openstack.org/admin-guide-cloud/content/section_telemetry-measurements.html>
<http://docs.openstack.org/developer/ceilometer/install/dbreco.html>
<http://www.severalnines.com/blog/openstack-metering-how-install-ceilometer-mongodb>
<http://docs.openstack.org/developer/ceilometer/install/manual.html>
<https://www.rdoproject.org/HowToTest/Ceilometer/H/AlarmThresholdEvaluation>
<https://www.rdoproject.org/CeilometerQuickStart>
<http://docs.openstack.org/developer/ceilometer/architecture.html>

