---
layout: post
title: Openstack Ceilometer
date: 2015-06-29 10:15:02
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Ceilometer]
---

* content
{:toc}

#### Openstack Ceilometer 简介

> Openstack Ceilometer 为Openstack平台中一个子项目，把Openstack内部发生的几乎所有的事件都收集起来，然后为计费和监控以及其它服务提供数据支撑。

> Ceilometer 数据收集与监控对象： Ceilometer提供内部nova、neutron、cinder、swift、硬件IPMI等服务进行数据收集。





#### 1. Ceilometer 安装软件（基于3台control、3台compute、3台ceph、1台Mongo节点）

   Control 节点软件包：

    a) openstack-ceilometer-common-2014.2-1.el7.centos.noarch （提供ceilometer 数据与消费）

	b) openstack-ceilometer-collector-2014.2-1.el7.centos.noarch (核心组件，监听Message Bus，将收集到的数据写入数据库，同时对收集到的其它服务发来的notification消息本地处理，然后重新发送到Message Bus 中去，随后再被其收集）

	c) openstack-ceilometer-api-2014.2-1.el7.centos.noarch  （提供Ceilometer API服务）

	d) openstack-ceilometer-alarm-2014.2-1.el7.centos.noarch (提供Ceilometer警告通知与警告评估)

	e) openstack-ceilometer-notification-2014.2-1.el7.centos.noarch(提供Ceilometer通告代理，并将Openstack服务的各种数据推送到收集中心)

	f) openstack-ceilometer-central-2014.2-1.el7.centos.noarch (Central Agent代理，运行在控制节点上，它主要收集其它服务（Image,Volume,Network)信息)

   Compute 节点软件包

    a) openstack-ceilometer-common-2014.2-1.el7.centos.noarch （提供ceilometer 数据与消费）

	b) openstack-ceilometer-compute-2014.2-1.el7.centos.noarch （提供openstack compute代理与compute服务,每一个计算节点都运行一个Compute Agent，该Agent通过Stevedore管理pollster插件，获取虚拟机CPU,Disk IO,Network IO，Instance消息）


#### 2. Ceilometer 结构
 
>  核心结构图

![Ceilometer 结构](/assets/images/201506/ceilometer-architecture.png)


Ceilometer 使用两种收集数据的方式，一种是消费OpenStack各个服务内发出的notification消息（上图中蓝色箭头），一种是通过调用各个服务的API去主动获取数据（上图中黑色箭头）。

其中Ceilometer内部消费主要记录Openstack内部发生的事件对应notification消息，如创建和删除instance。另一种是Ceilometer数据来源，notification消息是无法获取的，如instance的CPU运行时间，使用率，通过API实现周期性信息调用。


#### 3. 其它名称解析及作用

    a) Storage数据存储
 
    b) REST API API是唯一一个能对数据库进行操作的组件，然后加入的Alarm API也能够进行数据库读写

    c) Message Bus数据流瓶颈，所有数据都要经过Message Bus 被Collector收集而存到数据库中，目前Message Bus采用RabbitMQ实现 

    d) Pipeline 它是Agent和Message Bus以及外界之间的桥梁，Agent将数据发到pipeline，经过一组transforme的处理，然后通过Multi Publisher发送出去，可以通过Message Bus 发送到Collector，或者发送到其它的地方。Pipeline是可配置，Agent poll数据的时间间隔，以及Transformers和Publishers都是童过pipeline.yaml文件进行配置。

    e) Metering(计量) 收集资源的使用数据，其数据信息包括：使用对象（what），使用者（who），使用时间（when）和用量（how much）。

	f) Rating（计费） 将资源使用数据按照商务规则转化为可计费项目并计算费用

	g) Billing（结算）收钱开票

	h) Sample 某Resource某时刻Meter的值

	j) Statistics 某区间Samples的聚合值

	k) Alarm 某区间Statistics满足给定条件后发出的警告


> 公有云在计费方面三个层次计量(Metering)、计费（Rating）、结算（Billing)


#### 4. 告警

4.1 类型

> Alarm包括threshold alarm（阀值告警）和combination（组合告警）两种类型。

  * Threshold alarm: 根据监控指标阀值判断alarm状态，针对某一个监控指标建立alarm。包括（一个静态阀值和比较方法、指定事件的meter statistic、比较的事件窗)

  * Combination alarm 根据多个alarm的状态来判断自己的状态，多个alarm之间是or/and的关系，相当于多个指标建立了一个alarm。

  例如：(Combination alarm)

  ```
  ceilometer alarm-combination-create --name meta --alarm_ids Alarm_ID1 --alarm_ids ALARM_ID2 --operator or --alarm-action 'http://example.com'
  ```
  例如：（threshold alarm)

  ```
  ceilometer alarm-threshold-create --name cpu_high --description 'instance running hot'  --meter-name cpu_util  --threshold 70.0 --comparison-operator gt  --statistic avg --period 600 --evaluation-periods 3 --alarm-action 'log://' --query resource_id=INSTANCE_ID
  ```

(name: 告警名称，meter-name: meter 名称、threshold： 阀值、comparison_operator：参数确定怎么与阀值比较（包括:lt,le,eq,ne,ge,gt,默认eq)、statostoc: 参数却使用什么数据去和threshold比较（包括:max,min,avg,sum,count,默认是avg)、period：确定获取该监控指标的监控数据与evaluation_periods配合用，同时确定两个点之间的时间间隔，默认60s、evaluation_periods：表示连续的监控间隔数码。和period参数相乘，默认1、alarm-action：告警产生后的反应、query：过滤监控指标下的某个资源)

4.2 Alarm 状态
  
  * Alarm（告警状态）

  {"current": "alarm", "alarm_id": "742873f0-97f0-4d99-87da-b5f7c7829b7f", "reason": "Remaining as alarm due to 1 samples outside threshold, most recent: 0.138333333333", "previous": "alarm"}

  * OK（数据充足，未告警）

  {"current": "ok", "alarm_id": "742873f0-97f0-4d99-87da-b5f7c7829b7f", "reason": "Remaining as ok due to 1 samples inside threshold, most recent: 0.138333333333", "previous": "ok"}

  * Insuffclient Data（默认状态，数据不足）

   {"current": "insufficient data", "alarm_id": "742873f0-97f0-4d99-87da-b5f7c7829b7f", "reason": "1 datapoints are unknown", "previous": "ok"}

4.3 Alarm Action

  使用Ceilometer alarm-threshold/combination-create 的如下属性来为不同状态下的Alarm定义不同的Action：

  (--ok-action、--alarm-action、--insufficlent-data-action)

  Ceilometer支持两种action

  * "log": alarm被写入Log文件
  * "Webhook URL" HTTP(s) endpoint的URL，如：http://192.168.1.100:8080/alarm/instance__  Alarm的内容会以JSOn的格式被POST到该URL中。
