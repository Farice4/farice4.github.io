---
layout: post
title: "Python Super使用"
date: 2016-09-13 20:09:02
description: ""
categories: "Python"
tags: [Super使用]
---

* content
{:toc}

* Super　

　  super 是用来解决多重继承问题的，直接用类名调用父类方法在使用单继承的时候没问题，但是如果使用多继承，会涉及到查找顺序（MRO）、重复调用（钻石继承）等种种问题。总之前人留下的经验就是：保持一致性。要不全部用类名调用父类，要不就全部用 super，不要一半一半。





> 举例(未使用super)：

```
class FooParent(object): 
    def __init__(self): 
        self.parent = 'I\'m the parent.' 
        print 'Parent' 
     
    def bar(self,message): 
        print message, 'from Parent' 
         
class FooChild(FooParent): 
    def __init__(self): 
        FooParent.__init__(self) 
        print 'Child' 
         
    def bar(self,message): 
        FooParent.bar(self,message) 
        print 'Child bar function.' 
        print self.parent 
         
if __name__=='__main__': 
    fooChild = FooChild() 
    fooChild.bar('HelloWorld')  
```

举例(使用Super继承)

```
class FooParent(object): 
    def __init__(self): 
        self.parent = 'I\'m the parent.' 
        print 'Parent' 
     
    def bar(self,message): 
        print message,'from Parent' 
 
class FooChild(FooParent): 
    def __init__(self): 
        super(FooChild,self).__init__() 
        print 'Child' 
         
    def bar(self,message): 
        super(FooChild, self).bar(message) 
        print 'Child bar fuction' 
        print self.parent 
 
if __name__ == '__main__': 
    fooChild = FooChild() 
    fooChild.bar('HelloWorld')  
```

程序运行结果相同，为：

```
Parent
Child
HelloWorld from Parent
Child bar fuction
I'm the parent.
```
