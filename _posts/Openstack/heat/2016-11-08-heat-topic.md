---
layout: post
title: Heat 介绍
date: 2016-11-08 16:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Heat topic]
---

* content
{:toc}

#### 介绍

Heat 是一套业务流程平台，帮助用户更轻松的配置以Openstack为基础的云体系。通过Heat 的模板编排，完成各种资源调用，最终实现自动管理。





Openstack Heat 目前支持亚马逊的CloudFormation模板格式，也支持Heat自有的Hot模板格式。

#### Heat 架构

主要介绍heat服务，heat 结构，heat与各个模块之间的关系

##### Heat 服务介绍

Heat 服务包含如下：


    heat-api-cfn            组件提供了Amazon style 的查询 API，可以完全兼容于Amazon的CloudFormation，对于API的请求，同heat-api类似，处理之后，通过RPC传递给heat-engine进一步处理。
    heat-api-cloudwatch     组件用于alarm指标监控。
    heat-api                组件实现OpenStack支持的REST API。该组件通过把API请求经由AMQP传送给Heat engine来处理API请求。
    heat-engine             组件是heat中的核心模块，主要的逻辑业务处理模块。此模块最终完成应用系统的创建和部署。
    heat-cfntools           组件是一个单独的工具,主要用来完成虚拟机实例内部的操作配置任务。

##### Heat 架构介绍

> Heat 整体架构

![Heat framework](/assets/images/201611/heat_framework.png)

用户在Horizon或者命令行中提交包含模板和输入参数的请求，Horizon或者命令行工具会将请求转换为REST 格式的API调用，然后调用Heat-api或者Heat-api-cfn。

Heat-api与Heat-api-cfn在这个过程中会验证模板的正确性，然后通过RabbitMQ传递给Heat Engine来处理请求。如果验证不通过，会提示错误，终止Stack创建。


> Heat Engine架构

![Heat Engine](/assets/images/201611/heat_engine.png)

当Heat Engine拿到请求后，会进行资源解析，每种资源都对应Openstack 其它客户端，通过发送REST的请求给其它服务，完成请求的最终处理。

Heat Engine 作用分三层介绍:

* 第一层处理Heat层面请求，根据模板和参数创建Stack,Stack由各种资源组成。
* 第二层解析Stack各种资源的依赖关系，Stack和Stack嵌套关系。
* 第三层是根据解析出来的关系，依次调用各个客户端来创建资源。


#### Heat 模板介绍

Heat 构建Stack的实现依赖于模板，Heat模板支持JSON格式的CFN模板;同时支持基于YAML格式的HOT模板。CFN模板主要保持AWS的兼容，HOT格式是Heat自由的模板。

> Heat 模板格式介绍

一个典型的HOT的模板由下列元素构成:


![Heat framework](/assets/images/201611/heat_template_format.png)

* 模板版本(heat_template_version)： 必须指定，如果指定的版本不在范围内会出现错误，无法继续构建
* 参数列表(parameters)： 可选, 配置参数后，在resource中可以通过内建函数获取
* 资源列表(resources):  必须指定，生成Stack的各种资源。
* 输出列表(outputs):  可选，生成Stack后可以通过heat output查询的信息

> Heat 模板中的内建函数

Heat 中的内建函数，可以通过直接调用函数，获取数值。参数如下：

* get_attr

作用: 获取所创建资源的属性,一般用于outputs中获取resources中的信息, 如:

```
resources:
  my_instance:
    type: OS::Nova::Server
# ...

outputs:
  instance_ip:
    description: ....
    value: { get_attr: [my_instance, first_address] }
```

* get_file

作用: 获取文件的内容, 如:

```
resources:
  my_instance:
    type: OS::Nova::Server
    properties:
      user_data:
        get_file: install_http.sh
```

* get_param 

作用： 引用模板参数中的指定参数,如:

```
parameters:
  image:
    type: string
    description: instance image file
    # defaults: xxxxxxxxxxx

resources:
  my_instance:
    type: OS::Nova::Server
    properties:
      image: { get_param: image }
```

* get_resource

作用: 获取模板中指定资源,如：

```
heat_template_version: 2014-10-16
description: A simple server.
resources:
  server:
    type: OS::Nova::Server
    properties:
      block_device_mapping:
        - device_name: vda
          delete_on_termination: true
          volume_id: { get_resource: volume  }
      flavor: m1.tiny
      networks:
        - network: 45b855c7-34df-4002-aabf-c1e80ff352ed

  volume:
    type: OS::Cinder::Volume
    properties:
      image: 'TestVM'
      size: 1
```

* list_join

作用: 使用指定的分隔符将一个list中的字符合成一个字符串。

```
语法：
list_join:
- <delimiter>
- <list to join>
```

* digest

作用: 在指定的值上使用algorithm

```
语法:
digest:
- <algorithm>
- <value>
```

* repeat

作用: 迭代fore_each中的列表，按照template的格式生成一个list

```
语法:
repeat:
  template:
    <template>
  for_each:
    <var>: <list>
```

* resource_facade

作用: 检索资源的数据

```
语法：
resource_facade: <data type>
```

* str_replace

作用: 使用params中的值替换template中的占位符，从而构造一个新的字符串

```
语法：
str_replace:
  template: <template string>
  params: <parameter mappings>
```

* str_split

作用: 将一个字符串按照分隔符分割成一个list

```
语法：
str_split:
- ','
- string,to,split
```

* map_merge

作用: 合并多个map, 且后面的覆盖前面map中同一个key 的值

```
语法：
map_merge:
- <map 1>
- <map 2>
```

其它还包括的内建函数，参考以下链接:

[Heat模板内建函数: http://docs.openstack.org/developer/heat/template_guide/functions.html#ref](http://docs.openstack.org/developer/heat/template_guide/functions.html#ref)


#### Heat cfntools 介绍

cfntools是在虚拟机中跑的一堆辅助脚本，一般用来获取metadata，并根据metadata做一些自动化配置。

cfntools 与heat独立，需要单独安装才能使用。


#### Heat 支持的资源类型

|ID|资源名称|资源类型|备注|
|-|-|-|-|
|1|aodh|OS::Aodh::Alarm OS::Aodh::EventAlarm|原ceilometer alarm|
|2|barbican|OS::Barbican::CertificateContainer OS::Barbican::GenericContainer|密钥管理服务|
|3|ceilometer||计量服务|
|4|cinder|OS::Cinder::Volume OS::Cinder::VolumeType|块存储|
|5|designate|OS::Designate::Domain OS::Designate::Record|DNS服务|
|6|glance|OS::Glance::Image|镜像服务|
|7|keystone|OS::Keystone::Role OS::Keystone::User|认证服务|
|8|magnum|OS::Magnum::Bay|容器服务|
|9|manila|OS::Manila::Share|文件共享服务|
|10|mistral|OS::Mistral::Workflow|工作流组件|
|11|monasca|OS::Monasca::Notification|监控服务|
|12|nova|OS::Nova::Server|计算服务|
|13|neutron|OS::Neutron::Port|网络服务|
|14|sahara|OS::Sahara::Cluster|大数据服务|
|15|senlin|OS::Senlin::Cluster|对象集群服务|
|16|swift|OS::Swift::Container|对象存储服务|
|17|trove|OS::Trove::Instance|数据库服务|
|18|zaqar|OS::Zaqar::Queue|消息服务|
|19|Heat|OS::Heat::Stack|编排服务|

更多的支持资源类型，参考以下链接:

[Heat 支持资源类型: http://docs.openstack.org/developer/heat/template_guide/index.html](http://docs.openstack.org/developer/heat/template_guide/index.html)
