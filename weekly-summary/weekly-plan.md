# Week 10 Plan：2026.05.18 - 2026.05.24

## 本周目标

把 CDC grid world 扩展方向落到第一版可实现方案：复杂环境表示、区域图构造和 transition system 设计。

当前主线：

```text
complex polygon map
-> triangulation / convex cell decomposition
-> region graph
-> formation-aware transition system
-> DFTS / LTL symbolic synthesis
-> QP / controller refinement
```

## 学习任务

### 复杂环境表示

- [x] 阅读 Demyen & Buro 2006，重点看 triangle graph / abstract graph
- [ ] 快速浏览 Shewchuk Triangle，理解 constrained triangulation 的输入输出
- [ ] 阅读 Choset cell decomposition 中 free space -> cell adjacency graph 的部分
- [ ] 查 LaValle Chapter 6 中 polygonal obstacles / cell decomposition 作为背景

### CDC 扩展

- [ ] 明确原 CDC grid world 里的 region / transition / label 分别对应什么
- [ ] 设计 polygon / triangle map 下的新 region set
- [ ] 设计第一版 formation-aware transition feasibility rule
- [ ] 写一页 idea 草稿：问题、输入输出、方法流程、实验计划

### GCS / IRIS

- [ ] GCS 先保留在建模直觉层，不继续深推 Section 7
- [ ] IRIS 重点看输入输出和 convex region generation，不深挖 SDP 细节
- [ ] 对比 triangulation 和 IRIS 各自适合放在哪一层

### 基础补充

- [ ] 继续补 Boyd 凸优化第 3 章凸函数
- [ ] QP / CBF / CLF 只按 CDC 需要查，不展开太多
- [ ] RL / PPO 暂时后移，不抢当前主线

## 本周理想产出

- [x] 一份 complex environment representation 读书/论文笔记
- [ ] 一个 region graph / transition system 草图
- [ ] 一页 CDC journal extension idea 草稿
- [ ] 明确第一版实现选 triangulation 还是 IRIS

## 2026.05.19 更新

- 完成 Demyen & Buro 2006 第一轮阅读。
- 当前判断：这篇论文最适合作为 polygon map -> triangulation -> triangle graph -> formation-aware transition system 的第一版参考。
- 后续重点从 TA*/TRA* 搜索细节转向 transition feasibility：`through_width(region, entry_edge, exit_edge) >= required_width(formation)`。

## 本周重点

1. 先做复杂环境和 transition system，不急着做大 MICP。
2. 保留 CDC 的 symbolic synthesis + QP 两层结构。
3. 第一版追求清楚、可实现、可实验。
