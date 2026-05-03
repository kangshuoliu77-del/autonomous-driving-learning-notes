# Week 8 Plan：2026.05.03 - 2026.05.09

## 本周目标

收束 Phase 5 / Phase 6 的 learning heuristic 探索，把重点从 supervised heuristic 转向 PPO / RL 与 imitation learning 的入门实验。

当前主线：

```text
Phase 4 传统规划控制基线
-> Phase 5/6 理解 learning heuristic
-> expert data / imitation learning
-> PPO / RL simulation
```

## 学习任务

### 深度学习

- [ ] 继续推进 D2L 后续内容
- [ ] 重点了解 CNN 后续、Transformer、NLP、CV 的基本思想
- [ ] 不追求一次吃透，先建立工具箱和论文阅读背景

### 强化学习

- [ ] 选择一个简单环境跑通 PPO
- [ ] 理解 policy、value、reward、advantage、credit assignment
- [ ] 记录 PPO 训练流程和关键超参数

### 泊车 / Planning + Learning

- [ ] Phase 6 若继续，只做 CNN heuristic 接回 A* 的最小对照
- [ ] 梳理 Hybrid A* / MPC expert trajectory 能保存哪些字段
- [ ] 初步思考 imitation learning：输入、输出、标签、评价指标

### 长期基础

- [ ] MR 第 11 章按需继续
- [ ] Linear Systems Theory 继续推进
- [ ] Sutton RL 作为后续强化学习主教材
- [ ] 概率 / 贝叶斯 / 概率机器人作为 SLAM 和 uncertainty 预备

## 本周理想产出

- [ ] 一个 PPO 最小实验记录
- [ ] 一份 imitation learning 与 parking expert data 的简短设计草稿
- [ ] 如继续 Phase 6，补完 CNN learned heuristic 接回 A* 对照
- [ ] D2L 后续章节的简短学习记录

## 本周重点

1. 不继续深挖 Neural A*，把它定位为过程理解。
2. 从 supervised learning 过渡到 RL / imitation learning。
3. 继续围绕 planning 主线，不脱离已有 parking 系统。
