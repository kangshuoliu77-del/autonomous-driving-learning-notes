# Demyen & Buro 2006：Efficient Triangulation-Based Pathfinding

## 论文定位

这篇论文关注如何用 constrained Delaunay triangulation 表示复杂多边形环境，并在三角剖分图上做更高效的路径搜索。

对当前研究最有用的不是 TA*/TRA* 搜索细节，而是它提供了一条从复杂地图到离散 transition system 的路线：

```text
polygon map
-> constrained triangulation
-> triangle graph
-> reduced / abstract graph
-> width-aware passability
```

## 核心概念

### Polygon World

原始环境由多边形边界和障碍物线段描述。它对应复杂环境的输入地图。

和 grid world 相比，多边形表示可以更精确地表示斜边、长走廊、尖角和不规则障碍物。

### Constrained / Unconstrained Edge

- `constrained edge`：障碍物或环境边界，不能跨越
- `unconstrained edge`：为了完成三角剖分新增的自由空间内部边，可以跨越

这可以直接用于建立 region adjacency：

```text
two triangles share an unconstrained edge
=> candidate transition
```

### Triangle Graph

每个三角形作为一个节点，相邻三角形之间通过 unconstrained edge 连接。

这是从连续多边形地图到离散图结构的第一步。

## 非点机器人与通过宽度

论文考虑圆形物体的半径 `r`。如果物体要从一个三角形的一条边进入、另一条边出去，需要检查这个三角形内部的 through-width 是否至少为 `2r`。

这个思想比只看共享边宽度更准确：

```text
shared edge width
```

只能说明门口够不够宽，而不能说明物体能否在区域内部从入口走到出口。

更合理的判断是：

```text
through_width(region, entry_edge, exit_edge) >= required_width
```

对编队规划，可以改写为：

```text
allowed(R_prev, R_i, R_next, formation)
= through_width(R_i, entry_edge, exit_edge)
  >= required_width(formation)
```

整条 channel 的可通过性可以用局部 through-width 的最小值近似：

```text
channel_width = min_i through_width(R_i, entry_i, exit_i)
```

## Channel 思想

三角剖分图搜索得到的不是一条连续轨迹，而是一串相邻三角形：

```text
T_1 -> T_2 -> ... -> T_k
```

这些三角形合起来形成一个 channel / corridor。之后可以在 channel 内生成连续路径或控制轨迹。

这和当前研究的两层结构一致：

```text
symbolic planning gives a region sequence
controller / QP refines it into continuous motion
```

Modified funnel algorithm 可以在 channel 内求几何最短路，但当前阶段不需要深挖。更重要的是保留 channel 作为下层控制的几何约束。

## Triangulation Graph Reduction

论文把三角形按 degree 分成几类：

- `degree-0`：封闭区域，没有出口
- `degree-1`：dead end
- `degree-2`：corridor
- `degree-3`：junction / decision point

Fig. 3 的核心意思是：原始 triangle graph 中大量细碎三角形可以压缩成更抽象的 corridor-junction graph。

对当前研究的启发是：

```text
complex environment should not only be decomposed into cells;
it should also be abstracted into semantic graph structures.
```

需要保留的结构包括：

- task / proposition labeled regions
- start and goal regions
- unsafe regions
- junctions
- narrow passages / choke points
- formation-changing locations

因此不能直接照搬论文的 reduction。论文的 reduction 是 pathfinding-oriented；当前研究需要 label-preserving 和 formation-aware reduction。

## Further Reductions

论文还提到可以把双连通分量进一步压缩成 room-like components，并缓存入口点之间的最佳路径。

当前阶段只作为后续方向：

```text
Level 0: polygon map
Level 1: triangle / convex cells
Level 2: corridor-junction graph
Level 3: task-aware transition system
```

第一版实现不必做多层抽象，先完成 triangle graph 和 formation-aware transition feasibility。

## 对当前研究的直接用法

这篇论文可以直接借鉴四个方法思想：

1. 用 constrained triangulation 把 polygon map 分解成 triangle cells。
2. 用 unconstrained shared edge 建立候选 region transition。
3. 用 through-width / bottleneck 判断非点机器人或编队是否可通过。
4. 用 degree 分类识别 dead end、corridor、junction、choke point。

对应的第一版流程：

```text
polygon map
-> constrained triangulation
-> triangle cells R
-> adjacency graph E_R
-> compute through-width / bottleneck information
-> define formation required_width
-> build formation-aware transition system
-> connect to DFTS / LTL / QP framework
```

## 当前判断

这篇论文是复杂环境表示阶段的重点参考。它不直接解决 temporal logic synthesis 或 controller design，但很好地回答了：

```text
How to turn a complex polygonal environment into a compact,
geometry-aware transition system?
```

后续应把它和 cell decomposition、IRIS、GCS 分开定位：

- triangulation：第一版复杂 polygon map 分解和 region graph
- IRIS：生成更大 convex regions 的可选方案
- GCS：后续把 convex regions 和 optimization-based planning 接起来
- CDC framework：保留 symbolic synthesis + QP control refinement 主线
