---
layout: post
title: Openstack Ceilometer 命令学习
date: 2015-06-29 21:05:04
description: Openstack Ceilometer 学习记录
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack,Ceilometer,Cli]
---

* content
{:toc}

## Openstack Ceilometer Cli学习

  本文主要介绍Openstack Ceilometer 命令行学习及操作，学习分为Ceilometer采集查询，Ceilometer采集创建，Ceilometer采集删除等





#### Openstack Ceilometer CLi 查询

  查询包括`alarm-list（警告查询)、event-list（事件查询）、meter-list(采集查询，包括所有采集信息)、resource-list
  、semple-list(采集查询)、trait-list`

> 静态采集CPU数据

* 使用ceilometer sample-list -m cpu_util 直接查询

~~~
# ceilometer sample-list -m cpu_util
+--------------------------------------+----------+-------+-----------------+------+---------------------+
| Resource ID                          | Name     | Type  | Volume          | Unit | Timestamp           |
+--------------------------------------+----------+-------+-----------------+------+---------------------+
| 36290453-2b63-409a-b78f-20cf53275d8f | cpu_util | gauge | 7.29716193656   | %    | 2015-06-29T08:32:51 |
| 966345db-50e5-4e0c-884c-ab3d6d8d3686 | cpu_util | gauge | 7.33722871452   | %    | 2015-06-29T08:32:51 |
| d2898465-0678-4b2a-b6ef-0a4ebbce65e2 | cpu_util | gauge | 0.283333333333  | %    | 2015-06-29T08:32:51 |
| ee4935ea-9539-4031-9b95-3548fb92bd18 | cpu_util | gauge | 7.36894824708   | %    | 2015-06-29T08:32:50 |
| c1afd723-7da1-4765-a614-e364de9ac0d9 | cpu_util | gauge | 0.07            | %    | 2015-06-29T08:32:50 |
| cd1c4ba4-81c3-4fe5-b731-41df58be16f6 | cpu_util | gauge | 4.65358931553   | %    | 2015-06-29T08:32:49 |
| b4bce2ba-b287-474d-8277-ed9c72f1a943 | cpu_util | gauge | 8.65333333333   | %    | 2015-06-29T08:32:49 |
| 1bd307a3-17b4-4bf9-a804-58adba35940e | cpu_util | gauge | 8.66777963272   | %    | 2015-06-29T08:32:48 |
| 5fb34de9-bb44-4a49-8542-a8b3e2ad2c39 | cpu_util | gauge | 0.0333333333333 | %    | 2015-06-29T08:32:48 |
| 8f3abd93-8ba6-40e5-84d3-441a608b4212 | cpu_util | gauge | 4.67362270451   | %    | 2015-06-29T08:32:47 |
+--------------------------------------+----------+-------+-----------------+------+---------------------+
~~~

* 通过添加-l选项排序最大ID查询

~~~
# ceilometer sample-list -m cpu_util -l 5
+--------------------------------------+----------+-------+----------------+------+---------------------+
| Resource ID                          | Name     | Type  | Volume         | Unit | Timestamp           |
+--------------------------------------+----------+-------+----------------+------+---------------------+
| 36290453-2b63-409a-b78f-20cf53275d8f | cpu_util | gauge | 7.29716193656  | %    | 2015-06-29T08:32:51 |
| 966345db-50e5-4e0c-884c-ab3d6d8d3686 | cpu_util | gauge | 7.33722871452  | %    | 2015-06-29T08:32:51 |
| d2898465-0678-4b2a-b6ef-0a4ebbce65e2 | cpu_util | gauge | 0.283333333333 | %    | 2015-06-29T08:32:51 |
| ee4935ea-9539-4031-9b95-3548fb92bd18 | cpu_util | gauge | 7.36894824708  | %    | 2015-06-29T08:32:50 |
| c1afd723-7da1-4765-a614-e364de9ac0d9 | cpu_util | gauge | 0.07           | %    | 2015-06-29T08:32:50 |
+--------------------------------------+----------+-------+----------------+------+---------------------+
~~~

> 列出所有采集项使用`ceilometer meter-list`

~~~
#ceilometer meter-list
+----------------------------------------+------------+------------+-----------------------------------------------------------------------+------------------------------------------------+----------------------------------+
| Name                                   | Type       | Unit       | Resource ID                                                           | User ID                                        | Project ID                       |
+----------------------------------------+------------+------------+-----------------------------------------------------------------------+------------------------------------------------+----------------------------------+
| cpu                                    | cumulative | ns         | 003894a4-3c8e-4965-bf36-533375fc3407                                  | 66aa1213ea994344a110bf17ae999d96               | a9e4d648583a42c884d417f5b387fead |
| cpu                                    | cumulative | ns         | 0287dbfc-723d-42b8-a5e7-aa22807a6388                                  | 5e9bf02de68f49c187bf5893180c4b3e               | 55dcc8c59414499885ae37e3906e2562 |
| cpu                                    | cumulative | ns         | 030e1f3d-82fe-4b23-8c63-87fbbb565781                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 05e1f2cf-3fd2-430a-8170-675aa916f7be                                  | f827e1f13b3145d6b07d1cf3790b512d               | bf87349ae6704a87af75ebe9546d4af6 |
| cpu                                    | cumulative | ns         | 08a65f4b-4812-4a4e-a91d-1ac7a2816992                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 09434053-b51a-4f57-a973-5fd42bbd0571                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 0da3f008-60d7-4b10-a7eb-b143a842a25b                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 120f5583-878f-4f5d-b4f9-002022b4ead1                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 12c933e2-2ee9-4184-a8d0-fdea00fd9330                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 13ac82e2-3d66-4ab3-b0f4-cf606cab62e1                                  | 643e388a2ab04876a953f29b04a2a794               | bf87349ae6704a87af75ebe9546d4af6 |
| cpu                                    | cumulative | ns         | 14c84122-7d86-482b-9a41-c08d0aac4ba9                                  | b0b6f7142f8342da81977691029f30aa               | 48c459a8a8e8452c849c8e2eff3e1e80 |
| cpu                                    | cumulative | ns         | 179f3e26-129f-4160-ac84-59367c5e5452                                  | c5b98121f0bb4e80aec5d1e87dee79b5               | aceb89cb587b493e96042b2cbf84ac8f |
| cpu                                    | cumulative | ns         | 196a590d-f44f-4b83-a9d6-7e94193e49ff                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| cpu                                    | cumulative | ns         | 19cbf520-ad46-473a-8b2b-0aa623608d87                                  | 66aa1213ea994344a110bf17ae999d96               | a9e4d648583a42c884d417f5b387fead |
| cpu                                    | cumulative | ns         | 1bd307a3-17b4-4bf9-a804-58adba35940e                                  | 8b5aaedcae5d4a99aa75516c573483db               | 8b410fa00a634856a7e3b5bb5f20e08c |
| cpu                                    | cumulative | ns         | 1d0b3241-96de-4fe9-a118-065898b99f0a                                  | be0e831c54ea48e7969c22d676449374               | 722ab8ce061248d18e79d83e2a746249 |
| cpu                                    | cumulative | ns         | 1e6ce226-03aa-4fcb-a2c8-766be6c707a8                                  | 3dbf0919d60d4025842e6ea149e4aeba               | 3846bfe69b4a49948b8056d5f9c76859 |
| volume.size                            | gauge      | GB         | fae3cdfc-5cbb-4589-bfbb-d6b73693250b                                  | 32bcb1846dd94faf96cec6df500f1d94               | 04a8913a6b6f41a0b49cd3e8dfe71814 |
| volume.size                            | gauge      | GB         | fc7e408f-9c5e-4db9-b14c-35174fedb0f8                                  | f827e1f13b3145d6b07d1cf3790b512d               | bf87349ae6704a87af75ebe9546d4af6 |
| volume.size                            | gauge      | GB         | fd0b6c37-7ed0-471e-9324-6bdbe4e009d4                                  | f827e1f13b3145d6b07d1cf3790b512d               | bf87349ae6704a87af75ebe9546d4af6 |
| volume.size                            | gauge      | GB         | ff326414-8fb9-4dcf-8299-cc1e03c61534                                  | 66aa1213ea994344a110bf17ae999d96               | a9e4d648583a42c884d417f5b387fead |
+----------------------------------------+------------+------------+-----------------------------------------------------------------------+------------------------------------------------+----------------------------------+
~~~

* 警告采集`ceilometer alarm-list`

~~~
# ceilometer alarm-list
+--------------------------------------+----------+-------------------+---------+------------+---------------------------------+------------------+
| Alarm ID                             | Name     | State             | Enabled | Continuous | Alarm condition                 | Time constraints |
+--------------------------------------+----------+-------------------+---------+------------+---------------------------------+------------------+
| a020c017-b2a9-422e-b1bc-c414c98091d1 | cpu_high | insufficient data | True    | False      | cpu_util > 70.0 during 3 x 600s | None             |
+--------------------------------------+----------+-------------------+---------+------------+---------------------------------+------------------+
~~~

> 采集详细信息查询

  可通过ceilometer show ID参数查看查询详细信息，包括`alarm-show、event-show、sample-show`获取

* alarm 警告详细查询

~~~
# ceilometer alarm-show a020c017-b2a9-422e-b1bc-c414c98091d1
+---------------------------+--------------------------------------+
| Property                  | Value                                |
+---------------------------+--------------------------------------+
| alarm_actions             | [u'log://']                          |
| alarm_id                  | a020c017-b2a9-422e-b1bc-c414c98091d1 |
| comparison_operator       | gt                                   |
| description               | instance running hot                 |
| enabled                   | True                                 |
| evaluation_periods        | 3                                    |
| exclude_outliers          | False                                |
| insufficient_data_actions | []                                   |
| meter_name                | cpu_util                             |
| name                      | cpu_high                             |
| ok_actions                | []                                   |
| period                    | 600                                  |
| project_id                |                                      |
| query                     | resource_id == INSTANCE_ID           |
| repeat_actions            | False                                |
| state                     | insufficient data                    |
| statistic                 | avg                                  |
| threshold                 | 70.0                                 |
| type                      | threshold                            |
| user_id                   | 3dbf0919d60d4025842e6ea149e4aeba     |
+---------------------------+--------------------------------------+
~~~


#### 启用事件记录

  默认情况下，Ceilometer没有启用事件记录，如需要启用事件记录，需要修改`ceilometer.conf`配置文件

    #vim /etc/ceilometer/ceilometer.conf
    修改:store_events=false
    为： store_events=True

  修改完成后需要重启服务生效。

###### 事件查询

> 查询事件通过`ceilometer event-list`查询

  查询的事件列出了事件信息及类型，事件记录所有发生的事件，数据量较大。

> 查看事件类型`ceilometer event-type-list`

~~~
  # ceilometer event-type-list
  +-------------------------+
  | Event Type              |
  +-------------------------+
  | floatingip.update.end   |
  | floatingip.update.start |
  | identity.authenticate   |
  | member.create.end       |
  | member.create.start     |
  +-------------------------+
~~~

> List trait info for an event type.

~~~
  #  ceilometer trait-description-list -e member.create.end
  +------------+-----------+
  | Trait Name | Data Type |
  +------------+-----------+
  | request_id | string    |
  | service    | string    |
  | tenant_id  | string    |
  +------------+-----------+
~~~

> List trait list

~~~
[root@node-5 ~](controller)# ceilometer trait-list -e member.create.end -t request_id
+------------+------------------------------------------+-----------+
| Trait Name | Value                                    | Data Type |
+------------+------------------------------------------+-----------+
| request_id | req-08300fd1-be12-4f42-a15c-6185489bc5ad | string    |
| request_id | req-0bdcb6d3-6d25-4eb8-a0e1-9f306737154c | string    |
| request_id | req-0fd4d68c-d069-4baf-b67a-bdc1069337e9 | string    |
| request_id | req-121bc583-3b30-4976-8989-4ee2b9672d7b | string    |
| request_id | req-179966dc-f4ca-4bdd-8392-d53d4d3ca8e4 | string    |
| request_id | req-24703694-ef32-4718-8ccb-030b6ab8c3bb | string    |
| request_id | req-24a2837a-65c4-4d04-af7f-617e08210801 | string    |
| request_id | req-306651c6-cab4-465a-a5cb-28e18d54d1dd | string    |
| request_id | req-3371968f-e49b-4871-897f-5ec8a7d4105d | string    |
| request_id | req-33a76062-e4a9-4d9c-b53c-5c5597baaa4f | string    |
| request_id | req-379d57ec-e593-40d2-93d9-bcb73b067d77 | string    |

~~~
