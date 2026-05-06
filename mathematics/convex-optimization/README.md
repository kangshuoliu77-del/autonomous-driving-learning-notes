# 凸优化

这个目录用来整理 Boyd 和 Vandenberghe 的 *Convex Optimization* 学习笔记，以及它和机器人规划的联系。

## 为什么重要

当前 CDC -> TRO 项目需要凸优化，是因为原来的 multi-robot formation 环境比较简单，现在要扩展到更复杂的环境。

核心想法是：

```text
复杂非凸环境
-> 把自由空间分解成多个凸区域
-> 用线性不等式表示每个凸区域
-> 把凸区域连接成图
-> 在凸集合内部优化连续路径
```

这就是 Graphs of Convex Sets 和 convex decomposition 背后的数学语言。

## 笔记

- `chapter-01-introduction.md`：第 1 章文字整理，建立优化问题的大图。
- `boyd-chapter-01-notes.pdf`：Boyd 第 1 章 1.1-1.4 的学习笔记。
- `chapter-02-convex-sets.md`：第 2 章阅读重点，凸集、halfspace、polyhedron、convex hull，以及和 GCS 有关的几何直觉。
