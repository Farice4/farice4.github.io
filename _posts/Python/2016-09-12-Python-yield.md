---
layout: post
title: "Python yield使用"
date: 2016-09-12 11:20:06
description: ""
categories: "Python"
tags: [yield 使用]
---

* content
{:toc}

* Yield　

  Yield 的功能类似于return, 但是不同之处在于它返回的是生成器





* 生成器

  生成器是通过一个或多个yield表达式构成的函数，每一个生成器都是一个迭代器（但是迭代器不一定是生成器）．

　如果一个函数包含yield关键字，这个函数就会变为一个生成器．

　生成器并不会一次返回所有结果，而是每次遇到yield关键字后返回相应结果，并保留函数当前的运行状态，等待下一次的调用．

　由于生成器也是一个迭代器，那么它就应该支持next方法获取下一个值．

> 举例:

```
# 通过yield来创建生成器

def func():
    for i in xrange(10):
        yield i

# 调用如下:
f = func()
print f #此时生成器没有运行
<generator object func at 0x7fe01a853820>

print f.next()
0

print f.next()
1

print f.next()
2

......

print f.next()
9

print f.next() #当执行完最后一次循环后，结束yield语句，生成StopItertion异常oTraceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration

```

* 通过列表创建生成器

```
[i for i in xrange(10)]
```

* yield send使用

```
def func():
    n = 0
    while 1:
        n = yield n #可以通过send函数向n赋值

f = func()
f.next()
0

f.send(1)
1

f.send(2)
2

```

* 应用

> 生成一个满足很大列表的要求，这个列表需要保存在内存中，很明显内存限制这个问题

```
def get_primes(start):
    for element in magical_infinite_range(start):
        if is_prime(element):
            return element

```

```
def get_primes(number):
    while True:
        if is_prime(number):
            yield number
        number += 1

```
