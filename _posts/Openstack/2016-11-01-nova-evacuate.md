---
layout: post
title: Nova evacuate
date: 2016-10-27 16:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Nova evacuate]
---

* content
{:toc}

#### 介绍

nova evacuate 实现当虚拟机所在宿主机出现宕机后，虚拟机可以通过evacuate将虚拟机从宕机的物理节点迁移至其它节点。
nova evacuate其实是通过虚拟机rebuild的过程完成的，原compute节点在重新恢复后会进行虚拟机删除





#### nova evacuate代码分析

入口文件nova/api/openstack/compute/contrib/evacuate.py中Controller类下的_evacuate方法

```
 def _evacuate(self, req, id, body):
    # 在这个方法中进行了共享存储判断，有没有admin_pass的判断，获取instance,判断instance是否
    # 在url封装的body中
    # 下一步调用compute_api下的evacuate方法
    try:
            instance = self.compute_api.get(context, id, want_objects=True)
            if instance.host == host:
                msg = _("The target host can't be the same one.")
                raise exc.HTTPBadRequest(explanation=msg)
            self.compute_api.evacuate(context, instance, host,
                                      on_shared_storage, password)
```

转到nova/compute/api.py中的evacuate方法

```
def evacuate(self, context, instance, host, on_shared_storage,
                 admin_password=None):

    # 在这个地方进行了instance host获取
    inst_host = instance.host
    service = objects.Service.get_by_compute_host(context, inst_host)
       
    # 判断了host的服务状态，nova-compute service
    if self.servicegroup_api.service_is_up(service):
        msg = (_('Instance compute service state on %s '
                 'expected to be down, but it was up.') % inst_host)
        LOG.error(msg)
        raise exception.ComputeServiceInUse(host=inst_host)

    instance.task_state = task_states.REBUILDING
    instance.save(expected_task_state=[None])
    self._record_action_start(context, instance, instance_actions.EVACUATE)

    # 调用rebuild重建
    return self.compute_task_api.rebuild_instance(context,
                   instance=instance,
                   new_pass=admin_password,
                   injected_files=None,
                   image_ref=None,
                   orig_image_ref=None,
                   orig_sys_metadata=None,
                   bdms=None,
                   recreate=True,
                   on_shared_storage=on_shared_storage,
                   host=host)
```

转到nova/conductor/api.py中的ComputeTaskAPI类下的rebuild_instance方法

```
rebuild_instance(self, context, instance, orig_image_ref, image_ref,
                         injected_files, new_pass, orig_sys_metadata,
                         bdms, recreate=False, on_shared_storage=False,
                         preserve_ephemeral=False, host=None, kwargs=None):
        # kwargs unused but required for cell compatibility.
  
        # 这里调用了self._manager.rebuild_instance
        utils.spawn_n(self._manager.rebuild_instance, context,
```

转到nova/conductor/manager.py中的rebuild_instance方法

```
  def rebuild_instance(self, context, instance, orig_image_ref, image_ref,
                         injected_files, new_pass, orig_sys_metadata,
                         bdms, recreate, on_shared_storage,
                         preserve_ephemeral=False, host=None):

        with compute_utils.EventReporter(context, 'rebuild_server',
                                          instance.uuid):
            if not host:
                filter_properties = {'ignore_hosts': [instance.host]}
                request_spec = scheduler_utils.build_request_spec(context,
                                                                  image_ref,
                                                                  [instance])
                try:
                    hosts = self.scheduler_client.select_destinations(context,
                                                            request_spec,
                                                            filter_properties)
                    host = hosts.pop(0)['host']
                except exception.NoValidHost as ex:
                    with excutils.save_and_reraise_exception():
                        self._set_vm_state_and_notify(context,
                                'rebuild_server',
                                {'vm_state': instance.vm_state,
                                 'task_state': None}, ex, request_spec)
                        LOG.warning(_("No valid host found for rebuild"),
                                      instance=instance)

            # 这里开始调用compute上的manager.py中的rebuild_instance方法
            self.compute_rpcapi.rebuild_instance(context,
```

转到nova/compute/manager.py中的rebuild_instance方法

```
   def rebuild_instance(self, context, instance, orig_image_ref, image_ref,
                         injected_files, new_pass, orig_sys_metadata,
                         bdms, recreate, on_shared_storage,
                         preserve_ephemeral=False):
        context = context.elevated()

        if (bdms and
            any(not isinstance(bdm, obj_base.NovaObject)
                for bdm in bdms)):
            bdms = None

        orig_vm_state = instance.vm_state
        with self._error_out_instance_on_exception(context, instance):
            LOG.audit(_("Rebuilding instance"), context=context,
                      instance=instance)

            if recreate:
                if not self.driver.capabilities["supports_recreate"]:
                    raise exception.InstanceRecreateNotSupported

                self._check_instance_exists(context, instance)

                # To cover case when admin expects that instance files are on
                # shared storage, but not accessible and vice versa
                if on_shared_storage != self.driver.instance_on_disk(instance):
                    raise exception.InvalidSharedStorage(
                            _("Invalid state of instance files on shared"
                              " storage"))

                if on_shared_storage:
                    LOG.info(_('disk on shared storage, recreating using'
                               ' existing disk'))
                else:
                    image_ref = orig_image_ref = instance.image_ref
                    LOG.info(_("disk not on shared storage, rebuilding from:"
                               " '%s'") % str(image_ref))

                # NOTE(mriedem): On a recreate (evacuate), we need to update
                # the instance's host and node properties to reflect it's
                # destination node for the recreate.
                node_name = None
                try:
                    compute_node = self._get_compute_info(context, self.host)
                    node_name = compute_node.hypervisor_hostname
                except exception.NotFound:
                    LOG.exception(_LE('Failed to get compute_info for %s'),
                                  self.host)
                finally:
                    instance.host = self.host
                    instance.node = node_name
                    instance.save()

            if image_ref:
                image_meta = self.image_api.get(context, image_ref)
            else:
                image_meta = {}

            # This instance.exists message should contain the original
            # image_ref, not the new one.  Since the DB has been updated
            # to point to the new one... we have to override it.
            # TODO(jaypipes): Move generate_image_url() into the nova.image.api
            orig_image_ref_url = glance.generate_image_url(orig_image_ref)
            extra_usage_info = {'image_ref_url': orig_image_ref_url}
            self.conductor_api.notify_usage_exists(context,
                    obj_base.obj_to_primitive(instance),
                    current_period=True, system_metadata=orig_sys_metadata,
                    extra_usage_info=extra_usage_info)

            # This message should contain the new image_ref
            extra_usage_info = {'image_name': image_meta.get('name', '')}
            self._notify_about_instance_usage(context, instance,
                    "rebuild.start", extra_usage_info=extra_usage_info)

            instance.power_state = self._get_power_state(context, instance)
            instance.task_state = task_states.REBUILDING
            instance.save(expected_task_state=[task_states.REBUILDING])

            if recreate:
                self.network_api.setup_networks_on_host(
                        context, instance, self.host)

            network_info = compute_utils.get_nw_info_for_instance(instance)
            if bdms is None:
                bdms = objects.BlockDeviceMappingList.get_by_instance_uuid(
                        context, instance.uuid)

            block_device_info = \
                self._get_instance_block_device_info(
                        context, instance, bdms=bdms)

            def detach_block_devices(context, bdms):
                for bdm in bdms:
                    if bdm.is_volume:
                        # 这里调用了cinder api的detach操作,deatch volume
                        self.volume_api.detach(context, bdm.volume_id)

            files = self._decode_files(injected_files)

            kwargs = dict(
                context=context,
                instance=instance,
                image_meta=image_meta,
                injected_files=files,
                admin_password=new_pass,
                bdms=bdms,
                detach_block_devices=detach_block_devices,
                attach_block_devices=self._prep_block_device,
                block_device_info=block_device_info,
                network_info=network_info,
                preserve_ephemeral=preserve_ephemeral,
                recreate=recreate)
            try:
           
                # 这里的方法没有实现
                self.driver.rebuild(**kwargs)
            except NotImplementedError:
                # NOTE(rpodolyaka): driver doesn't provide specialized version
                # of rebuild, fall back to the default implementation

                # 这里是evacuate的真正实现调用_rebuild_default_impl
                self._rebuild_default_impl(**kwargs)
            instance.power_state = self._get_power_state(context, instance)
            instance.vm_state = vm_states.ACTIVE
            instance.task_state = None
            instance.launched_at = timeutils.utcnow()
            instance.save(expected_task_state=[task_states.REBUILD_SPAWNING])

            if orig_vm_state == vm_states.STOPPED:
                LOG.info(_LI("bringing vm to original state: '%s'"),
                         orig_vm_state, instance=instance)
                instance.vm_state = vm_states.ACTIVE
                instance.task_state = task_states.POWERING_OFF
                instance.progress = 0
                instance.save()
                self.stop_instance(context, instance)

            self._notify_about_instance_usage(
                    context, instance, "rebuild.end",
                    network_info=network_info,
                    extra_usage_info=extra_usage_info)

上面进行了共享卷的判断，cinder调用客户端进行deatch操作
```

转到rebuld_default_impl方法

```
 def _rebuild_default_impl(self, context, instance, image_meta,
                              injected_files, admin_password, bdms,
                              detach_block_devices, attach_block_devices,
                              network_info=None,
                              recreate=False, block_device_info=None,
                              preserve_ephemeral=False):
        if preserve_ephemeral:
            # The default code path does not support preserving ephemeral
            # partitions.
            raise exception.PreserveEphemeralNotSupported()

        detach_block_devices(context, bdms)

        if not recreate:
            self.driver.destroy(context, instance, network_info,
                                block_device_info=block_device_info)

        instance.task_state = task_states.REBUILD_BLOCK_DEVICE_MAPPING
        instance.save(expected_task_state=[task_states.REBUILDING])

        new_block_device_info = attach_block_devices(context, instance, bdms)

        instance.task_state = task_states.REBUILD_SPAWNING
        instance.save(
            expected_task_state=[task_states.REBUILD_BLOCK_DEVICE_MAPPING])


        # 这里其实也是通过driver的spawn方法来实现driver上的操作,完成最终实现
        self.driver.spawn(context, instance, image_meta, injected_files,
                          admin_password, network_info=network_info,
                          block_device_info=new_block_device_info)

```



#### 原虚拟机删除

当原nova-compue节点恢复后，会对evacuate的虚拟机进行删除清理


入口文件在nova/compute/manager.py中ComputeManager下的init_host方法

```
def init_host(self):
        """Initialization for a standalone compute service."""
        self.driver.init_host(host=self.host)
        context = nova.context.get_admin_context()
        instances = objects.InstanceList.get_by_host(
            context, self.host, expected_attrs=['info_cache'])

        if CONF.defer_iptables_apply:
            self.driver.filter_defer_apply_on()

        self.init_virt_events()

        try:
            # checking that instance was not already evacuated to other host
            self._destroy_evacuated_instances(context)
            for instance in instances:
                self._init_instance(context, instance)
        finally:
            if CONF.defer_iptables_apply:
                self.driver.filter_defer_apply_off()
```

再次调用self._destroy_evacuated_instances方法

```
    def _destroy_evacuated_instances(self, context):
        our_host = self.host
        filters = {'deleted': False}
        local_instances = self._get_instances_on_driver(context, filters)
        for instance in local_instances:
            if instance.host != our_host:
                if (instance.task_state in [task_states.MIGRATING,
                                            task_states.RESIZE_MIGRATING,
                                            task_states.RESIZE_MIGRATED,
                                            task_states.RESIZE_FINISH]
                    or instance.vm_state in [vm_states.RESIZED]):
                    LOG.debug('Will not delete instance as its host ('
                              '%(instance_host)s) is not equal to our '
                              'host (%(our_host)s) but its task state is '
                              '(%(task_state)s) and vm state is '
                              '(%(vm_state)s)',
                              {'instance_host': instance.host,
                               'our_host': our_host,
                               'task_state': instance.task_state,
                               'vm_state': instance.vm_state},
                              instance=instance)
                    continue
                LOG.info(_('Deleting instance as its host ('
                           '%(instance_host)s) is not equal to our '
                           'host (%(our_host)s).'),
                         {'instance_host': instance.host,
                          'our_host': our_host}, instance=instance)
                try:
                    network_info = self._get_instance_nw_info(context,
                                                              instance)
                    bdi = self._get_instance_block_device_info(context,
                                                               instance)
                    destroy_disks = not (self._is_instance_storage_shared(
                                                            context, instance))
                except exception.InstanceNotFound:
                    network_info = network_model.NetworkInfo()
                    bdi = {}
                    LOG.info(_('Instance has been marked deleted already, '
                               'removing it from the hypervisor.'),
                             instance=instance)
                    # always destroy disks if the instance was deleted
                    destroy_disks = True

                # 调用driver的destroy方法进行删除
                self.driver.destroy(context, instance,
                                    network_info,
                                    bdi, destroy_disks)
    
```

转到nova/virt/libvirt/driver.py方法

```
   def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        # 先做了关机
        self._destroy(instance)
        # 这里做了清理，包括删除虚拟机本地存储的信息，以及网络等
        self.cleanup(context, instance, network_info, block_device_info,
                     destroy_disks, migrate_data)
```

转到self.cleanup在同一个类下的方法

```
   def cleanup(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None, destroy_vifs=True):
        if destroy_vifs:
            self._unplug_vifs(instance, network_info, True)

        retry = True
        while retry:
            try:
                self.firewall_driver.unfilter_instance(instance,
                                                    network_info=network_info)
            except libvirt.libvirtError as e:
                try:
                    state = self.get_info(instance)['state']
                except exception.InstanceNotFound:
                    state = power_state.SHUTDOWN

                if state != power_state.SHUTDOWN:
                    LOG.warn(_LW("Instance may be still running, destroy "
                                 "it again."), instance=instance)
                    self._destroy(instance)
                else:
                    retry = False
                    errcode = e.get_error_code()
                    LOG.exception(_LE('Error from libvirt during unfilter. '
                                      'Code=%(errcode)s Error=%(e)s'),
                                  {'errcode': errcode, 'e': e},
                                  instance=instance)
                    reason = "Error unfiltering instance."
                    raise exception.InstanceTerminationFailure(reason=reason)
            except Exception:
                retry = False
                raise
            else:
                retry = False

        # FIXME(wangpan): if the instance is booted again here, such as the
        #                 the soft reboot operation boot it here, it will
        #                 become "running deleted", should we check and destroy
        #                 it at the end of this method?

        # NOTE(vish): we disconnect from volumes regardless
        block_device_mapping = driver.block_device_info_get_mapping(
            block_device_info)
        for vol in block_device_mapping:
            connection_info = vol['connection_info']
            disk_dev = vol['mount_device']
            if disk_dev is not None:
                disk_dev = disk_dev.rpartition("/")[2]

            if ('data' in connection_info and
                    'volume_id' in connection_info['data']):
                volume_id = connection_info['data']['volume_id']
                encryption = encryptors.get_encryption_metadata(
                    context, self._volume_api, volume_id, connection_info)

                if encryption:
                    # The volume must be detached from the VM before
                    # disconnecting it from its encryptor. Otherwise, the
                    # encryptor may report that the volume is still in use.
                    encryptor = self._get_volume_encryptor(connection_info,
                                                           encryption)
                    encryptor.detach_volume(**encryption)

            try:
                self._disconnect_volume(connection_info, disk_dev)
            except Exception as exc:
                with excutils.save_and_reraise_exception() as ctxt:
                    if destroy_disks:
                        # Don't block on Volume errors if we're trying to
                        # delete the instance as we may be partially created
                        # or deleted
                        ctxt.reraise = False
                        LOG.warn(_LW("Ignoring Volume Error on vol %(vol_id)s "
                                     "during delete %(exc)s"),
                                 {'vol_id': vol.get('volume_id'), 'exc': exc},
                                 instance=instance)

        if destroy_disks:
            # NOTE(haomai): destroy volumes if needed
            if CONF.libvirt.images_type == 'lvm':
                self._cleanup_lvm(instance)
            if CONF.libvirt.images_type == 'rbd':
                self._cleanup_rbd(instance)

        if destroy_disks or (
                migrate_data and migrate_data.get('is_shared_block_storage',
                                                  False)):
            self._delete_instance_files(instance)

        if CONF.serial_console.enabled:
            for host, port in self._get_serial_ports_from_instance(instance):
                serial_console.release_port(host=host, port=port)

        self._undefine_domain(instance)

在以上代码中进行了网络清理，卷映射清理，删除本地instance信息，undefine_domain完成最终的删除
```
