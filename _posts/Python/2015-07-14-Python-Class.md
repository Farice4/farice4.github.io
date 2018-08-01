---
layout: post
title: "Python 类的多重继承"
date: 2015-07-14 21:05:12
description: ""
categories: "Python"
tags: [类的多重继承]
---

* content
{:toc}

python和C++一样，支持多继承。概念虽然容易，但是困难的工作是如果子类调用一个自身没有定义的属性，它是按照何种顺序去到父类寻找呢，尤其是众多父类中有多个都包含该同名属性。

对经典类和新式类来说，属性的查找顺序是不同的。现在我们分别看一下经典类和新式类两种不同的表现：





#### 经典类

```
#! /usr/bin/python
# -*- coding:utf-8 -*-

class P1():
    def foo(self):
        print 'p1-foo'

class P2():
    def foo(self):
        print 'p2-foo'
    def bar(self):
        print 'p2-bar'

class C1(P1,P2):
    pass

class C2(P1,P2):
    def bar(self):
        print 'C2-bar'

class D(C1,C2):
    pass


if __name__ =='__main__':
    d=D()
    d.foo()
    d.bar()
执行的结果：
p1-foo
p2-bar

```
![class](/assets/images/201507/class_duo1.png)

从上面经典类的输出结果来看：

实例d调用foo()时，搜索顺序是D=>C1=>P1

实例d调用bar()时，搜索顺序是D=>C1=>P1=>P2

> 总结：经典类的搜索方式是按照“从左至右，深度优先”的方式查找属性。d先查找自身是否有foo方法，没有则查找最近的父类C1里是否有该方法，如果没有则继续向上查找，直到在P1中找到该方法，查找结束。

新式类：

```
#! /usr/bin/python
# -*- coding:utf-8 -*-

class P1(object):
    def foo(self):
        print 'p1-foo'
        
class P2(object):
    def foo(self):
        print 'p2-foo'
    def bar(self):
        print 'p2-bar'
        
class C1(P1,P2):
    pass
    
class C2(P1,P2):
    def bar(self):
        print 'C2-bar'
        
class D(C1,C2):
    pass 
    

if __name__ =='__main__':
    print D.__mro__   #只有新式类有__mro__属性，告诉查找顺序是怎样的
    d=D()
    d.foo()
    d.bar()
执行结果：
(<class '__main__.D'>, <class '__main__.C1'>, <class '__main__.C2'>, <class '__main__.P1'>, <class '__main__.P2'>, <type 'object'>)

p1-foo
C2-bar
```
> 从上面新式类的输出结果来看，

实例d调用foo()时，搜索顺序是D=>C1=>C2=>P1

实例d调用bar()时，搜索顺序是D=>C1=C2

总结：新式类的搜索方式是采用“广度优先”的方式去查找属性。


