# Belta, Isler & Pappas 2005：Discrete Abstractions for Robot Motion Planning and Control in Polygonal Environments

对应批注 PDF：

```text
belta-isler-pappas-2005-discrete-abstractions-polygonal-environments-annotated.pdf
```

## 论文定位

这篇论文是从复杂 polygonal environment 到 discrete abstraction / transition system，再到连续控制器实现的桥梁论文。

当前最有用的主线是：

```text
polygonal environment
-> triangulation
-> dual graph
-> language of legal triangle strings
-> local controllers implementing graph transitions
```

## 核心概念

### Qualitative Task

任务不是精确指定连续坐标，而是指定机器人需要到达或避开的区域：

```text
reach region A
avoid forbidden region B
stay inside safe region
```

这与 temporal logic / DFTS 的思想一致：逻辑层关心的是区域、命题和离散 word，而不是连续轨迹的每个坐标。

### Triangulation and Region Labels

论文用三角剖分把多边形环境划分为有限个三角形，并给每个三角形一个符号：

```text
L = {l_1, l_2, ..., l_M}
I(l_i) = triangle l_i 对应的几何区域
P = union of all I(l_i)
```

这对应当前项目中的：

```text
region set R
```

### Dual Graph

论文定义三角剖分的 dual graph：

```text
DG = (L, t)
```

其中：

- node 是 triangle label
- edge / relation `t` 表示两个三角形邻接
- 邻接关系来自共享边界

这可以直接类比为 region transition graph。

### Language of Dual Graph

`L(DG)` 是所有合法 triangle string：

```text
(l_i1, l_i2, ..., l_im)
```

其中相邻两个符号必须满足：

```text
(l_ij, l_i(j+1)) in t
```

也就是说，图上的合法路径就是离散语言。

## Problem 1 的意义

论文不重点研究如何产生高层 string，而是假设高层 string 已经由其他层给出，例如：

```text
shortest path
temporal logic specification
discrete game
```

它重点研究：

```text
given a legal string
-> automatically translate it into robot-control laws
```

这和当前项目的关系是：

```text
DFTS / LTL / GR(1) gives a symbolic strategy
QP / CBF / CLF controller refines it into continuous motion
```

## 两类控制器

论文为每个三角形构造两类局部控制器：

```text
Type I:
move from triangle l to adjacent triangle l'

Type II:
stay inside triangle l
```

一个离散 string 可以这样执行：

```text
l_1 -> l_2: Type I
l_2 -> l_3: Type I
...
l_m:        Type II stay controller
```

当前项目不需要照搬这篇的 affine vector field 控制器，但需要吸收原则：

```text
A graph transition is valid only if it can be implemented by a continuous controller.
```

## Hybrid System 表示

论文把实现过程写成 hybrid system：

```text
continuous state: x in P
discrete location: q_ij
```

其中 `q_ij` 表示：

```text
current triangle = i
intended target triangle = j
```

这个设计很有启发：执行 transition 时，仅知道当前 region 不够，还要知道目标 neighbor / exit facet。

对当前项目，formation-aware transition 可能依赖：

```text
current region
previous entry edge
next exit edge
formation
```

## 与当前项目的直接关系

这篇论文给当前项目提供的不是底层控制算法，而是框架原则：

```text
polygon map
-> triangulation / region decomposition
-> dual graph / region graph
-> legal region strings
-> controller-realizable transitions
```

当前项目要在此基础上增加：

```text
formation feasibility
through-width / bottleneck
task labels
unsafe labels
QP / CBF / CLF controller refinement
```

因此新的 transition system 不应只是 adjacency graph，而应是：

```text
geometry-aware + formation-aware + controller-aware transition system
```

## 当前阅读结论

已经抓住的重点：

- `triangle = qualitative state`
- `dual graph = discrete abstraction`
- `language of DG = legal triangle strings`
- `given string -> controller sequence`
- `transition must be implementable by continuous control`

后续不需要深挖：

- affine vector field 具体推导
- bisimulation 证明
- unicycle feedback linearization
- smoothness optimization

对当前研究最有用的一句话：

```text
The allowed transitions in a symbolic system should be exactly those that the continuous robot system can implement.
```
