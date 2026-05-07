# 数学笔记

这个目录用来整理我在机器人、自动驾驶和科研路线中需要补的数学基础。

当前最优先的是凸优化:

- formal multi-robot planning and control
- 复杂环境的 convex decomposition
- Graphs of Convex Sets
- 基于 CBF / CLF / QP 的控制细化
- optimization-based motion planning

## 目录结构

- `convex-optimization/`：Boyd《Convex Optimization》笔记，凸集、凸函数、标准凸问题、对偶理论，以及和 GCS 的联系。
- `numerical-optimization/`：数值分析、线性规划、非线性规划、数值求解器和优化算法。
- `optimal-control/`：Bellman 原理、HJB、Pontryagin maximum principle、LQR、MPC 和机器人运动最优性。

## 当前重点

围绕当前 TRO/GCS 方向，短期阅读顺序是：

1. Boyd 第 1 章：建立优化问题的大图。
2. Boyd 第 2 章：凸集、halfspace、polyhedron、convex hull、separating hyperplane。
3. Boyd 第 3 章：凸函数。
4. Boyd 第 4 章：标准凸优化问题，尤其是 LP 和 QP。
5. Boyd 第 5 章：对偶理论和 KKT，等建模图景清楚后再深入。
