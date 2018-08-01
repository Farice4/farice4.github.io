---
layout: post
title: Nova Soft Delete and Restore
date: 2016-10-27 16:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Nova SoftDelete]
---

* content
{:toc}

#### 介绍

Soft Delete
假删除，用户在配置的时间内可恢复。通过配置nova.conf中reclaim_instance_interval，启用Nova 软删除，底层将虚拟机假删除置为关机状态，只是在这个过程中删除了租户对quota配额的占用。reclaim_instance_interval时间到达后执行真正的物理上删除，删除后不可在恢复





Delete
虚拟机物理删除，无法进行恢复

Restore
租户在reclaim_instance_interval时间内执行的恢复操作，恢复后云主机处于ACTIVE状态，底层执行了libvirt hard_reboot操作，除在启动过程中
出现的启动错误外，启动完成后云主机都处于ACTIVE状态

#### Soft Delete 代码分析

代码入口位置在nova/api/openstack/compute/servers.py中Controller类下

```
 def delete(self, req, id):
        """Destroys a server."""
        try:

            # SoftDelete与Delete入口都是同一个位置，去调用 self._delete执行删除操作
            self._delete(req.environ['nova.context'], req, id)        
        except exception.NotFound:
            msg = _("Instance could not be found")
            raise exc.HTTPNotFound(explanation=msg)
        except exception.InstanceIsLocked as e:
            raise exc.HTTPConflict(explanation=e.format_message())
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(state_error,
                    'delete')

```

同一个类下面self._delete函数


```

def _delete(self, context, req, instance_uuid):
        instance = self._get_server(context, req, instance_uuid)
   
        # 判断是否启用了reclaim_instance_interval配置在nova.conf中
        if CONF.reclaim_instance_interval:                  
            try:
                # 这里开始调用nova/compute/api.py 中的API类下面的soft_delete函数
                self.compute_api.soft_delete(context, instance) 
            except exception.InstanceInvalidState:
                # Note(yufang521247): instance which has never been active
                # is not allowed to be soft_deleted. Thus we have to call
                # delete() to clean up the instance.
                self.compute_api.delete(context, instance)
        else:
            # 这里调用的delete，也就是永久删除,同样位于soft_delete的同一个类下
            self.compute_api.delete(context, instance)

```

下面来看nova/compute/api.py中API类的soft_delete方法


```
 def soft_delete(self, context, instance):
        """Terminate an instance."""
        LOG.debug('Going to try to soft delete instance',
                  instance=instance)
        if instance['vm_state'] == vm_states.SOFT_DELETED:
            LOG.warn("Instance %s is soft delete state" % (instance.uuid))
            reason = ("The instance is %s state" % (instance.vm_state))
            raise exception.InstanceTerminationFailure(reason=reason)
        else:
            self._delete(context, instance, 'soft_delete',
                         # 开始调用nova compute的soft delete操作
                         self._do_soft_delete,                
                         # 开始任务状态soft_delete状态
                         task_state=task_states.SOFT_DELETING, 
                         # 设置deleted_at的时间
                         deleted_at=timeutils.utcnow()) 
```


下面先看下 self._do_soft_delete 同样在上面API类下

```
def _do_soft_delete(self, context, instance, bdms, reservations=None,
                        local=False):
        if local:
            instance.vm_state = vm_states.SOFT_DELETED
            instance.task_state = None
            instance.terminated_at = timeutils.utcnow()
            instance.save()
        else:
            # 通过rpc调用compute下的soft_delete_instance
            self.compute_rpcapi.soft_delete_instance(context, instance,
                                                     reservations=reservations)
```

转到nova/compute/manager.py中的类ComputeManager下的soft_delete_instance方法

```
  def soft_delete_instance(self, context, instance, reservations):
        """Soft delete an instance on this host."""

        # 获取配额instance的规格信息
        quotas = objects.Quotas.from_reservations(context,
                                                  reservations,
                                                  instance=instance)
        try:
            self._notify_about_instance_usage(context, instance,
                                              "soft_delete.start")
            try:
                
                # 这里开始调用nova/virt/libvirt/driver.py中的soft_delete方法进行软删除
                # 但是driver.py中并没有实现soft_delete方法,因此触发except调用power_off
                self.driver.soft_delete(instance)
            except NotImplementedError:
                # Fallback to just powering off the instance if the
                # hypervisor doesn't implement the soft_delete method
                
                # 目前版本真正实现的soft_delete方法就是power_off
                self.driver.power_off(instance)
            current_power_state = self._get_power_state(context, instance)
            instance.power_state = current_power_state
            instance.vm_state = vm_states.SOFT_DELETED
            instance.task_state = None
            instance.save(expected_task_state=[task_states.SOFT_DELETING])
        except Exception:
            with excutils.save_and_reraise_exception():
                quotas.rollback()

        # 提交quotas更新
        quotas.commit()
        self._notify_about_instance_usage(context, instance, "soft_delete.end")

```

下面看下nova/virt/libvirt/driver.py中的power_off方法

```
def power_off(self, instance, timeout=0, retry_interval=0):
        """Power off the specified instance."""
     
        if timeout:
            # 这里执行clean_shutdown方法
            self._clean_shutdown(instance, timeout, retry_interval)
        
        self._destroy(instance)

```

下面看一下clean_shutdown方法

```
  def _clean_shutdown(self, instance, timeout, retry_interval):

        # List of states that represent a shutdown instance
        SHUTDOWN_STATES = [power_state.SHUTDOWN,
                           power_state.CRASHED]

        try:
            `# 获取instance name`
            dom = self._lookup_by_name(instance["name"])
        except exception.InstanceNotFound:
            # If the instance has gone then we don't need to
            # wait for it to shutdown
            return True

        (state, _max_mem, _mem, _cpus, _t) = dom.info()
        state = LIBVIRT_POWER_STATE[state]
        if state in SHUTDOWN_STATES:
            LOG.info(_LI("Instance already shutdown."),
                     instance=instance)
            return True

        LOG.debug("Shutting down instance from state %s", state,
                  instance=instance)

        # 这里调用了virsh底层的shutdown关机,可以参考virsh的相关命令
        dom.shutdown()
        retry_countdown = retry_interval

        for sec in six.moves.range(timeout):

            dom = self._lookup_by_name(instance["name"])
            (state, _max_mem, _mem, _cpus, _t) = dom.info()
            state = LIBVIRT_POWER_STATE[state]

            if state in SHUTDOWN_STATES:
                LOG.info(_LI("Instance shutdown successfully after %d "
                              "seconds."), sec, instance=instance)
                return True

            if retry_countdown == 0:
                retry_countdown = retry_interval
                # Instance could shutdown at any time, in which case we
                # will get an exception when we call shutdown
                try:
                    LOG.debug("Instance in state %s after %d seconds - "
                              "resending shutdown", state, sec,
                              instance=instance)
                    dom.shutdown()
                except libvirt.libvirtError:
                    # Assume this is because its now shutdown, so loop
                    # one more time to clean up.
                    LOG.debug("Ignoring libvirt exception from shutdown "
                              "request.", instance=instance)
                    continue
            else:
                retry_countdown -= 1

            time.sleep(1)

        LOG.info(_LI("Instance failed to shutdown in %d seconds."),
                 timeout, instance=instance)
        return False

```

#### restore 恢复soft_delete删除代码分析

先看入口文件nova/api/openstack/compute/contrib/deferred_delete.py中的类DeferredDeleteController下的_restore方法

```
  def _restore(self, req, id, body):
        """Restore a previously deleted instance."""
        context = req.environ["nova.context"]
        authorize(context)
        instance = common.get_instance(self.compute_api, context, id,
                                       want_objects=True)

        try:
            # 这里调用了nova/compute/api.py中的restore方法
            self.compute_api.restore(context, instance)
        except exception.QuotaError as error:
            raise webob.exc.HTTPForbidden(explanation=error.format_message())
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(state_error,
                    'restore')
        return webob.Response(status_int=202)


```

转到nova/compute/api.py类API下的restore方法

```
   def restore(self, context, instance):
        """Restore a previously deleted (but not reclaimed) instance."""
        # Reserve quotas
        flavor = instance.get_flavor()
        num_instances, quotas = self._check_num_instances_quota(
                context, flavor, 1, 1)

        self._record_action_start(context, instance, instance_actions.RESTORE)

        try:
            if instance.host:
                instance.task_state = task_states.RESTORING
                instance.deleted_at = None
                instance.save(expected_task_state=[None])
                
                # 这里使用rpc调用restore_instance方法,nova 中很多都是通过nova/compute/rpcapi.py
                # 实现的具体调用方法,最终去调用scheduler，compute等
                self.compute_rpcapi.restore_instance(context, instance)
            else:
                instance.vm_state = vm_states.ACTIVE
                instance.task_state = None
                instance.deleted_at = None
                instance.save(expected_task_state=[None])

            quotas.commit()
        except Exception:
            with excutils.save_and_reraise_exception():
                quotas.rollback()
```

转到nova/compute/manager.py类ComputeManager下的restore_instance方法

```
    def restore_instance(self, context, instance):
        """Restore a soft-deleted instance on this host."""
        self._notify_about_instance_usage(context, instance, "restore.start")
        try:
            # 这里调用virt/libvirt/driver.py中的restore方法,但是与上面软删除一样driver.py中
            # 并没有实现restore方法，因此调用了power_on方法
            self.driver.restore(instance)
        except NotImplementedError:
            
            # 最终调用了这里的power_on方法
            self._power_on(context, instance)
        current_power_state = self._get_power_state(context, instance)
        instance.power_state = current_power_state
        instance.vm_state = vm_states.ACTIVE
        instance.task_state = None
        instance.save(expected_task_state=task_states.RESTORING)
        self._notify_about_instance_usage(context, instance, "restore.end")

```

转到nova/virt/libvirt/driver.py中的类LibvirtDriver下的power_on方法

```
    def power_on(self, context, instance, network_info,
                 block_device_info=None):
        """Power on the specified instance."""
        # We use _hard_reboot here to ensure that all backing files,
        # network, and block device connections, etc. are established
        # and available before we attempt to start the instance.
        # 这里调用了driver.py下的_har_reboot硬重启，重启过程中做了很多操作
        self._hard_reboot(context, instance, network_info, block_device_info)

```

转到_hard_reboot方法

```
   def _hard_reboot(self, context, instance, network_info,
                     block_device_info=None):
        """Reboot a virtual machine, given an instance reference.

        Performs a Libvirt reset (if supported) on the domain.

        If Libvirt reset is unavailable this method actually destroys and
        re-creates the domain to ensure the reboot happens, as the guest
        OS cannot ignore this action.

        If xml is set, it uses the passed in xml in place of the xml from the
        existing domain.
        """
        
        # 这里先调用了_destroy来执行关机
        self._destroy(instance)

        # Get the system metadata from the instance
        system_meta = utils.instance_sys_meta(instance)

        # Convert the system metadata to image metadata
        image_meta = utils.get_image_from_system_metadata(system_meta)
        if not image_meta:
            image_ref = instance.get('image_ref')
            image_meta = compute_utils.get_image_metadata(context,
                                                          self._image_api,
                                                          image_ref,
                                                          instance)

        disk_info = blockinfo.get_disk_info(CONF.libvirt.virt_type,
                                            instance,
                                            block_device_info,
                                            image_meta)
        # NOTE(vish): This could generate the wrong device_format if we are
        #             using the raw backend and the images don't exist yet.
        #             The create_images_and_backing below doesn't properly
        #             regenerate raw backend images, however, so when it
        #             does we need to (re)generate the xml after the images
        #             are in place.
        xml = self._get_guest_xml(context, instance, network_info, disk_info,
                                  image_meta=image_meta,
                                  block_device_info=block_device_info,
                                  write_to_disk=True)

        # NOTE (rmk): Re-populate any missing backing files.
        disk_info_json = self._get_instance_disk_info(instance['name'], xml,
                                                      block_device_info)
        instance_dir = libvirt_utils.get_instance_path(instance)
        self._create_images_and_backing(context, instance, instance_dir,
                                        disk_info_json)

        # Initialize all the necessary networking, block devices and
        # start the instance.
        
        self._create_domain_and_network(context, xml, instance, network_info,
                                        block_device_info, reboot=True,
                                        vifs_already_plugged=True)
        self._prepare_pci_devices_for_use(
            pci_manager.get_instance_pci_devs(instance, 'all'))

        def _wait_for_reboot():
            """Called at an interval until the VM is running again."""
            state = self.get_info(instance)['state']

            if state == power_state.RUNNING:
                LOG.info(_LI("Instance rebooted successfully."),
                         instance=instance)
                raise loopingcall.LoopingCallDone()

        timer = loopingcall.FixedIntervalLoopingCall(_wait_for_reboot)
        timer.start(interval=0.5).wait()

# 通过代码可以看出来，这里与Nova boot一样都进行了get_guest_xml创建
# 获取后端磁盘存储信息，调用_create_domain_and_network来最终实现了虚拟机的构建
```


#### 虚拟机强制删除代码分析

先看入口文件nova/api/openstack/compute/contrib/deferred_delete.py中的类DeferredDeleteController下的_force_delete方法

```
    def _force_delete(self, req, id, body):
        """Force delete of instance before deferred cleanup."""
        context = req.environ["nova.context"]
        authorize(context)
        instance = common.get_instance(self.compute_api, context, id,
                                       want_objects=True)

        try:
            # 这里同样去调用nova/compute/api.py中的force_delete方法
            self.compute_api.force_delete(context, instance)
        except exception.InstanceIsLocked as e:
            raise webob.exc.HTTPConflict(explanation=e.format_message())
        return webob.Response(status_int=202)
```

转到nova/compute/api.py中的force_delete方法

```
    def force_delete(self, context, instance):
        """Force delete an instance in any vm_state/task_state."""
        # 调用了同一类下的_delete_instance方法
        self._delete_instance(context, instance)
```

转到_delete_instance方法

```
    def _delete_instance(self, context, instance):
        # 这里调用了_delete，同时将self._do_delete传递了进去
        self._delete(context, instance, 'delete', self._do_delete,
                     task_state=task_states.DELETING)
```

先看_do_delete方法

```
   def _do_delete(self, context, instance, bdms, reservations=None,
                   local=False):
        if local:
            instance.vm_state = vm_states.DELETED
            instance.task_state = None
            instance.terminated_at = timeutils.utcnow()
            instance.save()
        else:
            # 重点这个地方开始调用rpc方式去调用nova/compute/manager.py下的terminate_instance方法
            self.compute_rpcapi.terminate_instance(context, instance, bdms,
                                                   reservations=reservations)
```

转到nova/compute/manager.py中的terminate_instance方法

```
   def terminate_instance(self, context, instance, bdms, reservations):
        """Terminate an instance on this host."""
        if (bdms and
            any(not isinstance(bdm, obj_base.NovaObject)
                for bdm in bdms)):
            bdms = objects.BlockDeviceMappingList.get_by_instance_uuid(
                    context, instance.uuid)

        quotas = objects.Quotas.from_reservations(context,
                                                  reservations,
                                                  instance=instance)

        @utils.synchronized(instance['uuid'])
        def do_terminate_instance(instance, bdms):
            try:
                # 具体的实现由这里来调用
                self._delete_instance(context, instance, bdms, quotas)
            except exception.InstanceNotFound:
                LOG.info(_("Instance disappeared during terminate"),
                         instance=instance)
            except Exception:
                # As we're trying to delete always go to Error if something
                # goes wrong that _delete_instance can't handle.
                with excutils.save_and_reraise_exception():
                    LOG.exception(_LE('Setting instance vm_state to ERROR'),
                                  instance=instance)
                    self._set_instance_error_state(context, instance)

        do_terminate_instance(instance, bdms)

```

转到self._delete_instance方法

```
    def _delete_instance(self, context, instance, bdms, quotas):
        instance_uuid = instance['uuid']

        was_soft_deleted = instance['vm_state'] == vm_states.SOFT_DELETED
        if was_soft_deleted:
            # Instances in SOFT_DELETED vm_state have already had quotas
            # decremented.
            try:
                quotas.rollback()
            except Exception:
                pass

        try:
            events = self.instance_events.clear_events_for_instance(instance)
            if events:
                LOG.debug('Events pending at deletion: %(events)s',
                          {'events': ','.join(events.keys())},
                          instance=instance)
            instance.info_cache.delete()
            self._notify_about_instance_usage(context, instance,
                                              "delete.start")
            # 重点在_shutdown_instance方法调用
            self._shutdown_instance(context, instance, bdms)
            # 完成虚拟机删除后，会进行卷清理
            self._cleanup_volumes(context, instance_uuid, bdms,
                    raise_exc=False)
            # if a delete task succeed, always update vm state and task
            # state without expecting task state to be DELETING
            instance.vm_state = vm_states.DELETED
            instance.task_state = None
            instance.terminated_at = timeutils.utcnow()
            instance.save()
            self._update_resource_tracker(context, instance)
            system_meta = instance.system_metadata
            instance.destroy()
        except Exception:
            with excutils.save_and_reraise_exception():
                quotas.rollback()

        self._complete_deletion(context,
                                instance,
                                bdms,
                                quotas,
                                system_meta)

```

转到_shutdown_instance

```
   def _shutdown_instance(self, context, instance,
                           bdms, requested_networks=None, notify=True,
                           try_deallocate_networks=True):
        context = context.elevated()
        LOG.audit(_('%(action_str)s instance') % {'action_str': 'Terminating'},
                  context=context, instance=instance)

        if notify:
            self._notify_about_instance_usage(context, instance,
                                              "shutdown.start")

        network_info = compute_utils.get_nw_info_for_instance(instance)

        # NOTE(vish) get bdms before destroying the instance
        vol_bdms = [bdm for bdm in bdms if bdm.is_volume]
        block_device_info = self._get_instance_block_device_info(
            context, instance, bdms=bdms)

        # NOTE(melwitt): attempt driver destroy before releasing ip, may
        #                want to keep ip allocated for certain failures
        try:
            # 最终由这个地方进行了virt/libvirt/driver.py中的destroy方法执行
            self.driver.destroy(context, instance, network_info,
                    block_device_info)
        except exception.InstancePowerOffFailure:
            # if the instance can't power off, don't release the ip
            with excutils.save_and_reraise_exception():
                pass
        except Exception:
            with excutils.save_and_reraise_exception():
                # deallocate ip and fail without proceeding to
                # volume api calls, preserving current behavior
                if try_deallocate_networks:
                    self._try_deallocate_network(context, instance,
                                                 requested_networks)

        if try_deallocate_networks:
            self._try_deallocate_network(context, instance, requested_networks)

        for bdm in vol_bdms:
            try:
                # NOTE(vish): actual driver detach done in driver.destroy, so
                #             just tell cinder that we are done with it.
                connector = self.driver.get_volume_connector(instance)
                self.volume_api.terminate_connection(context,
                                                     bdm.volume_id,
                                                     connector)
                self.volume_api.detach(context, bdm.volume_id)
            except exception.DiskNotFound as exc:
                LOG.debug('Ignoring DiskNotFound: %s', exc,
                          instance=instance)
            except exception.VolumeNotFound as exc:
                LOG.debug('Ignoring VolumeNotFound: %s', exc,
                          instance=instance)
            except cinder_exception.EndpointNotFound as exc:
                LOG.warn(_LW('Ignoring EndpointNotFound: %s'), exc,
                             instance=instance)

        if notify:
            self._notify_about_instance_usage(context, instance,
                                              "shutdown.end")
```

转到nova/virt/libvirt/driver.py类LibvirtDriver下的destroy方法

```
   def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):

        # 执行虚拟机关机操作
        self._destroy(instance)
        # 执行虚拟机清理操作，主要看下清理操作
        self.cleanup(context, instance, network_info, block_device_info,
                     destroy_disks, migrate_data)
```

转到虚拟机的cleanup操作

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

        # 实现清理操作在_undefine_domain这个方法的调用
        self._undefine_domain(instance)
```

转到driver.py下的_undefine_domain方法

```
   def _undefine_domain(self, instance):
        try:
            virt_dom = self._lookup_by_name(instance['name'])
        except exception.InstanceNotFound:
            virt_dom = None
        if virt_dom:
            try:
                try:
                    virt_dom.undefineFlags(
                        libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE)
                except libvirt.libvirtError:
                    LOG.debug("Error from libvirt during undefineFlags."
                        " Retrying with undefine", instance=instance)
                    virt_dom.undefine()
                except AttributeError:
                    # NOTE(vish): Older versions of libvirt don't support
                    #             undefine flags, so attempt to do the
                    #             right thing.
                    try:
                        if virt_dom.hasManagedSaveImage(0):
                            virt_dom.managedSaveRemove(0)
                    except AttributeError:
                        pass
                    # 这里由virsh底层实现了undefine，可参考virsh相关命令
                    virt_dom.undefine()
            except libvirt.libvirtError as e:
                with excutils.save_and_reraise_exception():
                    errcode = e.get_error_code()
                    LOG.error(_LE('Error from libvirt during undefine. '
                                  'Code=%(errcode)s Error=%(e)s'),
                              {'errcode': errcode, 'e': e}, instance=instance)

```

回到上面的nova/compute/api.py中的_delete_instance中的 self._delete调用

```
   def _delete(self, context, instance, delete_type, cb, **instance_attrs):
        if instance.disable_terminate:
            LOG.info(_('instance termination disabled'),
                     instance=instance)
            return

        host = instance['host']
        bdms = objects.BlockDeviceMappingList.get_by_instance_uuid(
                context, instance.uuid)

        project_id, user_id = quotas_obj.ids_from_instance(context, instance)

        # At these states an instance has a snapshot associate.
        if instance['vm_state'] in (vm_states.SHELVED,
                                    vm_states.SHELVED_OFFLOADED):
            snapshot_id = instance.system_metadata.get('shelved_image_id')
            LOG.info(_("Working on deleting snapshot %s "
                       "from shelved instance..."),
                     snapshot_id, instance=instance)
            try:
                self.image_api.delete(context, snapshot_id)
            except (exception.ImageNotFound,
                    exception.ImageNotAuthorized) as exc:
                LOG.warning(_("Failed to delete snapshot "
                              "from shelved instance (%s)."),
                            exc.format_message(), instance=instance)
            except Exception as exc:
                LOG.exception(_LE("Something wrong happened when trying to "
                                  "delete snapshot from shelved instance."),
                              instance=instance)

        original_task_state = instance.task_state
        quotas = None
        try:
            # NOTE(maoy): no expected_task_state needs to be set
            instance.update(instance_attrs)
            instance.progress = 0
            instance.save()

            # NOTE(comstud): If we delete the instance locally, we'll
            # commit the reservations here.  Otherwise, the manager side
            # will commit or rollback the reservations based on success.
            quotas = self._create_reservations(context,
                                               instance,
                                               original_task_state,
                                               project_id, user_id)

            if self.cell_type == 'api':
                # NOTE(comstud): If we're in the API cell, we need to
                # skip all remaining logic and just call the callback,
                # which will cause a cast to the child cell.  Also,
                # commit reservations here early until we have a better
                # way to deal with quotas with cells.
                cb(context, instance, bdms, reservations=None)
                quotas.commit()
                return

            if not host:
                try:
                    compute_utils.notify_about_instance_usage(
                            self.notifier, context, instance,
                            "%s.start" % delete_type)
                    instance.destroy()
                    compute_utils.notify_about_instance_usage(
                            self.notifier, context, instance,
                            "%s.end" % delete_type,
                            system_metadata=instance.system_metadata)
                    quotas.commit()
                    return
                except exception.ObjectActionError:
                    instance.refresh()

            if instance.vm_state == vm_states.RESIZED:
                self._confirm_resize_on_deleting(context, instance)

            is_up = False
            try:
                service = objects.Service.get_by_compute_host(
                    context.elevated(), instance.host)
                if self.servicegroup_api.service_is_up(service):
                    is_up = True

                    if original_task_state in (task_states.DELETING,
                                                  task_states.SOFT_DELETING):
                        LOG.info(_('Instance is already in deleting state, '
                                   'ignoring this request'), instance=instance)
                        quotas.rollback()
                        return

                    self._record_action_start(context, instance,
                                              instance_actions.DELETE)

                    cb(context, instance, bdms,
                       reservations=quotas.reservations)
            except exception.ComputeHostNotFound:
                pass

            if not is_up:
                # If compute node isn't up, just delete from DB
                self._local_delete(context, instance, bdms, delete_type, cb)
                quotas.commit()

        except exception.InstanceNotFound:
            # NOTE(comstud): Race condition. Instance already gone.
            if quotas:
                quotas.rollback()
        except Exception:
            with excutils.save_and_reraise_exception():
                if quotas:
                    quotas.rollback()

# 这个里面主要是做一些检测，如果检测不能通过，那么quota回滚删除失败
```

对于nova/compute/manager.py中的_delete_instance中的self._cleanup_volumes调用其，最终涉及到cinder的api的调用

```
self._cleanup_volumes(context, instance_uuid, bdms,
                    raise_exc=False)
```

转到cleanup_volume的具体实现

```
def _cleanup_volumes(self, context, instance_uuid, bdms, raise_exc=True):
        exc_info = None

        for bdm in bdms:
            LOG.debug("terminating bdm %s", bdm,
                      instance_uuid=instance_uuid)
            if bdm.volume_id and bdm.delete_on_termination:
                try:
                    # 这个地方来实现volume_api的调用
                    self.volume_api.delete(context, bdm.volume_id)
                except Exception as exc:
                    exc_info = sys.exc_info()
                    LOG.warn(_LW('Failed to delete volume: %(volume_id)s due '
                                 'to %(exc)s'), {'volume_id': bdm.volume_id,
                                                  'exc': unicode(exc)})
        if exc_info is not None and raise_exc:
            six.reraise(exc_info[0], exc_info[1], exc_info[2])
```

volume_api是` self.volume_api = volume.API()` 因此调用的delete其最终也就是在volume.API中
默认为`default='nova.volume.cinder.API'`


nova/volume/cinder.py中类API下的delete方法如下：

```
   def delete(self, context, volume_id):
        cinderclient(context).volumes.delete(volume_id)

```
