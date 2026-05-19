# Choset & Pignon 1997：Coverage Path Planning: The Boustrophedon Cellular Decomposition

对应批注 PDF：

```text
choset-pignon-1997-boustrophedon-cellular-decomposition-annotated.pdf
```

## 论文定位

这篇论文的原始任务是 coverage path planning，但当前最有用的部分不是覆盖路径，而是：

```text
free space
-> exact cellular decomposition
-> cells
-> adjacency graph
```

它提供了复杂环境表示到离散图抽象的一条经典路线。

## 核心思想

### Exact Cellular Decomposition

论文把自由空间分成互不相交的 cell，并要求所有 cell 的并集正好等于原始 free space：

```text
free space = union of cells
```

每个 cell 可以看成一个离散状态。

### Adjacency Graph

论文把每个 cell 表示成图中的一个 node，相邻 cell 之间连一条 edge：

```text
cell -> node
adjacent cells -> edge
```

这就是从连续环境到离散 transition graph 的关键步骤。

### Boustrophedon Decomposition

Boustrophedon decomposition 是 trapezoidal decomposition 的改进。它不是在每个几何顶点都切 cell，而是只在 sweep line 的连通性发生变化时切：

```text
IN event:
one connected slice component splits into two

OUT event:
two connected slice components merge into one

MIDDLE event:
connectivity unchanged, only update current cell
```

核心原则：

```text
open / close cells only when slice connectivity changes
```

## 与 Triangulation 的区别

Triangulation：

```text
polygon map -> triangles -> triangle graph
```

优点是三角形天然凸、邻接边清楚、formation through-width 比较容易定义。

Boustrophedon：

```text
free space -> connectivity-based cells -> adjacency graph
```

优点是 cell 数量更少，更符合房间、走廊、分叉、合并等环境连通结构。

缺点是 cell 不一定凸，形状可能不规则，直接用于 QP / GCS / convex optimization 不如三角形自然。

## 与当前项目的关系

当前项目的主线是：

```text
complex environment
-> region decomposition
-> transition system
-> DFTS / temporal logic / formation planning
-> QP / CBF / CLF controller execution
```

这篇论文提供的是 region decomposition 和 adjacency graph 的经典框架。

但它的 coverage path 部分不是当前重点。当前更应该吸收的是：

```text
continuous environment problem
-> finite graph problem
```

以及：

```text
transition graph should preserve connectivity changes,
not arbitrary grid-level geometry details.
```

## 当前阅读结论

已经抓住的重点：

- exact cellular decomposition 将 free space 分成 cells
- cell 可以作为 discrete state
- adjacency graph 可以作为 transition system 的几何骨架
- boustrophedon 只在 sweep line 连通性变化时切 cell
- cell 更少，transition graph 更简洁

后续不需要深挖：

- coverage path 的具体 back-and-forth 执行
- exhaustive walk / TSP 细节
- 实验中的清扫轨迹细节
- FLOOR / CEILING pointer 级实现细节

对当前研究最有用的一句话：

```text
Cell decomposition turns a continuous free space into a finite adjacency graph, but the final transition system must still be filtered by formation and controller feasibility.
```
