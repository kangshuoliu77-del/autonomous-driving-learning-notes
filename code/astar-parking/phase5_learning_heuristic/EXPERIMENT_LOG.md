# Phase 5 实验记录：学习 Hybrid A* 启发式

这份记录用于保留 Phase 5 的完整实验过程：每一步在做什么、为什么这么做、遇到了什么问题、当前结果是什么。

> [!NOTE]
> 当前阶段已经完成：生成 `cost_to_go` 数据集、训练第一版 MLP 启发式模型，并完成第一轮离线评估。下一步是把 learned heuristic 谨慎接回 Hybrid A* 做对照实验。

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 数据集生成 | ✅ 完成 | 100 次 trials，1783 条样本 |
| MLP 训练 | ✅ 完成 | test loss 约 0.8251 |
| 离线评估 | ✅ 完成 | MAE 0.6216，ranking acc 约 0.98 |
| 接回 Hybrid A* | ⏳ 下一步 | 先作为 tie-breaker 或弱辅助项 |
| MPC / 控制器学习 | ⏸️ 暂缓 | 后续阶段再做 |

---

## 1. 🎯 当前阶段目标

Phase 5 的第一阶段不是直接替换 Hybrid A*，也不是直接学习 MPC 控制器，而是先做一个最小 learning heuristic 闭环：

```text
Phase 4 Hybrid A* 成功路径
-> 拆成 (state, goal) 样本
-> 生成 cost_to_go 标签
-> 训练 MLP 预测 cost_to_go
-> 后续再接回 Hybrid A* 辅助搜索
```

当前第一版不使用：

- MPC 轨迹
- local map / CNN
- Transformer
- RL

原因是第一阶段要先验证一个最小问题：

```text
只看当前状态和目标，MLP 能不能学到剩余路径代价的大趋势？
```

---

## 2. 🧭 为什么先学启发式

Hybrid A* 的搜索使用：

```text
f = g + h
```

其中：

- `g`：从起点走到当前节点已经花掉的代价
- `h`：当前节点到目标的剩余代价估计

Phase 4 当前的 `h` 是：

```text
远处：欧氏距离
近处：Reeds-Shepp 距离
```

这个启发式考虑了几何距离和车辆运动学，但基本不理解障碍物环境，也不能直接知道一条成功路径上真实还剩多少代价。

所以第一版 learning heuristic 的目标是：

```text
用成功路径监督训练一个模型，让它预测 state 到 goal 的 cost_to_go。
```

---

## 3. 🚗 为什么第一版不用 MPC 轨迹

Hybrid A* 路径比较粗，确实不是最终真实执行轨迹。

但是第一版要学的是：

```text
怎么帮助搜索
```

不是：

```text
怎么真实控制车辆
```

因此第一版标签来自 Hybrid A* 成功路径更直接：

```text
state -> 从这个 state 沿成功路径到 goal 还剩多少规划代价
```

MPC 轨迹后续可以用于学习：

- 控制器模仿
- 执行风险
- 是否碰撞
- 跟踪误差
- 轨迹质量

但这些比第一版 learned heuristic 更复杂，暂时不放进第一阶段。

---

## 4. 🧾 数据集生成

脚本：

```text
dataset_generator.py
```

命令：

```bash
python3 dataset_generator.py --num-trials 100 --output datasets/parking_cost_to_go_v1.npz
```

做的事情：

1. 复用 Phase 4 的垂直泊车场景
2. 随机采样起点
3. 调用 Phase 4 的 Hybrid A*
4. 如果成功找到路径，就把路径拆成训练样本
5. 保存成 `.npz` 数据集

生成结果：

```text
success trials: 100/100
X shape: (1783, 8)
y shape: (1783, 1)
```

含义：

- 一共跑了 100 次随机起点
- 100 次都找到路径
- 成功路径一共拆成 1783 条训练样本
- 每条样本输入是 8 维
- 每条标签是 1 维 cost_to_go

---

## 5. 🧩 输入和标签

输入 `X`：

```text
[x, y, sin(theta), cos(theta), goal_x, goal_y, sin(goal_theta), cos(goal_theta)]
```

为什么角度不用 `theta`，而用 `sin(theta), cos(theta)`：

- 角度有周期性
- `179°` 和 `-179°` 实际方向很近
- 但直接用弧度数值会相差很大
- 用 `sin/cos` 可以避免角度在 `-pi/pi` 附近跳变

标签 `y`：

```text
cost_to_go
```

也就是：

```text
从当前路径点沿 Hybrid A* 成功路径走到终点，还剩多少路径长度
```

例如一条路径：

```text
s0 -> s1 -> s2 -> ... -> goal
```

会生成：

```text
s0 label = s0 到 goal 的剩余长度
s1 label = s1 到 goal 的剩余长度
...
goal label = 0
```

---

## 6. 🧠 第一个 MLP 模型

脚本：

```text
train_heuristic_mlp.py
```

模型结构：

```text
Linear(8, 64)
ReLU
Linear(64, 64)
ReLU
Linear(64, 1)
```

含义：

```text
8维 state-goal 特征
-> MLP
-> 预测 1 个 cost_to_go
```

训练设置：

```text
train / val / test = 70% / 15% / 15%
loss = MSELoss
optimizer = Adam
learning rate = 1e-3
epochs = 100
seed = 0
```

---

## 7. 📊 当前训练结果

一次记录的训练结果：

```text
epoch 100, train loss 1.0839, val loss 1.1836
test loss: 0.8854
```

整理脚本后再次验证的结果：

```text
epoch 100, train loss 1.0014, val loss 1.1103
test loss: 0.8251
```

典型预测：

```text
true=0.00, pred=0.03
true=6.00, pred=6.05
true=4.00, pred=3.65
true=11.00, pred=10.67
true=17.00, pred=15.32
true=9.00, pred=9.01
```

初步结论：

- MLP 已经能学到 cost_to_go 的大趋势
- 典型误差大约在 1 个 cost 单位左右
- 较大的 cost 样本误差更明显，这是第一版数据集可以接受的现象

> [!IMPORTANT]
> 这个结果只说明模型能离线预测 `cost_to_go` 的大趋势，还不能直接说明它接回 Hybrid A* 后一定能提升搜索效率。

---

## 8. 🔎 第一轮离线评估

脚本：

```text
evaluate_heuristic.py
```

评估目的：

```text
先判断第一版 MLP heuristic 到底学得怎么样，再决定是否接回 Hybrid A*。
```

评估数据：

```text
X shape: (1783, 8)
y shape: (1783, 1)
```

前 10 个样本预测：

```text
true=22.00, pred=19.09
true=21.00, pred=20.17
true=20.00, pred=21.44
true=19.00, pred=20.37
true=18.00, pred=19.08
true=17.00, pred=17.83
true=16.00, pred=16.56
true=15.00, pred=15.69
true=14.00, pred=14.82
true=13.00, pred=13.57
```

整体误差：

```text
MAE: 0.6216
RMSE: 1.0099
Max error: 8.1689
```

含义：

- `MAE` 表示平均每个样本预测错多少 cost 单位
- `RMSE` 对大误差更敏感，用来观察是否存在明显错得很大的样本
- `Max error` 表示最差样本的最大绝对误差

当前结果说明：

- 平均误差约 0.62，整体预测可接受
- RMSE 大于 MAE，说明大多数样本误差较小，但少量样本误差较明显
- 最大误差 8.1689，说明模型在部分状态上仍不稳定

分 cost 区间误差：

```text
0-5    count= 500, MAE=0.2819, Max=2.3288
5-10   count= 498, MAE=0.3956, Max=2.3140
10-15  count= 448, MAE=0.7748, Max=5.2493
15-20  count= 271, MAE=0.9905, Max=6.6783
20+    count=  66, MAE=2.3471, Max=8.1689
```

含义：

- 近目标区间 `0-10` 预测最好
- 中距离区间 `10-20` 误差逐渐增大
- 大 cost 区间 `20+` 只有 66 条样本，误差明显最大

当前判断：

```text
cost_to_go 越大，预测越困难。
```

可能原因：

- 大 cost 样本数量少
- 离目标越远，真实剩余代价越依赖路径绕行和障碍物结构
- 第一版 MLP 没有输入地图，只能根据 state 和 goal 推断，无法真正理解障碍物分布

排序准确率对比：

```text
Euclidean h ranking acc: 0.8918
2D Dijkstra h ranking acc: 0.8235
MLP learned h ranking acc: 0.9832
```

该指标做法：

```text
随机抽取 10000 对样本，比较某个 heuristic 是否能判断哪一个 state 的 cost_to_go 更小。
```

为什么需要这个指标：

```text
A* 搜索中，模型不一定必须把 cost_to_go 的绝对数值预测得完全准确。
更重要的是，它能不能判断哪个节点更值得先扩展。
```

为什么要和欧氏距离比：

```text
原始 Hybrid A* 里最基础的 h 是当前位置到目标位置的几何距离。
欧氏距离本身不理解姿态、绕行和障碍物结构，因此排序不一定接近真实 cost_to_go。
如果 MLP 的排序准确率明显高于欧氏距离，才说明它不只是学了“离目标近”，而是更接近成功路径上的剩余代价。
```

为什么要加 2D Dijkstra baseline：

```text
欧氏距离只看直线距离，不理解障碍物。
2D Dijkstra distance field 从 goal 在栅格地图上反向扩散，能得到 obstacle-aware 的二维最短路径距离。
它比欧氏距离更像传统搜索里的强启发式 baseline。
```

但这个 baseline 仍然有局限：

- 只考虑 `(x,y)`，不考虑 `theta`
- 不考虑车辆最小转弯半径
- 不考虑倒车、换挡和非完整约束
- 当前实现基于原始 occupancy grid，不是车辆 C-space 膨胀后的距离场

当前结果说明：

- 欧氏距离 baseline 的 ranking accuracy 是 0.8918
- 2D Dijkstra baseline 的 ranking accuracy 是 0.8235
- MLP learned heuristic 的 ranking accuracy 是 0.9832
- MLP 的排序能力明显强于欧氏距离 baseline
- 在当前数据集上，2D Dijkstra baseline 反而低于欧氏距离
- 虽然大 cost 区间数值误差较大，但 MLP 整体判断“谁更接近目标”的能力较好
- 第一版 MLP 具备作为搜索辅助项或 tie-breaker 的初步价值

对 2D Dijkstra 结果的解释：

```text
2D Dijkstra 知道障碍物，但不知道车辆姿态和非完整约束。
而本数据集标签来自 Hybrid A* 成功路径的剩余长度，里面包含姿态、倒车、转向和运动学约束的影响。
因此 2D Dijkstra 并不一定比欧氏距离更接近 Hybrid A* cost_to_go 排序。
```

这也说明：

```text
在泊车问题中，真正重要的不只是二维位置绕障碍距离，还包括车辆姿态和可行运动方式。
```

本轮离线评估结论：

```text
第一版 MLP heuristic 可以学习到 cost_to_go 的总体趋势；
近目标区域预测较准；
远离目标时误差明显增大；
排序能力明显强于欧氏距离和 2D Dijkstra baseline，适合作为辅助 heuristic 进入下一步实验；
但不适合直接替代原始 h。
```

---

## 9. ⚠️ 遇到的问题和解决

### ⏱️ 数据生成速度慢

现象：

100 次 trials 需要较长时间。

原因：

数据生成阶段主要耗时在 Hybrid A*：

- Python 循环
- `heapq`
- set 查重
- 碰撞检测
- 状态扩展

这些是 CPU 逻辑，不适合直接用 GPU。

结论：

- 数据生成慢是正常的
- GPU 主要用于后续 MLP/CNN 训练
- 后续如果需要更多数据，可以做多进程并行生成

---

## 10. 📦 当前产物

代码：

```text
dataset_generator.py
train_heuristic_mlp.py
evaluate_heuristic.py
```

本地生成但不提交 Git 的文件：

```text
datasets/parking_cost_to_go_v1.npz
models/heuristic_mlp_v1.pth
```

不提交数据和模型的原因：

- `.npz` 和 `.pth` 是实验产物
- 后续可能频繁更新
- 代码仓库先保持轻量

---

## 11. 🚀 下一步计划

阶段检查：

- [x] 生成第一版 `cost_to_go` 数据集
- [x] 训练第一版 MLP heuristic
- [x] 做离线误差和排序评估
- [ ] 作为弱辅助项接回 Hybrid A*
- [ ] 对比原始启发式和 learned heuristic 的搜索效率

下一步不是直接替换原始 `h`，而是把 learned heuristic 以更保守的方式接回搜索。

```text
不要直接使用 h = learned_h
```

第一版接入建议：

```text
方案 A：tie-breaker
当多个节点的原始 f 接近时，用 learned_h 判断谁更值得先扩展

方案 B：弱辅助项
h = original_h + alpha * learned_h
其中 alpha 先取较小值
```

原因：

learned heuristic 不一定满足 A* 的 admissible 条件，直接替换可能导致搜索不稳定。

下一轮实验需要记录：

- 原始 Hybrid A* 的搜索时间
- 原始 Hybrid A* 的 expanded nodes
- learned heuristic 版本的搜索时间
- learned heuristic 版本的 expanded nodes
- 成功率
- 路径长度
- 是否出现碰撞或搜索失败
