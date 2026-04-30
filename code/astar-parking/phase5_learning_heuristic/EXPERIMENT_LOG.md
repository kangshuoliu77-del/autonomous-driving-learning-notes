# Phase 5 实验记录：学习 Hybrid A* 启发式

这份记录用于保留 Phase 5 的完整实验过程：每一步在做什么、为什么这么做、遇到了什么问题、当前结果是什么。

> [!NOTE]
> 当前阶段已经完成：生成 `cost_to_go` 数据集，并训练出第一版 MLP 启发式模型。下一步是离线评估，然后再谨慎接回 Hybrid A*。

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 数据集生成 | ✅ 完成 | 100 次 trials，1783 条样本 |
| MLP 训练 | ✅ 完成 | test loss 约 0.8251 |
| 接回 Hybrid A* | ⏳ 下一步 | 先做离线评估，再接入搜索 |
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

## 8. ⚠️ 遇到的问题和解决

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

## 9. 📦 当前产物

代码：

```text
dataset_generator.py
train_heuristic_mlp.py
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

## 10. 🚀 下一步计划

阶段检查：

- [x] 生成第一版 `cost_to_go` 数据集
- [x] 训练第一版 MLP heuristic
- [ ] 做离线误差和排序评估
- [ ] 作为弱辅助项接回 Hybrid A*
- [ ] 对比原始启发式和 learned heuristic 的搜索效率

下一步不是立刻替换原始 `h`，而是先做离线评估：

```text
load heuristic_mlp_v1.pth
评估预测误差
评估排序准确率
```

如果离线评估稳定，再把 learned heuristic 接回 Hybrid A*。

第一版接入建议：

```text
不要直接替换传统 h
先作为 tie-breaker 或弱辅助项
```

原因：

learned heuristic 不一定满足 A* 的 admissible 条件，直接替换可能导致搜索不稳定。
