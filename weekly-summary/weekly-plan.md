# Week 6 Plan：2026.04.19 - 2026.04.25

## 本周目标

围绕 A* 泊车实验继续深入，打通 Planning → Control 闭环。

## 学习任务

### MR 精读
- [ ] 第 9 章：轨迹生成（Time Scaling、Trajectory Parameterization）
- [ ] 第 11 章：机器人控制（PID、前馈+反馈、运动控制与力控制）

### Phase 4 实验（phase4_hybrid_astar_v2）

#### 搜索加速
- [~] collision_checker numpy 向量化 — 尝试后回退，小数据量下纯 Python 更快
- [~] RS 曲线启发式 — 实现完整 RS 路径族（48种），提升 < 8%，保留但无实质效果
- [~] 双向 Hybrid A* — 实现后放弃，SE(2) 相遇点朝向不兼容产生折角

#### 路径平滑
- [~] 梯度下降平滑 — 尝试两种方案均放弃；dt=1.0 路径点稀疏，无折角可平滑

#### 解析扩展
- [x] Reeds-Shepp 曲线 — 完整实现（reeds_shepp.py，48种路径族）

#### 控制器接入
- [~] Pure Pursuit — 尝试后放弃，不适用
- [x] MPC 路径跟踪 — CasADi + IPOPT，4角点碰撞检测，成功率 10/10（100%）
- [x] 规划-跟踪闭环联调 — Hybrid A* → 插值加密 → MPC，完整闭环验证

## 实际产出

- phase4_hybrid_astar_v2：完整实验代码 + EXPERIMENT_LOG.md（含所有失败尝试）
- Reeds-Shepp 路径族实现
- CasADi+IPOPT MPC 控制器，成功率 100%，0碰撞
- 第 9、11 章精读笔记（待完成）
