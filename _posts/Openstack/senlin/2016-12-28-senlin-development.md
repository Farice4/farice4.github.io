---
layout: post
title: Senlin Development record
date: 2016-12-13 14:32:06
description: ""
keywords: Markdown,Jekyll
categories: Openstack 
tags: [Openstack Senlin Development doc]
---

* content
{:toc}


### Senlin profile

This is about senlin development doc





> Senlin profile create

senlin profile about nova parameter in spec, senlin profile (name, type, metadata,)

> Senlin profile update

senlin support profile update, but update parameter is name or metadata

> Senlin profile delete

senlin support profile delete, but profile is not by use in cluster or nodes


### Senlin cluster

Senlin cluster support zero or more nodes in cluster, cluster nodes use same profile

Cluster support create,retrieve,update,delete opertion

> Cluster status

* INIT: the cluster object has been initialized, but not created yet;
* ACTIVE: the cluster is created and providing service;
* CREATING: the cluster creation action is still on going;
* ERROR: the cluster is still providing services, but there are things going wrong that needs human intervention;
* CRITICAL: the cluster is not operational, it may or may not be providing services as expercted.
Senlin cannot recover if from its current status, The best way to deal with cluster is to delete it and then re-create it if needed.
* DELETING: the cluster deleteion is ongoing;
* WARNING: the cluster is operational, but there are some warnings detected during past operations. In this case, human involvement is suggested but not required.
* UPDATING: the cluster is being updated.

> Cluster create

cluster create will be wait engine to complete the creation job

* desired_capacity: the desired number of nodes in the cluster, which is treated aalso as initial number of nodes to be created;
* min_size: the minimum number of nodes inside the cluster, default value is 0;
* max_size: the maxinum number of nodes inside the cluster, default value is -1, which means ther is no upper limit on the number of nodes;

> Cluster get

list cluster

> Updating a cluster

a cluster can be updated upon user is requests.

Cluster support update (name, profile_id, metadata, desired_capacity, min_size, max_size)

> Update cluster profile

When profile_id is specified, the request will be interpreted as a wholistic update to all nodes across the cluster.

> Update Cluster Size

Cluster support update cluster desired_capacity、min_size、max_size. The desired_capacity update , node number will be immediate update.

> Cluster Actions

A cluster object supports the following asynchronous actions.

* add_nodes: add a list of nodes into the target cluster;
* del_nodes: remove the specified list of nodes from the cluster;
* replace_nodes: replace the speclfied list of nodes in the cluster;
* resize: adjust the size of the cluster;
* scale_in: explictly shrink the size of the cluster;
* scale_out: explicitly enlarge the size of the cluster;
* policy_attach: attach a policy object to the cluster;
* policy_detach: detach a policy object from the cluster;
* policy_update: modify the settings of a policy that is attached to the cluster;

> Adding nodes to a cluster

Senlin API provides the add_nodes action for user to add some existing nodes into the specified cluster.

The senlin engine will examine nodes in the list one by one and see if any of the following conditions is true. Senlin engine rejects the request if so:

* Any node from the list is not in ACTIVE state ?
* Any node from the list is still member of another cluster ?
* Any node from the list is not found in the database ?
* Number of nodes to add is zero ?

In the cases where there are load-balancing policies attached to cluster, the CLUSTER_ADD_NODES action will save the list of UUIDs of the new nodes into the action is data field so that those policies clould update the associated resources.

> Deleting Nodes from a Cluster

Senlin API provides the del_nodes action for user to delete some existing nodes from the specified cluster. The parameter for this action interpreted as a list in which each item is the UUID, name or short ID of a node.

The Senlin engine will examine nodes in the list one by one and see if any of the following conditions is true. Senlin engine rejects the request if so.

* Any node from the list cannot be found from the database?
* Any node from the list is not member of the specified cluster?
* Number of nodes to delete is zero?

> Replacing Nodes in a Cluster

Senlin API support replacing existing nodes in the specified cluster.

The Senlin engine will examine nodes in the dict one by one and see if all of the following conditions is true. Senlin engine acctpts the request if so.

* All nodes from the list can be found from the database
* All replaced nodes from the list are the members of the specified cluster.
* All replacement nodes from the list are not the members of any cluster.
* The profile types of all replacement nodes match that of the specified cluster.
* The statuses of all replacement nodes are ACTIVE.

> Resize a Cluster

Senlin API support cluster resize, This operation is designed for the auto-scaling and manual-scaling use cases.

Resize parameter about (adjustment_type, number, min_size, max_size, min_step, strict)

> Scaling in/out a Cluster

As a convenience method, Selin provides the scale_out and the scale_in action API for clusters. With these two APIs, a user can request a cluster to be resized by the specified number of nodes.

The scale_out and the scale_in APIs both take a parameter named count which is a positive integer.

> Cluster Policy Bindings

Senlin API provides the following action APIs for managing the binding relationship between a cluster and a policy:

* policy_attach: attach a policy to a cluster;
* policy_detach: detach a policy from a cluster;
* policy_update: update the properties of the binding between a cluster and policy.

The policy default enable in cluster
