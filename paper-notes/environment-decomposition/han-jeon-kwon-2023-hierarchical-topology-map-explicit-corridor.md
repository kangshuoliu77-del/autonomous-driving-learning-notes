# Han, Jeon & Kwon 2023: Hierarchical Topology Map with Explicit Corridor

对应批注 PDF：

```text
han-jeon-kwon-2023-hierarchical-topology-map-explicit-corridor-annotated.pdf
```

## 论文定位

这篇论文提出 HTM-EC，目标是从 occupancy grid map 中提取 skeleton / topology graph，再利用 explicit corridor 做全局路径规划和路径优化。

对当前研究，它不是最终理论框架，而是 ECM / corridor skeleton 路线的重要工程参考。它最有价值的地方是说明：

```text
occupancy grid map
-> skeleton extraction
-> topology graph
-> explicit corridor annotation
-> on-skeleton path
-> off-skeleton path refinement
```

这和当前复杂环境扩展中的 map abstraction 问题高度相关。

## 核心结构

### HTM

原始 HTM 可以写成：

```text
M_ht = {G, Q}
```

其中：

- `Q` 是 ordered skeleton points；
- `G=(N,E)` 是 topology graph；
- topology node 来自 skeleton 的 terminal / intersection / merging points；
- graph edge 是两个 topology node 之间的一串 skeleton points。

论文把 edge 写成：

```text
E_ij = <N_i, N_j, I_ij, C_ij>
```

其中 `I_ij` 记录这条 topology edge 对应哪些 skeleton points，`C_ij` 是沿这段 skeleton 的代价。

### HTM-EC

HTM-EC 在 HTM 上加入 explicit corridor annotation。每个 skeleton point 对应：

```text
b(k) = {q(k), r(k), O(k)}
```

其中：

- `q(k)` 是第 `k` 个 skeleton point；
- `r(k)` 是它到最近障碍物的距离；
- `O(k)` 是最近障碍物点集合。

所以：

```text
B = {b(k)}
M_ht^ec = {G, B}
```

这和 ECM 的核心思想相近：skeleton / medial axis 不只是线，还带有 nearest-obstacle / clearance 信息。

## 路径规划流程

论文的 planning 分三步：

```text
1. 把 start / goal 插入 topology graph；
2. 在 topology graph 上搜索 on-skeleton path；
3. 沿 skeleton path 诱导出的 corridor 做 discretization，再用 dynamic programming 得到 off-skeleton path。
```

对当前项目来说，最重要的是前两步的结构：

```text
large map
-> small topology graph
-> corridor edge with clearance information
```

这支持我们把复杂地图先压成 corridor graph，而不是直接在 dense grid 或 raw triangles 上做高层 DFTS。

## 对当前研究的直接用法

这篇文章可以借鉴四点：

1. 从 OGM 或复杂地图中提取 skeleton / topology graph。
2. 把一条 graph edge 理解为 corridor，而不是普通线段。
3. 给 corridor edge 保存 underlying skeleton points 和 clearance / nearest-obstacle annotation。
4. 先在 topology graph 上做高层规划，再在 corridor tube 内做几何 refinement。

对应当前 TRO 扩展，可以改写成：

```text
corridor graph G_c = (V_c, E_c)

edge e in E_c:
    centerline / skeleton segment
    nearest-obstacle annotation
    bottleneck clearance
    allowed formations
    local controller / QP feasibility flag
```

这比直接问“哪些 triangle 应该 merge”更自然，因为 formation 能否通过主要由 corridor 的 bottleneck width / clearance 决定。

## 和 ECM 2016 的区别

ECM 2016 更理论干净：

```text
polygonal obstacles
-> segment Voronoi diagram / medial axis
-> nearest-obstacle annotation
-> corridor map
```

HTM-EC 2023 更工程可落地：

```text
occupancy grid map
-> distance field + image thinning
-> topology graph
-> explicit corridor
-> dynamic programming refinement
```

当前判断：

- 理论表述应优先依靠 ECM / medial axis / generalized Voronoi graph；
- demo 或工程 prototype 可以借鉴 HTM-EC 的 OGM skeleton pipeline；
- 如果使用 image thinning，需要承认它是近似 skeleton，不是 exact segment Voronoi / exact ECM。

## 局限

这篇文章不直接解决当前项目的核心难点：

- 它是 single mobile robot global path planning；
- 没有 multi-robot formation；
- 没有 formation switching；
- 没有 LTL / GR(1) synthesis；
- 没有 QP / CBF / CLF control refinement；
- 没有 symbolic transition soundness。

另外，论文自己也提到 grid skeleton 会带来误差：有些 skeleton point 可能无法精确找到最近障碍物点。Voronoi / exact medial axis 在理论上更干净。

## 对当前 TRO 主线的结论

HTM-EC 读完后，当前主线更明确：

```text
complex environment
-> clearance / explicit-corridor graph
-> formation-aware transition candidates
-> geometric / formation / controller pruning
-> verified DFTS
-> GR(1) / LTL synthesis
-> QP / CBF / CLF refinement
```

状态空间仍建议写成：

```text
S = (V_c union E_c) x F
```

其中：

- `(v,f)` 表示在 junction / terminal / task / switch node 附近；
- `(e,f)` 表示 formation `f` 正在 corridor tube 中通过；
- `(e,f)` 不应解释成 edge midpoint。

这篇文章证明 corridor / topology representation 对路径规划有工程价值，但当前项目真正的创新点仍应放在：

```text
clearance-aware
formation-aware
controller-refinable
transition system construction
```

## 当前阅读结论

后续不需要深挖本文的 allowable speed 和 dynamic programming 公式。那些主要服务单机器人 time-optimal path refinement。

需要保留的是：

```text
HTM-EC = OGM skeleton + topology graph + explicit corridor annotation
```

它可以作为当前 ECM / GVD / corridor map 调研线的重要参考，也可以作为未来实验 baseline 或 engineering fallback。
