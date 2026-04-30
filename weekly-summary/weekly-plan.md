# Week 7 Plan：2026.04.26 - 2026.05.02

## 本周目标

在 Phase 4 泊车规划控制闭环基础上，完成 PyTorch / D2L 核心入门，并启动 Phase 5 learning heuristic 实验。

本周主线已经从“补深度学习基础”推进到：

```text
Phase 4 Hybrid A* 成功路径
-> cost_to_go 数据集
-> MLP heuristic
-> 离线评估
-> 后续接回 Hybrid A*
```

## 学习任务

### 机器学习 / 深度学习

- [x] 整理《动手学深度学习》资料
- [x] 完成 D2L 第 2 章预备知识核心主线
- [x] 完成 D2L 第 3 章线性神经网络核心主线
- [x] 完成 D2L 第 4 章 MLP 核心主线
- [x] 完成 D2L 第 5 章深度学习计算核心内容
- [x] 完成 D2L 第 6 章 CNN 核心主线
- [x] 梳理 `dataset -> dataloader -> model -> loss -> optimizer -> train loop`
- [x] 将多个 D2L 复习模板整理入库并推送
- [ ] 后续按实验需要补第 11 章优化算法
- [ ] 后续按论文需要理解 Neural A* / Transformer 基本思想

### 泊车实验延伸

- [x] 设计第一版 `cost_to_go` 数据集字段
- [x] 确定 `.npz` 数据保存格式
- [x] 生成 100 次 Hybrid A* 成功路径样本
- [x] 训练第一版 MLP heuristic
- [x] 整理 Phase 5 README 和实验记录
- [x] 调研 learning heuristic / neural planning 相关论文
- [ ] 编写 `evaluate_heuristic.py`
- [ ] 评估预测误差、不同 cost 区间误差和 ranking accuracy
- [ ] 将 MLP heuristic 作为弱辅助项或 tie-breaker 接回 Hybrid A*
- [ ] 对比原始 Hybrid A* 与 learned heuristic 的搜索节点数、耗时、成功率

### MR 学习

- [ ] MR 第 11 章按 Phase 4 / MPC 需要继续看控制器相关内容
- [ ] 暂不机械通读，优先服务当前 Phase 5 实验

## 本周理想产出

- [x] `machine-learning/` 目录结构
- [x] D2L 3-6 章核心复习模板
- [x] Phase 5 learning heuristic 第一版代码
- [x] 第一版 `cost_to_go` 数据集
- [x] 第一版 MLP heuristic 训练结果
- [x] Phase 5 实验记录
- [ ] learned heuristic 离线评估脚本
- [ ] 原始 Hybrid A* vs learned heuristic 对照实验

## 本周后半段重点

1. 不再继续机械刷 D2L，新知识优先服务 Phase 5。
2. 先做离线评估，不急着把神经网络接进搜索。
3. 评估重点不是只看 test loss，而是看排序能力和不同 cost 区间表现。
4. 如果离线评估合理，再把 MLP 作为辅助启发式接回 Hybrid A*。
5. 下一版更智能的方向是加入 `local map + CNN`，让模型看到障碍物和空间结构。
