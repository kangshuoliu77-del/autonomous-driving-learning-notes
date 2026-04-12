# 🚗 自动驾驶学习笔记 autonomous-driving-learning-notes

> 系统记录从零学习自动驾驶、控制理论、强化学习和机器人的过程

---

## 📂 仓库结构

- 🤖 **robotics/** —— 机器人学
  - modern-robotics/ —— Modern Robotics 读书笔记
- 📐 **control-theory/** —— 控制理论
  - 现代控制理论基础 状态空间 稳定性 能控能观
  - 线性系统理论 LST 进阶学习中
- 🧠 **reinforcement-learning/** —— 强化学习
- 📄 **paper-notes/** —— 论文精读笔记
- 💻 **code/** —— 实验代码
  - cartpole-pid/ —— 倒立摆 PID 控制
  - cartpole-lqr/ —— 倒立摆 LQR 控制
  - cartpole-mpc/ —— 倒立摆 MPC 控制
  - astar-parking/ —— A* 狭窄空间规划
- 📅 **weekly-summary/** —— 每周学习总结

---

## 📖 当前学习进度

### 🤖 机器人学
- [x] Modern Robotics 第2章 构型空间 C-space
- [x] Modern Robotics 第3章 刚体运动 SO(3) SE(3) 指数坐标 旋量
- [ ] Modern Robotics 第9章 轨迹生成
- [ ] Modern Robotics 第10章 运动规划
- [x] Modern Robotics 第11章 机器人控制 PID 误差动力学

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
- [ ] MARL MADDPG MAPPO QMIX

### 🧪 实验
- [ ] 倒立摆 PID 控制
- [ ] 倒立摆 LQR 控制
- [ ] 倒立摆 MPC 控制
- [ ] A* 狭窄空间规划

---

## 📝 最近更新

- **2026.04 Week 5** 搭建学习仓库 上传 MR 第3章手写笔记 补全 Week 1-5 周报
- **2026.04 Week 4** 完成 MR 第3章精读 Linear System Theory 第1 2 6章
- **2026.04 Week 3** 现代控制理论 状态空间 稳定性 能控能观性 MR 第2 11章
- **2026.03 Week 2** 避障算法 APF DWA A* PP RL优化避障论文
- **2026.03 Week 1** RL 入门 MDP 贝尔曼 值迭代 策略迭代 MC TD PPO

---

*最后更新 2026.04*
