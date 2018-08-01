---
layout: post
title: Nova resize
date: 2016-10-27 16:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Nova resize]
---

* content
{:toc}

#### 介绍

Risze的作用是调整instance 的vCPU，内存和磁盘资源，Instance需要多少资源都是通过flavor来定义，resize会选择新的flavor替换原flavor。从本质上讲Resize是在Migrate的同时应用新的flavor




#### 工作过程

* 向nova-api发送Resize请求
* nova-api发送消息
* nova-scheduler 执行调度
* nova-scheduler 发送消息
* nova-compute 执行操作

Resize 分两种情况：

* nova-scheduler选择的目标节点与源节点是不同节点,会执行Migrate相关操作
* nova-scheduler选择的目标节点与源节点是相同节点,则不需要执行Migrate操作

#### 代码调用过程

![nova resize](/assets/images/201611/nova_resize.jpeg)
