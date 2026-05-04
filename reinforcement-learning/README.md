# Reinforcement Learning

这个目录用于记录强化学习与后续 planning + RL / MARL 相关学习。

## 当前资料

- `books/Book-all-in-one.pdf`：Shiyu Zhao, *Mathematical Foundations of Reinforcement Learning*
  - Week 1 强化学习入门的主要资料
  - 覆盖 MDP、state/action/reward、return、Bellman equation、state/action value、optimality、policy/value iteration、Monte Carlo、TD、Actor-Critic、PPO 等基础主线
- `books/SuttonBartoIPRLBook2ndEd.pdf`：Sutton & Barto, *Reinforcement Learning: An Introduction*
  - 后续系统学习强化学习的主教材
- `books/2011.00583v5.pdf`：*Game-Theoretic Multiagent Reinforcement Learning*
  - 后续 MARL / 多车交互决策方向参考

## 与当前项目的关系

当前自动泊车实验已经完成传统规划控制基线：

```text
Hybrid A* -> CasADi/IPOPT MPC
```

后续强化学习相关路线主要围绕：

```text
expert trajectory
-> imitation learning / pre-train
-> PPO / RL fine-tuning in simulation
```

强化学习不是替代当前 planning 主线，而是作为后续 planning + learning 的延伸。
