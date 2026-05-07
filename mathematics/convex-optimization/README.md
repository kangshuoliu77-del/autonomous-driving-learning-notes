# 凸优化

这个目录用来整理 Boyd 和 Vandenberghe 的 *Convex Optimization* 学习笔记，以及它和机器人规划的联系。

## 为什么重要

当前多机器人 formal methods / motion planning 学习需要凸优化，是因为复杂环境规划通常需要把非凸空间拆分成更容易处理的凸区域。

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
- `boyd-chapter-02-notes.pdf`：Boyd 第 2 章 2.1、2.2、2.3、2.5 的学习笔记。
