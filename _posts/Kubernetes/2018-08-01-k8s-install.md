---
layout: post
title: "K8S Install v1.10.0"
date: 2018-08-01 13:15:03
description: ""
category: "Kubernetes"
tags: [Kubernetes安装]
---

* content
{:toc}

---
本文主要记录通过kubeadm方式安装k8s 1.10.0版本，本文档既适用于单节点安装也适用于集群安装，网络方案采用fannel插件。





### 安装前环境准备
> 关闭防火墙firewalld

```
systemctl stop firewalld
systemctl disable firewalld
```

> 禁用Selinux

```
setenforce 0  (临时关闭)
```
vi 打开/etc/sysconfig/selinux文件，修改SELINUX值（永久关闭)

```
SELINUX=disabled
```

> 关闭swap交换分区
```
swapoff -a (临时关闭)
```

vi 打开/etc/fstab文件，将挂载swap分区注释掉（永久关闭)

```
#UUID=2276f4dc-8b29-41bf-8aed-573c93e41976 swap                    swap    defaults        0 0
```

以上配置完成后，重启操作系统

### 安装docker ce软件

下载地址：https://download.docker.com/linux/centos/7/x86_64/stable/Packages/

> 下载的版本选择17.03.2.

```
mkdir docker_rpm
cd docker_rpm
wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-selinux-17.03.2.ce-1.el7.centos.noarch.rpm
wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-17.03.2.ce-1.el7.centos.x86_64.rpm

```

> 执行docker安装
```
yum install -y ./docker-ce-selinux-17.03.2.ce-1.el7.centos.noarch.rpm
yum install -y ./docker-ce-17.03.2.ce-1.el7.centos.x86_64.rpm
```
> 启动docker服务

```
systemctl enable docker
systemctl start docker
```

> 配置docker registry mirror与cgroup
编辑/etc/docker/daemon.json文件
```
{"registry-mirrors": ["http://85d5449d.m.daocloud.io"],"exec-opts": ["native.cgroupdriver=systemd"]}
```

> 重启docker服务，验证cgroup配置成功

```
systemctl restart docker
docker info  (能够看到显示的cgroup为systemd)
```

### 安装kubeadm, kubelet, kubectl软件

这里安装1.10.0版本

> 配置kubernetes yum安装源

```
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
EOF
yum -y install epel-release
yum clean all
```

> 安装kubeadm, kubelet, kubectl软件

```
yum install kubeadm-1.10.0 kubectl-1.10.0 kubelet-1.10.0
systemctl enable kubelet && systemctl start kubelet
```

### 配置1.10.0版本所需要镜像

因k8s默认从google storage上下载镜像，国内无法正常下载，因此手动将镜像先下载下来，通过一个脚本进行下载，并对镜像打上相应tag。

在image.sh文件中添加以下内容:
```
#!/bin/bash
images=(kube-proxy-amd64:v1.10.0 kube-scheduler-amd64:v1.10.0 kube-controller-manager-amd64:v1.10.0 kube-apiserver-amd64:v1.10.0
etcd-amd64:3.1.12 pause-amd64:3.1 kubernetes-dashboard-amd64:v1.8.3 k8s-dns-sidecar-amd64:1.14.8 k8s-dns-kube-dns-amd64:1.14.8
k8s-dns-dnsmasq-nanny-amd64:1.14.8)
for imageName in ${images[@]} ; do
  docker pull mirrorgooglecontainers/$imageName
  docker tag mirrorgooglecontainers/$imageName k8s.gcr.io/$imageName
  docker rmi mirrorgooglecontainers/$imageName
done
```
运行image.sh下载镜像

```
sh image.sh
```

### 初始化master节点

```
kubeadm init --kubernetes-version=v1.10.0 --apiserver-advertise-address 192.168.53.10 --pod-network-cidr=10.244.0.0/16
```

解释：

* --kubernetes-version                   指的是相关这里使用的版本是1.10.0

* --apiserver-advertise-address     如果该Master节点有多网卡则需要指定，如果不指定，kubeadm 会自动选择有默认网关的 interface。

* --pod-network-cidr             指定 Pod 网络的范围。Kubernetes 支持多种网络方案，而且不同网络方案对 --pod-network-cidr 有自己的要求，这里设置为 10.244.0.0/16 是因为我们将使用 flannel 网络方案，必须设置成这个 CIDR

以下内容是初始化成功后输出的截取内容：

```
Your Kubernetes master has initialized successfully!
To start using your cluster, you need to run the following as a regular user:
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
https://kubernetes.io/docs/concepts/cluster-administration/addons/
You can now join any number of machines by running the following on each node
as root:
kubeadm join 192.168.53.10:6443 --token mjcpfv.ygwck7pjyue68fw9 --discovery-token-ca-cert-hash sha256:6c31a69d3bfa45a5dd50de2e07f1c71731d17244a009742a3dbf83e03a5a62f6

```

其它节点根据上面相同的方式执行，非master节点不需要执行`kubeadm init`操作，只需要执行`kubeadm join`操作

末尾的：
```
kubeadm join 192.168.53.10:6443 --token mjcpfv.ygwck7pjyue68fw9 --discovery-token-ca-cert-hash sha256:6c31a69d3bfa45a5dd50de2e07f1c71731d17244a009742a3dbf83e03a5a62f6
```
可以用来在其他Node节点上执行，以将其他节点加入到集群中。

### 配置kubectl认证信息

cp /etc/kubernetes/admin.conf ~/.kube/config

### 安装flannel网络

```
mkdir -p /etc/cni/net.d/

cat <<EOF> /etc/cni/net.d/10-flannel.conf
{
"name": "cbr0",
"type": "flannel",
"delegate": {
"isDefaultGateway": true
}
}
EOF

mkdir /usr/share/oci-umount/oci-umount.d -p

mkdir /run/flannel/

cat <<EOF> /run/flannel/subnet.env
FLANNEL_NETWORK=10.244.0.0/16
FLANNEL_SUBNET=10.244.1.0/24
FLANNEL_MTU=1450
FLANNEL_IPMASQ=true
EOF

```
应用fannel插件yml文件,创建fannel pod

```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

### 验证k8s环境安装

> 检测节点状态，节点状态为Ready，表示正常
```
kubectl get nodes
NAME                   STATUS    ROLES     AGE       VERSION
k8s-master-openstack   Ready     master    3h        v1.10.0
k8s-node1-openstack    Ready     <none>    3h        v1.10.0
k8s-node2-openstack    Ready     <none>    3h        v1.10.0
```

> 检测pod运行状态

```
kubectl get pods --all-namespaces -o wide
NAMESPACE     NAME                                           READY     STATUS    RESTARTS   AGE       IP              NODE
default       cirros-66995cfc6c-pf4b5                        1/1       Running   0          37m       10.244.1.2      k8s-node1-openstack
kube-system   etcd-k8s-master-openstack                      1/1       Running   0          46m       192.168.8.180   k8s-master-openstack
kube-system   kube-apiserver-k8s-master-openstack            1/1       Running   0          46m       192.168.8.180   k8s-master-openstack
kube-system   kube-controller-manager-k8s-master-openstack   1/1       Running   0          46m       192.168.8.180   k8s-master-openstack
kube-system   kube-dns-86f4d74b45-kjrx9                      3/3       Running   8          46m       10.244.1.2      k8s-node2-openstack
kube-system   kube-flannel-ds-amd64-6ssxl                    1/1       Running   0          42m       192.168.8.115   k8s-node1-openstack
kube-system   kube-flannel-ds-amd64-btltw                    1/1       Running   0          42m       192.168.8.180   k8s-master-openstack
kube-system   kube-flannel-ds-amd64-gszwd                    1/1       Running   0          42m       192.168.8.67    k8s-node2-openstack
kube-system   kube-proxy-6hm4l                               1/1       Running   0          45m       192.168.8.115   k8s-node1-openstack
kube-system   kube-proxy-c2n8z                               1/1       Running   0          46m       192.168.8.180   k8s-master-openstack
kube-system   kube-proxy-tkn6v                               1/1       Running   0          45m       192.168.8.67    k8s-node2-openstack
kube-system   kube-scheduler-k8s-master-openstack            1/1       Running   0          46m       192.168.8.180   k8s-master-openstack
```

> 创建cirros 镜像pod测试

```
kubectl run cirros --image=cirros
```

> 查看创建结果

```
kubectl get pods
NAME                      READY     STATUS    RESTARTS   AGE
cirros-66995cfc6c-pf4b5   1/1       Running   0          3h
```