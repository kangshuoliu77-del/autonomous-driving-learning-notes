# Week 6 Plan：2026.04.19 - 2026.04.25

## 本周目标

围绕 A* 泊车实验继续深入，打通 Planning → Control 闭环。

## 学习任务

### MR 精读
- [ ] 第 9 章：轨迹生成（Time Scaling、Trajectory Parameterization）
- [ ] 第 11 章：机器人控制（PID、前馈+反馈、运动控制与力控制）

### Phase 4 优化（新建 phase4_hybrid_astar_v2）
- [x] 搜索加速：collision_checker numpy 向量化完成
- [ ] 搜索加速：RS 曲线启发式、双向 A*
- [ ] 轨迹平滑：梯度下降 / 牛顿法后处理路径点
- [ ] 解析扩展：Reeds-Shepp 曲线对接终点

### 控制器接入
- [ ] 实现 Pure Pursuit 或 MPC 路径跟踪
- [ ] 与 Phase 3 规划结果联调，验证闭环效果

## 预期产出

- 第 9、11 章精读笔记
- Phase 3 优化版代码（加速 + 平滑 + RS 射击）
- 规划-跟踪闭环 Demo
