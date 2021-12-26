## 基于 MegFlow 框架的猫咪检测以及自动投喂的解决方案

> 有关项目实现的详细可以看这里 **[基于旷视开源框架MegFlow的猫粮机](https://sinnammanyo.cn/personal-site/docs/studio/summary/%E7%8C%AB%E7%B2%AE%E6%9C%BA/Cat-food-machine-based-on-MegFLow)**

## 如何修改以及使用

目前程序实现比较简单，只是针对自己的两只猫咪进行了逻辑操作，包括特征提取部分，多次添加同一只猫咪的不同体态，不同环境下的特征

可以使用 **example/cat_finder** 中的 `image` 服务进行猫咪特征的注册

- [examples/cat_finder](https://github.com/rcxxx/MegFlow/tree/master/flow-python/examples/cat_finder)

然后修改对应 **`name.py`** 中的

``` py
self._cat_dt = [...]
self._cat_ts = [...]
```

来存储相应的猫咪信息

- **`serial.py`** 为串口数据节点
  - 串口屏使用 [USART HMI](http://wiki.tjc1688.com/doku.php?id=start)

- **`nano_gpio.py`** 为 `Jetson Nano` 开发板的 `io` 控制节点

