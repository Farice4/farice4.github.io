---
layout: post
title: Heat Template Example
date: 2016-11-08 16:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Heat Template]
---

* content
{:toc}

#### 介绍

本文主要介绍模板在Heat中的使用，以及Heat常用的命令使用。





#### Heat 模板举例介绍

 前面一篇文档已经介绍过了，模板的格式包括版本（必填）、参数（可选）、资源（必填）、输出（可选）四个部分。

> 模板带参数，创建时手动指定参数

* 模板文件

```
# 模板版本配置
heat_template_version: 2014-10-16

description: A Simple Server

# 参数部分
parameters:
    image_id:
        type: string
        description: Image ID of Name
    network_id:
        type: string
        description: private network ID of Name
    flavor_id:
        type: string
        description: ID or Name for flavor

# 资源部分
resources:
    # server 资源
    server:
        # 使用了OS关于Nova部分的资源
        type: OS::Nova::Server
        properties:
            block_device_mapping:
                - device_name: vda
                  delete_on_termination: true
                  volume_id: { get_resource: volume }

            # 这里使用了内建函数get_param
            flavor: { get_param: flavor_id }
            networks:
                - network: { get_param: network_id }

    # cinder 块存储卷资源 
    volume:
        type: OS::Cinder::Volume
        properties:
            image: { get_param: image_id }
            size: 1
# 输出部分
outputs:
    server_networks:
        description: The network of the deployed server
      
        # 使用内建函数get_attr获取resources中的server与networks信息
        value: { get_attr: [server, networks] }

```

* 创建Stack

```
# heat stack-create -f cirros_os_new.yaml -P image_id=625d4f2c-cf67-4af3-afb6-c7220f766947 -P network_id=45b855c7-34df-4002-aabf-c1e80ff352ed -P flavor_id=1 heat_cirros_example
+--------------------------------------+---------------------+--------------------+----------------------+
| id                                   | stack_name          | stack_status       | creation_time        |
+--------------------------------------+---------------------+--------------------+----------------------+
| 4a7b21b2-17ec-4de1-b4f7-d2ff01eda698 | heat_cirros_example | CREATE_IN_PROGRESS | 2016-11-09T08:55:09Z |
+--------------------------------------+---------------------+--------------------+----------------------+
```

* 创建完成，查看创建结果

```
# heat stack-list
+--------------------------------------+---------------------+-----------------+----------------------+
| id                                   | stack_name          | stack_status    | creation_time        |
+--------------------------------------+---------------------+-----------------+----------------------+
| 4a7b21b2-17ec-4de1-b4f7-d2ff01eda698 | heat_cirros_example | CREATE_COMPLETE | 2016-11-09T08:55:09Z |
+--------------------------------------+---------------------+-----------------+----------------------+

```

* 查看nova云主机信息

```
# nova list
+--------------------------------------+-----------------------------------------+--------+------------+-------------+-----------------------+
| ID                                   | Name                                    | Status | Task State | Power State | Networks              |
+--------------------------------------+-----------------------------------------+--------+------------+-------------+-----------------------+
| 65d6422e-b54e-4ec1-9ea2-aa61ae443fe0 | heat_cirros_example-server-y57it2rxrbgy | ACTIVE | -          | Running     | fabian-priv=5.5.5.189 |
+--------------------------------------+-----------------------------------------+--------+------------+-------------+-----------------------+
```

* 查看heat stack output 信息

```
# heat output-list 4a7b21b2-17ec-4de1-b4f7-d2ff01eda698
+-----------------+------------------------------------+
| output_key      | description                        |
+-----------------+------------------------------------+
| server_networks | The network of the deployed server |
+-----------------+------------------------------------+

# heat output-show 4a7b21b2-17ec-4de1-b4f7-d2ff01eda698 server_networks
{
  "fabian-priv": [
    "5.5.5.189"
  ]
}

```

* 查看stack事件信息

```
# heat event-list 4a7b21b2-17ec-4de1-b4f7-d2ff01eda698
+---------------+--------------------------------------+------------------------+--------------------+----------------------+
| resource_name | id                                   | resource_status_reason | resource_status    | event_time           |
+---------------+--------------------------------------+------------------------+--------------------+----------------------+
| server        | 3be05029-3a2b-4215-af7e-015efb1f8f7b | state changed          | CREATE_COMPLETE    | 2016-11-09T08:55:39Z |
| server        | 36c620e6-f10f-4cc8-a737-c3374b1188bd | state changed          | CREATE_IN_PROGRESS | 2016-11-09T08:55:21Z |
| volume        | 00ef4f9b-71ae-4c06-886a-6042e69721d0 | state changed          | CREATE_COMPLETE    | 2016-11-09T08:55:21Z |
| volume        | 66089573-c867-4cd5-8b59-0d49edb5e177 | state changed          | CREATE_IN_PROGRESS | 2016-11-09T08:55:09Z |
+---------------+--------------------------------------+------------------------+--------------------+----------------------+

查看事件详细信息
# heat event-show 4a7b21b2-17ec-4de1-b4f7-d2ff01eda698 server 3be05029-3a2b-4215-af7e-015efb1f8f7b

```

* horizon 上查看stack信息

![stack_cirros](/assets/images/201611/stack1.png)

查看stack详细信息

![stack_cirros](/assets/images/201611/stack_cirros2.png)


> 模板没有参数，没有输出，启动时绑定floating ip，设置windows 密码

```
heat_template_version: 2014-10-16
description: windows server boot bind floating ip and config password
resources:
    server:
        type: OS::Nova::Server
        properties:
            block_device_mapping:
                - device_name: vda
                  delete_on_termination: true
                  volume_id: { get_resource: volume  }
            flavor: m1.small

            # 这里使用了metadata为windows配置注入密码参数
            metadata: { "admin_pass": "eayun@2015" }
            networks:
                - port: { get_resource: port  }
    port:
        # 这里使用了Port资源
        type: OS::Neutron::Port
        properties:
            # 租户网络的网络id
            network: 556ebd8d-72ea-482f-897b-8354e2635a59
    floating_ip:
        type: OS::Neutron::FloatingIP
        properties:
            # 外部网络的网络id
            floating_network: f64f4451-7441-4a81-8cac-a4c4acd4cc40
    # 这里使用了floatingip 映射的绑定
    floating_ip_assoc:
        type: OS::Neutron::FloatingIPAssociation
        properties:
            floatingip_id: { get_resource: floating_ip  }
            port_id: { get_resource: port  }
    volume:
        type: OS::Cinder::Volume
        properties:
            image: '26f31f40-05cb-431b-bacf-63b9caed9623'
            size: 20

```

Stack创建完成后，通过nova list可以看到虚拟机已经进行了floating ip绑定,同时使用传递的密码能够正常登录进入windows系统

> 模板创建网络与路由并绑定外网网关

```
heat_template_version: 2013-05-23
description: HOT template for two interconnected VMs with floating ips.
parameters:
    public_net:
        type: string
        description: public network id
        # 指定了default的外部网络，网络id
        default: f64f4451-7441-4a81-8cac-a4c4acd4cc40
resources:
    private_net:
        # 调用Neutron的net资源
        type: OS::Neutron::Net
        properties:
            # 定义租户网络名称
            name: private-net
    private_subnet:
        type: OS::Neutron::Subnet
        properties:
            network_id: { get_resource: private_net  }
            # 定义租户网络的子网掩码
            cidr: 8.8.8.0/24
            gateway_ip: 8.8.8.1
    router1:
        type: OS::Neutron::Router
        properties:
            external_gateway_info:
                network: { get_param: public_net  }
    router1_interface:
        # 调用Neutron路由资源进行路由连接配置
        type: OS::Neutron::RouterInterface
        properties:
            router_id: { get_resource: router1  }
            subnet_id: { get_resource: private_subnet  }

```

Stack创建完成后，通过查看发现，已经创建了租户网络与路由，并且租户网络与路由都已经连接

> 模板带userdata脚本

```
heat_template_version: 2014-10-16
parameters:
    key_name:
        type: string
        description: instance key name
        default: fabian
    flavor:
       type: string
       default: m1.small
    image:
        type: string
        default: c4cc706b-4bc0-4c6e-a603-a1bf634b13d1
resources:
    server:
        type: OS::Nova::Server
        properties:
            block_device_mapping:
                - device_name: vda
                  delete_on_termination: true
                  volume_id: { get_resource: volume  }
            flavor: { get_param: flavor  }
            key_name: { get_param: key_name  }
            networks:
                - port: { get_resource: port  }
            
            # 这里使用了user_data，当系统启动完成后会进行脚本运行
            user_data_format: RAW
            user_data: |
                #!/bin/bash
                echo "Running boot script"
                echo "Hello test fabian" > /tmp/fabian.txt
                yum install httpd -y
                echo "Hello Fabian Web" > /var/www/html/index.html
                systemctl stop firewalld
                systemctl start httpd
    port:
        type: OS::Neutron::Port
        properties:
            network: 556ebd8d-72ea-482f-897b-8354e2635a59
    floating_ip:
        type: OS::Neutron::FloatingIP
        properties:
            floating_network: f64f4451-7441-4a81-8cac-a4c4acd4cc40
    floating_ip_assoc:
        type: OS::Neutron::FloatingIPAssociation
        properties:
            floatingip_id: { get_resource: floating_ip  }
            port_id: { get_resource: port  }
    volume:
        type: OS::Cinder::Volume
        properties:
            image: { get_param: image  }
            size: 20

```

> 模板自动实现Linux下负载均衡

* AutoScaling介绍

![heat_auto](/assets/images/201611/heat_auto.png)

Autoscaling 是 Heat 的另外一大特性，它通过ceilometer监控伸缩组(scaling group)的虚拟机的负载，当虚拟机的负载超过阈值时，ceilometer 发送告警给 heat，heat 收到告警后，根据伸缩策略(scaling policy)增加虚拟机，并将虚拟机加入到 load balancer 的 backends 中；反之，当虚拟机的负载很低时，heat 收到告警后删除虚拟机。

Resource的依赖关系如下:

![heat_auto](/assets/images/201611/heat_resource.png)


* 模板文件lb_env.yaml

```
# 这个文件主要记录一些环境配置信息
parameters:
  image: c4cc706b-4bc0-4c6e-a603-a1bf634b13d1
  key_name: fabian
  flavor: m1.small
  network: 45b855c7-34df-4002-aabf-c1e80ff352ed
  subnet_id: ad212162-ffa1-4ea3-8dfc-f0ecf2603202
  external_network_id: f64f4451-7441-4a81-8cac-a4c4acd4cc40
```

* 模板文件withlb.yaml

```
# 主要用来实现AutoScaling
heat_template_version: 2014-10-16
description: AutoScaling With Alarm Example
parameters:
  image:
    type: string
    description: Image used for servers
  key_name:
    type: string
    description: SSH key to connect to the servers
  flavor:
    type: string
    description: flavor used by the web servers
  network:
    type: string
    description: network to use
  subnet_id:
    type: string
    description: subnet on which the load balancer will be located(UUID)
  external_network_id:
    type: string
    description: UUID of a Neutron external network
resources:
  server_group:
    # 定义了AutoScalingGroup，最大3台最小1台instance
    type: OS::Heat::AutoScalingGroup
    properties:
      min_size: 1
      max_size: 3
      resource:
        type: lb_server.yaml
        properties:
          flavor: {get_param: flavor}
          image: {get_param: image}
          key_name: {get_param: key_name}
          pool_id: {get_resource: pool}
          network: {get_param: network}
          metadata: {"metering.stack": {get_param: "OS::stack_id"}}
          user_data:
            str_replace:
              template: |
                  #!/bin/bash -v
                  yum -y install httpd
                  systemctl restart sshd
                  systemctl disable firewalld
                  systemctl stop firewalld
                  systemctl enable httpd.service
                  systemctl start httpd.service
                  echo "$HOSTNAME" >  /var/www/html/index.html
                  echo "$stack_id" >> /var/www/html/index.html
              params:
                  $stack_id: {get_param: "OS::stack_id"}

  # 这里定义了一个up的策略，后面会进行调用
  scaleup_policy:
    type: OS::Heat::ScalingPolicy
    properties:
      adjustment_type: change_in_capacity
      auto_scaling_group_id: {get_resource: server_group}
      cooldown: 60
      scaling_adjustment: 1

  # 这里定义了一个down的策略，后面会调用
  scaledown_policy:
    type: OS::Heat::ScalingPolicy
    properties:
      adjustment_type: change_in_capacity
      auto_scaling_group_id: {get_resource: server_group}
      cooldown: 60
      scaling_adjustment: -1
  cpu_alarm_high:
    type: OS::Ceilometer::Alarm
    properties:
      description: Scale-up if the average CPU > 50% for 1 minute
      meter_name: cpu_util
      statistic: avg
      # 采集数据周期的时间跨度
      period: 60
      # 采集跨度的次数
      evaluation_periods: 1
      # 这里是判断的阀值
      threshold: 50
      # 这里在使用ceilometer进行cpu_util平均值进行检测,后做的一个警告动作，调用了scaleup_policy策略
      alarm_actions:
        - {get_attr: [scaleup_policy, alarm_url]}
      matching_metadata: {'metadata.user_metadata.stack': {get_param: "OS::stack_id"}}
      comparison_operator: gt
  cpu_alarm_low:
    type: OS::Ceilometer::Alarm
    properties:
      description: Scale-down if the average CPU < 15% for 1 minute
      meter_name: cpu_util
      statistic: avg
      period: 60
      evaluation_periods: 1
      threshold: 15
      alarm_actions:
        - {get_attr: [scaledown_policy, alarm_url]}
      matching_metadata: {'metadata.user_metadata.stack': {get_param: "OS::stack_id"}}
      comparison_operator: lt
  
  # 定义了一个监控，用于检测各节点健康
  monitor:
    type: OS::Neutron::HealthMonitor
    properties:
      type: TCP
      delay: 5
      max_retries: 5
      timeout: 5
  pool:
    type: OS::Neutron::Pool
    properties:
      protocol: HTTP
      monitors: [{get_resource: monitor}]
      subnet_id: {get_param: subnet_id}
      lb_method: ROUND_ROBIN
      vip:
        protocol_port: 80
  lb:
    type: OS::Neutron::LoadBalancer
    properties:
      protocol_port: 80
      pool_id: {get_resource: pool}
  lb_floating:
    type: "OS::Neutron::FloatingIP"
    properties:
      floating_network_id: {get_param: external_network_id}
      port_id: {get_attr: [pool, vip, port_id]}

outputs:
  scale_up_url:
    description: >
      This URL is the webhook to scale up the autoscaling group.  You
      can invoke the scale-up operation by doing an HTTP POST to this
      URL; no body nor extra headers are needed.
    value: {get_attr: [scaleup_policy, alarm_url]}
  scale_dn_url:
    description: >
      This URL is the webhook to scale down the autoscaling group.
      You can invoke the scale-down operation by doing an HTTP POST to
      this URL; no body nor extra headers are needed.
    value: {get_attr: [scaledown_policy, alarm_url]}
  ceilometer_query:
    value:
      str_replace:
        template: >
          ceilometer statistics -m cpu_util
          -q metadata.user_metadata.stack=stackval -p 600 -a avg
        params:
          stackval: { get_param: "OS::stack_id"  }
    description: >
      This is a Ceilometer query for statistics on the cpu_util meter
      Samples about OS::Nova::Server instances in this stack.  The -q
      parameter selects Samples according to the subject's metadata.
      When a VM's metadata includes an item of the form metering.X=Y,
      the corresponding Ceilometer resource has a metadata item of the
      form user_metadata.X=Y and samples about resources so tagged can
      be queried with a Ceilometer query term of the form
      metadata.user_metadata.X=Y.  In this case the nested stacks give
      their VMs metadata that is passed as a nested stack parameter,
      and this stack passes a metadata of the form metering.stack=Y,
      where Y is this stack's ID.
  website_url:
    value:
      str_replace:
        template: http://host/
        params:
          host: { get_attr: [lb_floating, floating_ip_address]  }
    description: >
      This URL is the "external" URL that can be used to access the
      website.

```

* 模板文件lb_server.yaml 

```
heat_template_version: 2014-10-16
description: A load-balancer server
parameters:
  image:
    type: string
    description: Image used for servers
  key_name:
    type: string
    description: SSH key to connect to the servers
  flavor:
    type: string
    description: flavor used by the servers
  pool_id:
    type: string
    description: Pool to contact
  user_data:
    type: string
    description: Server user_data
  metadata:
    type: json
  network:
    type: string
    description: network to use
resources:
  server:
    type: OS::Nova::Server
    properties:
      flavor: {get_param: flavor}
      image: {get_param: image}
      key_name: {get_param: key_name}
      metadata: {get_param: metadata}
      networks: [{"network": {get_param: network}}]
      user_data: {get_param: user_data}
      user_data_format: RAW
  member:
    type: OS::Neutron::PoolMember
    properties:
      pool_id: {get_param: pool_id}
      address: {get_attr: [server, first_address]}
      protocol_port: 80

```

* 运行Stack创建

```
heat stack-create -f withlb.yaml -e lb_env.yaml www
```

* Stack 检测

```
1、检测Stack创建是否成功
2、检测nova instance是否创建成功
3、检测ceilometer 关于alarm创建是否成功
4、检测lb创建是否成功
5、测试web访问
```

* 自动伸缩弹性测试

```
1、虚拟机加压，实现自动新增云主机
cat /dev/urandom > /dev/null &
2、测试web访问发现访问了不同instance的网站
3、关闭原虚拟机加压的命令
4、测试发现instance实现自动关闭一台云主机
```

参考地址:

[自动伸缩wiki: https://oa.eayun.cn/wiki/doku.php?id=eayunstack:heat:autoscaling](https://oa.eayun.cn/wiki/doku.php?id=eayunstack:heat:autoscaling)

[Heat 模板编辑参考:http://docs.openstack.org/developer/heat/template_guide/composition.html](http://docs.openstack.org/developer/heat/template_guide/composition.html)

[Heat 自动伸缩官方介绍:https://wiki.openstack.org/wiki/Heat/AutoScaling](https://wiki.openstack.org/wiki/Heat/AutoScaling)
