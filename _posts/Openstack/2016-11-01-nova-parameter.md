---
layout: post
title: Nova 的属性参数以及libvirt.xml文件 
date: 2016-10-27 16:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Nova parameter libvirt.xml]
---

* content
{:toc}

#### 介绍

介绍一些nova 的使用属性参数，通过这些参数能够更好的理解nova





#### nova libvirt.xml使用

nova 使用libvirt.xml分为两种情况，如下：

* get_guest_xml 方法获取

```
 使用的包括: 

1) _get_existing_domain_xml
2) hard_reboot
3) recue
4) spawn
5) post_live_migration_at_destination
6) finish_migration
7) finish_revert_migration

```

* _get_existing_domain_xml 方法获取

```
使用的包括: 

1) resume
2) unrescue_xml
```


#### nova boot client url的body参数

```
{u'server': {u'name': u'fabian_pdb', u'imageRef': u'', u'block_device_mapping_v2': [{u'boot_index': u'0', u'uuid': u'ef8c480b-6444-4370-ac47-d8b70c1733b4', u'source_type': u'image', u'volume_size': u'1', u'destination_type': u'volume', u'delete_on_termination': False}], u'flavorRef': u'1', u'max_count': 1, u'min_count': 1, u'networks': [{u'uuid': u'bde7281f-933a-4bbf-8028-f6e4968c32fd'}], 'scheduler_hints': {}}}
```

#### block_mapping_device 参数

```
block_mapping_device
[{'guest_format': None, 'boot_index': 0, 'no_device': None, 'connection_info': None, 'snapshot_id': None, 'volume_size': 1, 'device_name': None, 'disk_bus': None, 'image_id': u'ef8c480b-6444-4370-ac47-d8b70c1733b4', 'source_type': u'image', 'device_type': None, 'volume_id': None, 'destination_type': u'volume', 'delete_on_termination': False}]

```

#### nova boot instance 参数

```
Instance(access_ip_v4=None,access_ip_v6=None,architecture=None,auto_disk_config=False,availability_zone=None,cell_name=None,cleaned=False,config_drive='',created_at=2016-10-31T03:01:25Z,default_ephemeral_device=None,default_swap_device=None,deleted=False,deleted_at=None,disable_terminate=False,display_description='fabian_pdb',display_name='fabian_pdb',ephemeral_gb=0,ephemeral_key_uuid=None,fault=<?>,host='juno',hostname='fabian-pdb',id=40,image_ref='',info_cache=InstanceInfoCache,instance_type_id=2,kernel_id='',key_data=None,key_name=None,launch_index=0,launched_at=None,launched_on='juno',locked=False,locked_by=None,memory_mb=512,metadata={},node='juno',numa_topology=None,os_type=None,pci_devices=<?>,power_state=0,progress=0,project_id='3d29f317c9bd42c7b9f331b7c8aeb883',ramdisk_id='',reservation_id='r-nhgeqner',root_device_name='/dev/vda',root_gb=1,scheduled_at=None,security_groups=SecurityGroupList,shutdown_terminate=False,system_metadata={image_base_image_ref='',image_container_format='bare',image_disk_format='qcow2',image_min_disk='1',image_min_ram='0',instance_type_ephemeral_gb='0',instance_type_flavorid='1',instance_type_id='2',instance_type_memory_mb='512',instance_type_name='m1.tiny',instance_type_root_gb='1',instance_type_rxtx_factor='1.0',instance_type_swap='0',instance_type_vcpu_weight=None,instance_type_vcpus='1',network_allocated='True'},task_state='spawning',terminated_at=None,updated_at=2016-10-31T03:01:33Z,user_data=None,user_id='b29694c6e95c40809e6bff716529762f',uuid=cfd22c8e-1b78-4f24-8615-42446a14a89c,vcpus=1,vm_mode=None,vm_state='building')
```

#### block_device_info 参数

```
{'block_device_mapping': [{'guest_format': None, 'boot_index': 0, 'mount_device': u'/dev/vda', 'connection_info': {u'driver_volume_type': u'iscsi', 'serial': u'72b1746e-5aeb-4690-b121-0e30887c98e3', u'data': {u'access_mode': u'rw', u'target_discovered': False, u'encrypted': False, u'qos_specs': None, u'target_iqn': u'iqn.2010-10.org.openstack:volume-72b1746e-5aeb-4690-b121-0e30887c98e3', u'target_portal': u'10.10.10.117:3260', u'volume_id': u'72b1746e-5aeb-4690-b121-0e30887c98e3', u'target_lun': 0, u'auth_password': u'mN24KKwGe2qXNRnp', u'auth_username': u'7LDg26AAWBbteyr2oeoi', u'auth_method': u'CHAP'}}, 'disk_bus': None, 'device_type': None, 'delete_on_termination': False}], 'root_device_name': u'/dev/vda', 'ephemerals': [], 'swap': None}

```

#### disk_info 参数

```
{'disk_bus': 'virtio', 'cdrom_bus': 'ide', 'mapping': {u'/dev/vda': {'bus': 'virtio', 'boot_index': '1', 'type': 'disk', 'dev': u'vda'}, 'root': {'bus': 'virtio', 'boot_index': '1', 'type': 'disk', 'dev': u'vda'}}}
```


#### network_info 参数

```
[VIF({'profile': {}, 'ovs_interfaceid': u'cbda95c2-f24c-414e-aad4-4bc5aa23cd43', 'network': Network({'bridge': 'br-int', 'subnets': [Subnet({'ips': [FixedIP({'meta': {}, 'version': 4, 'type': 'fixed', 'floating_ips': [], 'address': u'5.5.5.118'})], 'version': 4, 'meta': {'dhcp_server': u'5.5.5.103'}, 'dns': [IP({'meta': {}, 'version': 4, 'type': 'dns', 'address': u'114.114.114.114'})], 'routes': [], 'cidr': u'5.5.5.0/24', 'gateway': IP({'meta': {}, 'version': 4, 'type': 'gateway', 'address': u'5.5.5.1'})})], 'meta': {'injected': False, 'tenant_id': u'3d29f317c9bd42c7b9f331b7c8aeb883'}, 'id': u'bde7281f-933a-4bbf-8028-f6e4968c32fd', 'label': u'fabian_pri'}), 'devname': u'tapcbda95c2-f2', 'vnic_type': u'normal', 'qbh_params': None, 'meta': {}, 'details': {u'port_filter': True, u'ovs_hybrid_plug': True}, 'address': u'fa:16:3e:34:ea:5c', 'active': False, 'type': u'ovs', 'id': u'cbda95c2-f24c-414e-aad4-4bc5aa23cd43', 'qbg_params': None})]
```


#### libvirt.xml 的xml文件参数

```
'<domain type="qemu">\n  <uuid>f2f35976-7921-4f9b-9e1a-7767c56af2ce</uuid>\n  <name>instance-00000029</name>\n  <memory>524288</memory>\n  <vcpu cpuset="0-7">1</vcpu>\n  <metadata>\n    <nova:instance xmlns:nova="http://openstack.org/xmlns/libvirt/nova/1.0">\n      <nova:package version="2014.2.2-1.el7"/>\n      <nova:name>fabian_pdb</nova:name>\n      <nova:creationTime>2016-10-31 06:38:15</nova:creationTime>\n      <nova:flavor name="m1.tiny">\n        <nova:memory>512</nova:memory>\n        <nova:disk>1</nova:disk>\n        <nova:swap>0</nova:swap>\n        <nova:ephemeral>0</nova:ephemeral>\n        <nova:vcpus>1</nova:vcpus>\n      </nova:flavor>\n      <nova:owner>\n        <nova:user uuid="b29694c6e95c40809e6bff716529762f">fabian</nova:user>\n        <nova:project uuid="3d29f317c9bd42c7b9f331b7c8aeb883">fabian</nova:project>\n      </nova:owner>\n    </nova:instance>\n  </metadata>\n  <sysinfo type="smbios">\n    <system>\n      <entry name="manufacturer">Fedora Project</entry>\n      <entry name="product">OpenStack Nova</entry>\n      <entry name="version">2014.2.2-1.el7</entry>\n      <entry name="serial">d38029d1-a06e-4155-8920-584f54963002</entry>\n      <entry name="uuid">f2f35976-7921-4f9b-9e1a-7767c56af2ce</entry>\n    </system>\n  </sysinfo>\n  <os>\n    <type>hvm</type>\n    <boot dev="hd"/>\n    <smbios mode="sysinfo"/>\n  </os>\n  <features>\n    <acpi/>\n    <apic/>\n  </features>\n  <clock offset="utc"/>\n  <cpu match="exact">\n    <topology sockets="1" cores="1" threads="1"/>\n  </cpu>\n  <devices>\n    <disk type="block" device="disk">\n      <driver name="qemu" type="raw" cache="none"/>\n      <source dev="/dev/disk/by-path/ip-10.10.10.117:3260-iscsi-iqn.2010-10.org.openstack:volume-6c2d7237-bf14-4da3-8c8c-0d3e19e99bf0-lun-0"/>\n      <target bus="virtio" dev="vda"/>\n      <serial>6c2d7237-bf14-4da3-8c8c-0d3e19e99bf0</serial>\n    </disk>\n    <interface type="bridge">\n      <mac address="fa:16:3e:72:6e:2c"/>\n      <model type="virtio"/>\n      <driver name="qemu"/>\n      <source bridge="qbrdcadb3f6-30"/>\n      <target dev="tapdcadb3f6-30"/>\n    </interface>\n    <serial type="file">\n      <source path="/var/lib/nova/instances/f2f35976-7921-4f9b-9e1a-7767c56af2ce/console.log"/>\n    </serial>\n    <serial type="pty"/>\n    <input type="tablet" bus="usb"/>\n    <graphics type="vnc" autoport="yes" keymap="en-us" listen="0.0.0.0"/>\n    <video>\n      <model type="cirrus"/>\n    </video>\n    <memballoon model="virtio">\n      <stats period="10"/>\n    </memballoon>\n  </devices>\n</domain>\n'
```


#### 其它一些参数

nova 另外还包括一些参数，如context关于项目认证的一些参数，quota关于配额限制，policy权限控制等
