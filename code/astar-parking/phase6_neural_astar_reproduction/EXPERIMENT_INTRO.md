# Phase 6 实验开头：Learning Heuristic / Neural A* 简化复现

Phase 6 的目标是先简单复现论文中“用神经网络学习启发式函数”的核心思想，再考虑如何把这个思想迁移回自动泊车实验。

本阶段不是直接继续改 Phase 4 的 Hybrid A*，也不是直接把 CNN 接到泊车场景里，而是先做一个更清楚、更可控的二维网格实验：

```text
随机 2D 栅格地图
-> Dijkstra 反向搜索生成 cost-to-go 标签
-> CNN 学习整张地图上的 heuristic
-> 把 learned heuristic 接回 A*
-> 对比传统 heuristic 和 learned heuristic 的搜索效率
```

这样做的原因是：Phase 5 已经证明 MLP 可以从 Hybrid A* 成功路径里学到 `cost_to_go` 的大趋势，但 Phase 5 的输入只包含状态和目标，没有地图信息。也就是说，Phase 5 的模型还不能真正“看见障碍物”。Phase 6 则开始让模型输入地图，让网络学习 obstacle-aware heuristic，这是论文中最值得借鉴的部分。

---

## 1. 相关论文思想

当前参考论文是：

```text
Learning Heuristic Functions for Mobile Robot Path Planning Using Deep Neural Networks
```

论文的核心思想可以概括为：

```text
不要让神经网络直接输出动作；
而是让神经网络学习 heuristic；
再把 learned heuristic 放回传统搜索算法里使用。
```

也就是说，它不是端到端替代 A*，而是保留搜索框架：

```text
f = g + h
```

其中：

- `g` 是从起点到当前节点已经花掉的代价
- `h` 是从当前节点到目标的剩余代价估计

传统 A* 常用的 `h` 可能是：

```text
Manhattan distance
Euclidean distance
Dijkstra distance field
Reeds-Shepp distance
```

论文希望用神经网络学到更接近真实 `cost-to-go` 的 `h`，从而减少 A* 搜索时展开的节点数。

---

## 2. 论文大致流程

论文的方法可以拆成几个步骤：

### 2.1 生成训练标签

论文先用传统搜索方法生成标签。对于简单 2D 网格世界，可以从目标点开始反向跑 Dijkstra：

```text
goal
-> 反向扩散到所有可达格子
-> 得到每个格子到 goal 的最短距离
```

这个距离场就是：

```text
h*(x, y)
```

也就是每个位置到目标的真实最短代价。

### 2.2 用地图和目标作为输入

论文不是只输入当前点坐标，而是让网络看到环境结构。

二维网格版本可以理解成：

```text
obstacle map
goal map
```

其中：

- `obstacle map` 表示哪些格子是障碍物
- `goal map` 表示目标点在哪里

这样网络可以学习：

```text
障碍物怎么影响到目标的距离
哪里需要绕路
哪里是死胡同
哪里更接近目标
```

### 2.3 网络输出 heuristic map

网络不是只输出一个数，而是输出整张图上的 heuristic：

```text
输入：地图 + 目标
输出：每个格子的 cost-to-go
```

所以输出可以看成：

```text
H x W 的距离场
```

训练时用网络输出和 Dijkstra 标签做误差，例如 MSE 或 MAE。

### 2.4 接回 A*

训练好后，网络预测出的 heuristic map 会被放回 A*：

```text
A* 搜索当前节点 (x, y)
-> 去 learned heuristic map 里查 h(x, y)
-> 用 f = g + h 排序 open list
```

最终评估时，论文真正关心的不只是预测误差，还包括：

- 搜索节点数是否减少
- 搜索时间是否减少
- 路径长度是否保持合理
- 成功率是否稳定

这一点对我的实验非常重要。因为 heuristic 的价值不是“预测数值看起来准”，而是能不能让 planner 搜索得更有效。

---

## 3. 和我的泊车实验的关系

我的前几个阶段已经形成了一个从简单到复杂的路径：

```text
Phase 1：2D point A*
Phase 2：障碍物膨胀后的 2D A*
Phase 3：Hybrid A*，加入车辆姿态和运动学
Phase 4：Hybrid A* v2 + 控制相关尝试
Phase 5：用 MLP 学 Hybrid A* 成功路径上的 cost_to_go
Phase 6：复现论文的 CNN learned heuristic 思路
```

Phase 5 的输入是：

```text
[x, y, sin(theta), cos(theta), goal_x, goal_y, sin(goal_theta), cos(goal_theta)]
```

它的标签来自 Hybrid A* 成功路径上的剩余代价：

```text
cost_to_go
```

这个标签有一个优点：

```text
它来自真实 Hybrid A* 成功路径，因此包含了车辆姿态、倒车、转向和非完整约束的影响。
```

但它也有一个缺点：

```text
模型没有输入地图，因此不能真正理解障碍物结构。
```

Phase 6 的意义就是补上这一块：

```text
让模型看地图；
让模型学习地图结构对 heuristic 的影响；
先在 2D 网格世界复现清楚，再迁移回泊车问题。
```

---

## 4. 关于 Dijkstra 标签和泊车问题的矛盾

这是 Phase 6 开始前必须明确的一点。

在普通 2D A* 中，状态只有：

```text
(x, y)
```

动作通常是：

```text
上下左右
或八邻域移动
```

这种情况下，从目标点反向跑 Dijkstra，得到的距离场就是该 2D 问题里的最优 heuristic：

```text
h*(x, y)
```

但是自动泊车不是普通 2D 点机器人问题。泊车车辆的状态是：

```text
(x, y, theta)
```

车辆还受到这些约束：

- 不能侧移
- 不能原地转向
- 有最小转弯半径
- 有前进和倒车
- 有倒车惩罚和转向惩罚
- 车身是矩形，会发生碰撞
- 到达目标时还要满足姿态要求

所以，如果只在 2D 栅格上跑 Dijkstra，它最多能得到：

```text
点机器人从当前位置到目标位置的最短距离
```

它不能得到：

```text
车辆从当前姿态开到目标姿态的真实最短可行代价
```

因此，2D Dijkstra 对泊车问题来说不是严格最优启发，只能作为一个 baseline。

真正的泊车最优启发应该是：

```text
h*(x, y, theta)
= 从当前车辆状态到目标泊车状态的最小可行代价
```

这个 `h*` 必须在和 Hybrid A* 一样的状态空间和动作模型上计算：

```text
状态：x, y, theta
动作：forward / reverse + left / straight / right
代价：距离 + 倒车惩罚 + 转向惩罚
约束：车辆运动学 + 车身碰撞
```

这也解释了为什么 Phase 5 的标签虽然不是严格全局最优 `h*`，但仍然比普通 2D Dijkstra 更贴近我的泊车问题：

```text
Phase 5 的标签来自 Hybrid A* 成功路径的剩余代价。
它不是数学意义上的全状态最优值函数，
但它已经包含了 Hybrid A* 实际规划时的非完整约束、倒车、转向和碰撞检查。
```

---

## 5. 为什么 Phase 6 仍然先做 2D 简化复现

虽然 2D Dijkstra 不能直接作为泊车问题的最优标签，但它仍然适合 Phase 6 的第一步。

原因是：

```text
先复现论文思想，而不是一开始就解决完整泊车问题。
```

二维网格实验的优点：

- 状态空间简单，容易检查
- Dijkstra 标签可靠，容易解释
- CNN 输入输出结构清楚
- A* baseline 容易实现
- 可以快速验证 learned heuristic 是否能减少搜索节点

如果一开始直接进入泊车 CNN，会同时遇到很多问题：

- 地图怎么编码
- 姿态怎么编码
- 车辆矩形怎么编码
- 标签到底用 Hybrid A* 路径剩余代价，还是 SE(2) 反向搜索
- 网络输出一个数，还是输出 `(x, y, theta)` 的三维 heuristic volume
- learned heuristic 是否会破坏 A* 的最优性和稳定性

这些问题都很重要，但不适合一开始全部混在一起。

所以 Phase 6 的路线是：

```text
先用 2D 网格世界复现论文的最小闭环；
再把学到的方法迁移回泊车。
```

---

## 6. Phase 6 第一版实验目标

Phase 6 第一版只做 2D 随机地图 learned heuristic。

输入：

```text
X_map: (N, C, H, W)
```

其中 `C` 可以先设为 3：

```text
channel 0: obstacle map
channel 1: start map
channel 2: goal map
```

标签：

```text
y: Dijkstra cost-to-go map
```

也就是：

```text
每个 free cell 到 goal 的最短距离
```

训练目标：

```text
CNN(map, start, goal) -> cost_to_go_map
```

搜索实验：

```text
传统 A* + Manhattan heuristic
传统 A* + Euclidean heuristic
A* + CNN learned heuristic
```

评估指标：

- 成功率
- 路径长度
- expanded nodes
- generated nodes
- planning time
- learned heuristic 的 MAE / RMSE

最重要的指标是：

```text
expanded nodes 是否减少。
```

因为 learned heuristic 的主要目标是减少搜索浪费。

---

## 7. Phase 6 和后续泊车版本的衔接

Phase 6 第一版是 2D 网格复现，不代表最终泊车版本。

后续迁移到泊车时，可能有两条路线：

### 7.1 路线 A：地图 CNN + 状态 MLP 融合

输入：

```text
local map image
state vector: x, y, sin(theta), cos(theta)
goal vector: goal_x, goal_y, sin(goal_theta), cos(goal_theta)
```

输出：

```text
一个 cost_to_go 数值
```

这条路线和 Phase 5 最接近，比较容易接回现有 Hybrid A*。

### 7.2 路线 B：学习 SE(2) heuristic volume

输入：

```text
map + goal
```

输出：

```text
H x W x theta_bins 的 heuristic volume
```

也就是：

```text
每个 (x, y, theta) 到 goal 的预测代价
```

这更接近严格的泊车 heuristic，但实现难度明显更高。

需要解决：

- SE(2) 状态离散化
- 反向运动学搜索生成标签
- 三维输出的内存和训练问题
- 与 Hybrid A* 连续状态的插值问题

因此 Phase 6 暂时不直接做路线 B。

---

## 8. 当前阶段判断

当前最合理的学习和实验顺序是：

```text
1. 完成 2D 随机地图数据生成
2. 用 Dijkstra 生成 cost-to-go 标签
3. 写一个普通 2D A* baseline
4. 训练 CNN 预测 cost-to-go map
5. 把 learned heuristic 接回 A*
6. 对比 expanded nodes 和路径质量
7. 整理 Phase 6 实验报告
8. 再决定是否迁移回 Hybrid A* 泊车
```

Phase 6 的核心不是证明 CNN 一定比传统 heuristic 强，而是弄清楚：

```text
神经网络学习 heuristic 的完整流程到底是什么；
地图输入对 heuristic 学习有什么帮助；
learned heuristic 接回搜索后，评价标准应该怎么看；
这个方法哪些部分能迁移到我的泊车实验，哪些部分不能直接迁移。
```

---

## 9. 当前结论

Phase 6 是从 Phase 5 到更完整 learning-based planning 的过渡阶段。

Phase 5 已经证明：

```text
只用状态向量，MLP 可以学到 Hybrid A* 成功路径上的 cost_to_go 趋势；
但由于没有地图输入，模型不能真正理解障碍物。
```

Phase 6 要验证：

```text
让 CNN 输入地图后，模型能否学习 obstacle-aware heuristic；
learned heuristic 是否能减少 A* 搜索节点；
论文中的方法哪些可以迁移到泊车，哪些需要改造。
```

当前先做 2D 简化复现是合理的，因为它能把论文方法跑通、看懂、讲清楚。等这个闭环完成后，再回到泊车问题中考虑：

```text
map + state + goal
```

或者：

```text
SE(2) heuristic volume
```

这两个更贴近真实自动泊车的版本。
