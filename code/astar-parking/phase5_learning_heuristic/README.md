# Phase 5：Learning Hybrid A* 启发式

本阶段开始把 learning 方法接入自动泊车实验。

第一版目标很小：

```text
Hybrid A* 成功路径
-> (state, goal) 样本
-> cost_to_go 标签
-> MLP 学习启发式
```

当前不直接学习 MPC 控制器，也不直接使用 CNN 地图输入。

---

## 当前文件

```text
dataset_generator.py      # 生成 cost_to_go 数据集
train_heuristic_mlp.py    # 训练第一版 MLP heuristic
EXPERIMENT_LOG.md         # 中文实验过程记录
```

本地会生成但不提交 Git：

```text
datasets/*.npz
models/*.pth
```

---

## 数据集格式

每条样本：

```text
input = [x, y, sin(theta), cos(theta), goal_x, goal_y, sin(goal_theta), cos(goal_theta)]
label = cost_to_go
```

`cost_to_go` 表示：

```text
从当前状态沿 Hybrid A* 成功路径走到目标，还剩多少路径长度
```

---

## 运行

生成数据：

```bash
cd code/astar-parking/phase5_learning_heuristic
python3 dataset_generator.py --num-trials 100 --output datasets/parking_cost_to_go_v1.npz
```

训练 MLP：

```bash
python3 train_heuristic_mlp.py
```

---

## 当前结果

100 次随机起点数据生成：

```text
success trials: 100/100
X shape: (1783, 8)
y shape: (1783, 1)
```

第一版 MLP 已能预测 cost_to_go 的大趋势，典型误差约 1 个 cost 单位。

详细过程见：

```text
EXPERIMENT_LOG.md
```
