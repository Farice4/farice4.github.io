---
layout: post
title: Openstack client
date: 2017-01-16 11:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Client]
---

* content
{:toc}

#### 介绍
Openstack client(OSC) 为用户提供了一个同一的关于openstack cli操作与api调用的统一接口。





#### 工作过程

* OpenstackClient 提供connection.py用于创建keystone 认证连接,profile.py用于注册openstackclient下的所有客户端接口
* 其它组件通过调用openstackclient 的connection创建连接
* 连接创建完成后，直接调用每个注册服务下的_proxy.py中的proxy各个方法(每个组件下，根据api的版本目录下都对应了_proxy.py)


#### OpenStack Client使用举例

>构建连接文件conn.py
code:

```
from openstack import connection
from openstack import profile

auth_url='http://10.10.10.114:5000/v3'
region='RegionOne'
project_name='admin'
user_domain_name='Default'
project_domain_name='Default'
username='admin'
password='123'

def create_connection():
    prof = profile.Profile()
    prof.set_region(profile.Profile.ALL, region)
    conn = connection.Connection(profile=prof, auth_url=auth_url, project_name=project_name, username=username, passworin_name=project_domain_name)=user_domain_name, project_domaa
    return conn

```
以上代码导入了Openstack Client的connection方法与profile(组件接口注册), 创建了一个连接，当需要执行openstack client下的各个组件时，直接调用create_connection创建连接


>列出网络
code:

```
from conn import create_connection 
def list_networks(conn):
    print "List networks:"
    for pt in conn.network.networks():
        print pt.to_dict()

list_networks(create_connection) 调用conn.py中的连接
]# python connection.py 
List networks:
{u'status': u'ACTIVE', u'subnets': [u'df68f190-8933-4064-98cf-2392cfc9f590'], u'name': u'admin_pri', u'provider:physical_network': None, u'admin_state_up': True, u'tenant_id': u'93236417c37d49b4b027f1811ec5af5e', u'provider:network_type': u'gre', u'router:external': False, u'shared': False, u'id': u'2209c875-d84e-4d6a-afaa-d2a6036e56fb', u'provider:segmentation_id': 2}
{u'status': u'ACTIVE', u'subnets': [u'b7cd7a36-0d56-4b24-abd8-daa762c48710'], u'name': u'public', u'provider:physical_network': None, u'admin_state_up': True, u'tenant_id': u'93236417c37d49b4b027f1811ec5af5e', u'provider:network_type': u'gre', u'router:external': True, u'shared': False, u'id': u'dff6bacc-206a-48be-bc86-281d8e73fa56', u'provider:segmentation_id': 1}

```

> 列出loadbance pools(v1)
openstack client 不支持loadbance v1, 因此需要在openstack client 下修改pools.py中的base_path路径resource,由base_path = '/loadbance/pools' 修改为base_path = '/lb/pools'

下面是单个文件的所有code:

```
from openstack import profile
from openstack import connection

auth_url='http://10.10.10.114:5000/v3'
region='RegionOne'
project_name='admin'
user_domain_name='Default'
project_domain_name='Default'
username='admin'
password='123'

def create_connection():
    prof = profile.Profile()
    prof.set_region(profile.Profile.ALL, region)
    conn = connection.Connection(profile=prof, auth_url=auth_url, project_name=project_name, username=username, password=password, user_domain_name=user_domain_name, project_domain_name=project_domain_name)
    return conn

conn = create_connection()

# List loadbance pools
def list_pools(conn):
    print "List pools: "
    for pt in conn.network.pools():
        print pt.to_dict()
list_pools(conn)

# python connection.py 
List pools: 
{u'status': u'ACTIVE', u'lb_method': u'ROUND_ROBIN', u'protocol': u'TCP', u'description': u'', u'health_monitors': [], u'subnet_id': u'df68f190-8933-4064-98cf-2392cfc9f590', u'tenant_id': u'93236417c37d49b4b027f1811ec5af5e', u'admin_state_up': True, u'vip_id': u'e7845623-7bba-4331-b24a-b64f01723892', u'health_monitors_status': [], u'members': [], u'provider': u'haproxy', u'status_description': None, u'id': u'1b614f12-56ae-45e9-84f3-cda906203a0e', u'name': u'pool2'}
{u'status': u'ACTIVE', u'lb_method': u'ROUND_ROBIN', u'protocol': u'TCP', u'description': u'', u'health_monitors': [], u'subnet_id': u'df68f190-8933-4064-98cf-2392cfc9f590', u'tenant_id': u'93236417c37d49b4b027f1811ec5af5e', u'admin_state_up': True, u'vip_id': None, u'health_monitors_status': [], u'members': [], u'provider': u'haproxy', u'status_description': None, u'id': u'd242dc52-5eb1-4bc6-8125-147b915c2ef2', u'name': u'pool3'}
{u'status': u'ACTIVE', u'lb_method': u'ROUND_ROBIN', u'protocol': u'TCP', u'description': u'', u'health_monitors': [], u'subnet_id': u'df68f190-8933-4064-98cf-2392cfc9f590', u'tenant_id': u'93236417c37d49b4b027f1811ec5af5e', u'admin_state_up': True, u'vip_id': None, u'health_monitors_status': [], u'members': [], u'provider': u'haproxy', u'status_description': None, u'id': u'e417cd50-118f-485c-9e38-003a3fb0f751', u'name': u'pool3'}

```
