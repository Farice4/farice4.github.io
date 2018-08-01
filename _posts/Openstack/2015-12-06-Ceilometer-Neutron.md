---
layout: post
title: Ceilometer Neutron-Metering
date: 2015-12-06 17:02:09
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Ceilometer Meter]
---

* content
{:toc}


### Ceilometer 监控网络流量

#### Ceilometer 网络流量采集两种方式

* Ceilometer 网络流量监控默认是通过Compute 的libvirt进行监控，记录网卡进入与出去流量统计，针对某个虚拟机的网卡，该方式记录所有网卡通过的流量统计。

* 网络bandwidth的采集是通过neutron-metering-agent 代理方式进行流量采集，然后push到oslo-messaging, ceilometer-agent-notification 通过监听消息队列来收取bandwidth信息。 

* 同一子网下虚拟机互相访问不会统计，但不同子网间进过虚拟路由器的流量会被统计，虚拟机与外部网络互访也会统计（有floatingip) 






#### Bandwidth 采集配置

* 安装neutron-metering-agent

```
# yum install openstack-neutron-metering-agent
```
* 修改配置文件/etc/neutron/neutron.conf
  
```
service_plugins =neutron.services.l3_router.l3_router_plugin.L3RouterPlugin,neutron.services.metering.metering_plugin.MeteringPlugin
notification_driver=neutron.openstack.common.notifier.rpc_notifier  (消息发布）
```

* 修改neutron-metering-agent.ini文件
  
```
[DEFAULT]
# Show debugging output in log (sets DEBUG log level output)
debug = True

# Default driver:
# driver = neutron.services.metering.drivers.noop.noop_driver.NoopMeteringDriver
# Example of non-default driver
driver = neutron.services.metering.drivers.iptables.iptables_driver.IptablesMeteringDriver
 
# Interval between two metering measures
measure_interval = 30

# Interval between two metering reports
report_interval = 300
  
# interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
  
use_namespaces = True
  
#interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
```
  
#### 重启neutron-service服务与neutrong-metering-agent服务
  
```
systemctl restart neutron-server.service
systemctl restart neutron-metering-agent.service
如果neutron-metering-agent 为新安装，需要加入开机自动启动，systemctl enable neutron-metering-agent.service
neutron agent-list (查看代理是否已经运行)
```
  
  
#### 配置Neutron-metering 采集信息

Create some metering labels for traffic passing through routers external interface
  
The following will meter all traffic going through routers’ external interfaces:

```
neutron meter-label-create public-in
neutron meter-label-rule-create public-in 0.0.0.0/0 --direction ingress

neutron meter-label-create public-out
neutron meter-label-rule-create public-out 0.0.0.0/0 --direction egress
```
  
#### 查看iptables 上的规则链
  
```
iptables -L -vnx
  
ip netns exec qrouter-d31150a1-e519-46e5-a5bc-a5ab94c1dab1 iptables -t filter -L neutron-meter-l-5814b182-67a -v -n -x  (查看流量统计情况,qrouter 与neutron-meter-l可以通过在/var/log/neutron/metering-agent.log中查看到
```
  
#### 查看统计信息
  
```
ceilometer meter-list  （会出现bandwidth采集名称)
ceilometer sample-list -m bandwidth  （查询bandwidth采样信息）
ceilometer statistics -m bandwidth --period 60 -q "resource_id= xxxxxxxx" 　（查看统计信息）
```
  
