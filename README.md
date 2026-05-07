# 🚗 Autonomous-Driving-Learning-Notes

> 系统记录从零学习自动驾驶、控制理论、强化学习和机器人的过程

---

## 📂 仓库结构

- 🤖 **robotics/** —— 机器人学
  - modern-robotics/ —— Modern Robotics 读书笔记
- 📐 **control-theory/** —— 控制理论
  - 现代控制理论基础 状态空间 稳定性 能控能观
  - 线性系统理论 LST 进阶学习中
- 🧠 **reinforcement-learning/** —— 强化学习
- 🧩 **machine-learning/** —— 机器学习与深度学习
  - resources/ —— 课程资料、参考书、PDF
  - notes/ —— 机器学习 / 深度学习学习笔记
  - experiments/ —— 小实验、训练 demo、数据集说明
- 📄 **paper-notes/** —— 论文精读笔记
- 💻 **code/** —— 实验代码
  - cartpole/ —— 倒立摆 PID LQR MPC 控制
  - astar-parking/ —— A* / Hybrid A* 泊车规划 (Phase 1-6)
    - phase5_learning_heuristic/ —— MLP 学习 `cost_to_go` 启发式
    - phase6_neural_astar_reproduction/ —— Neural A* / CNN heuristic 二维 toy 复现
- 📅 **weekly-summary/** —— 每周学习总结

---

## 📖 当前学习进度

### 🤖 机器人学
- [x] Modern Robotics 第2章 构型空间 C-space
- [x] Modern Robotics 第3章 刚体运动 SO(3) SE(3) 指数坐标 旋量
- [x] Modern Robotics 第9章 轨迹生成
- [x] Modern Robotics 第10章 运动规划
- [ ] Modern Robotics 第11章 机器人控制

### 📐 控制理论

#### 现代控制理论基础 ✅
- [x] 状态空间表达式 $\dot{x}=Ax+Bu$ $y=Cx+Du$
- [x] 状态空间表达式的解 齐次 非齐次 状态转移矩阵
- [x] 李雅普诺夫稳定性 第一法 第二法
- [x] 能控性与能观性 矩阵判据 对偶原理

#### 线性系统理论 LST 🔄
- [x] 第1章 线性系统数学描述
- [x] 第2章 状态空间与传递函数
- [x] 第6章 稳定性分析
- [ ] LQR 线性二次型调节器
- [ ] MPC 模型预测控制

### 🧠 强化学习
- [x] MDP 与贝尔曼方程 值迭代 策略迭代
- [x] Monte Carlo 与 TD 学习
- [x] PPO Actor-Critic 体系
- [ ] 倒立摆 PPO / Actor-Critic 最小实验
- [ ] imitation learning / behavior cloning 基础实验
- [ ] MARL MADDPG MAPPO QMIX

### 🧩 机器学习 / 深度学习
- [x] PyTorch 基础与张量操作
- [x] 监督学习训练流程 Dataset Dataloader Model Loss Optimizer
- [x] 《动手学深度学习》第 2-6 章核心主线
- [x] MLP / CNN 基础与泊车 local map 模板
- [x] Learning A* heuristic / neural planning 初步调研
- [x] 泊车 `cost_to_go` 数据集设计与第一版 MLP heuristic
- [x] learned heuristic 离线评估与排序准确率评估
- [x] 将 learned heuristic 作为 tie-breaker 接回 Hybrid A* 做初步对照
- [x] Neural A* / CNN heuristic 二维 toy 流程初步复现
- [ ] D2L 后续 CNN / Transformer / CV / NLP 快速补全

### 🧪 实验
- [x] A* 泊车规划 (Phase 1-3)
- [x] Phase 4 Hybrid A* + CasADi/IPOPT MPC 闭环泊车
- [x] Phase 5 `cost_to_go` 数据集生成
- [x] 第一版 MLP heuristic 训练
- [x] learned heuristic 离线评估与排序准确率评估
- [x] Hybrid A* + learned heuristic tie-breaker 初步对照实验
- [x] Phase 6 Neural A* / CNN heuristic 二维 toy
- [ ] 倒立摆 PID 控制
- [ ] 倒立摆 LQR 控制
- [ ] 倒立摆 MPC 控制
- [ ] 倒立摆 RL / PPO 控制


---

## 📝 最近更新

- **2026.05 Week 8** 论文资料按方向整理到 `../papers/`；后续路线从 learning heuristic 练习转向 RL / imitation learning / PPO，以及多机器人 formal methods 与 GCS 等 planning 理论资料
- **2026.05 Week 7** 完成 Phase 5 learning heuristic 离线评估与 Hybrid A* tie-breaker 初步对照；完成 Phase 6 Neural A* / CNN heuristic 二维 toy，理解 learning 加速 search 的基本流程
- **2026.04 Week 7** 完成 D2L 第 2-6 章核心主线，启动 Phase 5 learning heuristic；生成 100 次 Hybrid A* 成功路径数据集，训练第一版 MLP `cost_to_go` 模型
- **2026.04 Week 6** 完成 Phase 4 Hybrid A* + CasADi/IPOPT MPC 闭环泊车，成功率 10/10，碰撞 0/10
- **2026.04 Week 5** 精读 MR 第10章，完成 A* 泊车实验 Phase 1-3
- **2026.04 Week 4** 完成 MR 第3章精读 Linear System Theory 第1 2 6章
- **2026.04 Week 3** 现代控制理论 状态空间 稳定性 能控能观性 MR 第2章
- **2026.03 Week 2** 避障算法 APF DWA A* PP RL优化避障论文
- **2026.03 Week 1** RL 入门 MDP 贝尔曼 值迭代 策略迭代 MC TD PPO

---

*最后更新 2026.05.05*
