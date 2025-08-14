# mapping

* #TODO: (mid)...

![alt text](./assets/puml/mapping/system_overview.png)

## ValueConversionTables

```c++
// 0 is unknown, [1, 32767] maps to [lower_bound, upper_bound].
// vector[0] = unknown_result;
// vector[1, 32767] 存放的是 [lower_bound, upper_bound]，线性插值分布值；

// GetConversionTable(float unknown_result, float lower_bound, float upper_bound)
// 返回vector 大小 是 65536，相当于存放了两边，目前不清楚放两遍的作用

```

## probability_values.h

* 概率值相关定义
  * **Probability** ： 概率，定义范围为[0.1,0.9],即[kMinProbability,kMaxProbability] ，未知为 **kUnknownProbabilityValue = 0**；
  * **Odds**（优势） ：**probability / (1 - probability)** ，如果有一个事件发生的概率为probability，那么优势就是发生概率与不发生概率的比值。
  * **CorrespondenceCost**（匹配代价）：**（1 - probability）** , 高概率表示事件发生的可能性高，而代价则应该低。优化过程中，我们更倾向于使用代价（cost）的概念，因为优化通常是最小化代价。

> 通过查表法，用于将浮点数映射到紧凑的 uint16整数表示（范围 [1, 32767]），主要用于优化存储和处理效率；

