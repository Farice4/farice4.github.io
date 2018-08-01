---
layout: post
title: Senlin introduction
date: 2016-12-13 14:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Senlin introduction]
---

* content
{:toc}

#### Senlin 基本介绍

Senlin 是Openstack 下的一个组件服务， Senlin的架构完全是为HA和AutoScaling设计的， 支持的插件包括Nova, Heat, Neutron, Loadbance, Ceilometer, Container






##### Senlin 架构

![Senlin 结构](/assets/images/201612/senlin_jiagou.png)

主要架构包括如下：

* senlinclient 

senlin 客户端与Openstack其它组件一样提供命令行的客户端支持, 与senlin server交互

* senlin api

senlin api 提供senlin reset api服务，对外提供senlin server的所有api接口

* senlin-engine

senlin 核心服务， 用于操作senlin的集群、节点、profile文件、webhook、策略等


#### Senlin 功能

##### Senlin 名词解析


* Profile

profile 是Senlin里面的模板文件， 与Heat模板文件一样， 支持nova, heat, 容器

![Senlin profile](/assets/images/201612/senlin_profile.png)

* cluster

Senlin 集群概念， 提供对象管理，这些对象的集合称为集群

* Node

Senlin 抽象的物理节点， 节点可以单独存在，也可以将节点加入到集群， 创建节点后， nova会创建相应的instance

* Policies

Senlin 中的策略， 针对一个集群可以配置不同的策略，这些策略可以来管理集群中的资源

![Senlin policy](/assets/images/201612/senlin_policy.png)

* Receiver

Senlin 中的接收器，对外提供一个url地址， 执行Post url地址能够改变集群中的节点数

##### Senlin 功能

* Senlin AutoScaling

 Heat 的设计是基于 AWS 的，不够通用，目前我们认为 Heat 的作用更多的在于基于模版的资源管理，它的重点不在于AutoScaling、HA，而是作为一个引擎来帮其他服务或者开发者做资源管理的工作。

Selin 项目本身就是针对集群与AutoScaling设计的

> Senlin 与 Heat AutoScaling区别

|名称| 支持类型|
|-|-|
|Heat|支持通过Ceilometer Alarm的方式触发webhook提供autoscaling自动伸缩， 支持创建Loadbance负载均衡|
|Senlin|支持Receiver对外提供url， 上层可根据需要如：根据时间、根据特定情况、根据alarm警告触发url，实现autoscaling自动伸缩, 支持创建Loadbance负载均衡|

> Senlin AutoScaling 架构
![Senlin policy](/assets/images/201612/senlin_autoscaling.png)

    1. Senlin 通过profile构建集群
    2. 为集群添加策略(策略中定义添加/删除 节点数)
    3. 创建Receiver提供webhook地址url
    4. 根据需要触发webhook url实现策略定义(触发webhook url的包括ceilometer alarm、上层时间计划、特定需要)

* Senlin 集群节点扩展与删除

Senlin 中提供了对集群中的节点扩展与删除操作，添加与删除的节点满足集群中的最大与最小值, 支持在集群中创建节点，同样支持将Senlin 创建的节点添加到集群中


* Senlin 集群定义节点数

Senlin 在创建集群时支持指定创建集群中的节点数，当最小为0时，支持创建一个空集群，后期根据需要为集群中添加节点

* Senlin 集群策略支持

Senlin集群支持自定义策略，策略类型包括删除(可根据需要删除集群中的指定节点)、Scaling策略(提供自动伸缩策略)、Loadbance策略(支持集群提供负载均衡)、健康检测策略(根据健康检测结果，替换掉集群中出现故障的节点)

* Selin 跨区域支持

Senlin 支持节点跨区域管理(nova zone的概念)

* Senlin 支持事件记录

Senlin 根据集群中触发的事件，记录事件的时间与触发的条件

* Senlin 支持集群Resize操作

Senlin Resize允许修改集群中的最大、最小、期望、添加节点数



#### Senlin部署条件

    1) Senlin 发布第一个版本为mitaka版本， 安装时需要的认证必须为keystone v3版本

    2) Senlin 的loadbance策略支持的loadbance必须为单独服务，必须配置单独的endpoint

    3) Senlin 不提供alarm警告创建， 上层使用时根据需要创建alarm，创建的alarm绑定cluster id，webhook执行动作为senlin 中的receiver 提供的alarm_url链接

    4) Senlin 要实现根据时间，根据特定计划触发receiver中的alarm_url链接需要上层配置计划，配置触发alarm_url链接

    5) Senlin 在使用中需要openstacksdk支持, openstacksdk实现了各个组件组件的调用
