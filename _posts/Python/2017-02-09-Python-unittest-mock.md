---
layout: post
title: "Python Mock使用"
date: 2017-02-09 20:09:02
description: ""
categories: "Python"
tags: [Unittest Mock使用]
---

* content
{:toc}

### Mock介绍

  Mock这个词在英语中有模拟的这个意思，因此我们可以猜测出这个库的主要功能是模拟一些东西。准确的说，Mock是Python中一个用于支持单元测试的库，它的主要功能是使用mock对象替代掉指定的Python对象，以达到模拟对象的行为。




### Mock使用举例


> 程序代码(mockclass.py)


```
class CouldClient(object):
    def connect(self):
        pass

    def disconnect(self):
        pass

    def upload(self):
        pass

    def download(self):
        pass

``` 

> 测试代码(testcould.py)

```


import unittest

import mock
from mockclass import CouldClient


class TestCloud(unittest.TestCase):
    def setUp(self):
        self.obj = mock.Mock(CouldClient)

    def terDown(self):
        self.obj = None

    def test_connect(self):
        self.obj.connect.return_value = 200
        self.assertEqual(self.obj.connect(), 200)


if __name__ == '__main__':
    unittest.main()

```
