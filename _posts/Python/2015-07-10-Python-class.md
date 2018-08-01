---
layout: post
title: "Python Class类的使用"
date: 2015-07-10 10:05:04
description: ""
categories: "Python"
tags: [Class 类的使用]
---

* content
{:toc}

### Python中的Class

尽管Python在Function Programming中有着其他语言难以企及的的优势，但是我们也不要忘了Python也是一门OO语言哦。因此我们关注Python在FP上的优势的同时，还得了解一下Python在OO方面的特性。
要讨论Python的OO特性，了解Python中的Class自然是首当其冲了。在Python中定义class和创建对象实例都很简单，具体代码如下：




复制代码

```
class GrandPa:
    def __init__(self):
        print('I\'m GrandPa')
  
  
class Father(GrandPa):
    def __init__(self):
        print('I\'m Father!')
  
class Son(Father):
   """A simple example class"""
   i = 12345
   def __init__(self):
       print('这是构造函数,son')
   def sayHello(self):
       return 'hello world'
 
if __name__ == '__main__':
    son = Son()
    # 类型帮助信息 
    print('类型帮助信息: ',Son.__doc__)
    #类型名称
    print('类型名称:',Son.__name__)
    #类型所继承的基类
    print('类型所继承的基类:',Son.__bases__)
    #类型字典
    print('类型字典:',Son.__dict__)
    #类型所在模块
    print('类型所在模块:',Son.__module__)
    #实例类型
    print('实例类型:',Son().__class__)

```

```

运行情况：

Python 3.3.2 (v3.3.2:d047928ae3f6, May 16 2013, 00:03:43) [MSC v.1600 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> ================================ RESTART ================================
>>> 
这是构造函数,son
类型帮助信息:  A simple example class
类型名称: Son
类型所继承的基类: (<class '__main__.Father'>,)
类型字典: {'__module__': '__main__', 'sayHello': <function Son.sayHello at 0x010194F8>, '__doc__': 'A simple example class', '__init__': <function Son.__init__ at 0x010194B0>, 'i': 12345}
类型所在模块: __main__
这是构造函数,son
实例类型: <class '__main__.Son'>
>>> 

```

#Python支持多重继承

首先第一点，你会发现Class的定义中有一个括号，这是体现继承的地方。 Java用extends，C#、C++用冒号(:)，Python则用括号了。从括号中包含着两个值，聪明的你一定可以发现：Python支持多重继承；

#__init__是Class中的构造函数

第二点，__init__是Class中的构造函数，两种不同形式的构造函数体现了Python支持函数重载。在构造函数中，有一个特别的参数self，其含义与我们在Java和C#中常见的this是一样的。在这里需要强调一点：在Class中定义的方法实质上也是function，但是在方法定义的时候必须包含self这个参数，而且必须将self这个参数放在第一位；

#python成员变量

第三点，在Python中，你并不需要显式的声明Class的Data Members，而是在赋值的时候，被赋值的变量就相应成为了Class的Data Memebers，正如代码中的x和y。不仅你不需要显式的声明Data Members，更加特别的，你甚至可以通过del方法将Class中的Data Memebers给删掉。当我第一次看到这样的特性的时候，着实吃了一惊。毕竟OO的第一条就是封装了，但是这样的特性是不是破坏了封装的特性呢？

#python方法二义性问题

第四点，由于Python支持多重继承，因此就有可能出现方法二义性问题[1]。然而由于Python遵循深度优先的搜寻法则，很好地避免了方法二义性的问题。例如在以上的代码中，MyClass同时继承于BaseClassA和BaseClassB，假设MyClass调用一个叫derivedMethod方法，derivedMethod同时定义在BaseClassA和BaseClassB中，且Signature也完全相同，那么BaseClassA中的方法将被调用。如果BaseClassA中并没有定义derivedMethod，而是BaseClassA的父类定义了这个方法的话，将会是BaseClassA的父类中derivedMethod被调用。总之，继承方法搜索的路径是先从左到右，在选定了一个BaseClass之后，将会一直沿着该BaseClass的继承结构进行搜索，直至最顶端，然后再到另外一个一个BaseClass。

就先说着这么多了，对于Python中OO的特性将会在以后的Post中有进一步的讲述。

[1] 方法二义性：由于一个类同时继承于两个或者多个父类，而在这些父类当中存在着signature完全相同的方法，那么编译器将无法判断子类将继承哪个父类中的方法，从而导致方法二义性问题。
