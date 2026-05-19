# Shewchuk 1996：Triangle: Engineering a 2D Quality Mesh Generator and Delaunay Triangulator

对应批注 PDF：

```text
shewchuk-1996-triangle-2d-mesh-generator-delaunay-triangulator-annotated.pdf
```

## 论文定位

这篇不是当前项目的理论主线论文，而是工具链论文。它说明 Triangle 这个 2D mesh / triangulation 工具如何生成：

```text
Delaunay triangulation
constrained Delaunay triangulation
quality triangular meshes
```

当前项目最需要的是：

```text
polygon map + obstacle boundaries
-> constrained triangulation
-> free-space triangles
-> triangle adjacency graph
```

## 当前项目需要掌握的内容

### Constrained Delaunay Triangulation

普通 Delaunay triangulation 只处理点，不能保证墙、障碍物边界、外边界被保留。

当前项目需要的是 constrained Delaunay triangulation：

```text
constrained edge = cannot-cross boundary
```

例如：

```text
wall
outer boundary
obstacle boundary
unsafe-region boundary
```

这些边不能被删除、翻转或穿越。

### PSLG 输入

Triangle 的输入是 PSLG：

```text
PSLG = vertices + segments
```

当前项目的地图可以整理为：

```text
outer boundary vertices
outer boundary segments
obstacle vertices
obstacle segments
hole points inside obstacles
```

### Holes

Triangle 通过用户指定的 hole point 删除洞内三角形。

项目含义：

```text
obstacle polygon 内部放一个 hole point
Triangle 删除 obstacle 内部 triangles
保留 free-space triangles
```

前提是 obstacle boundary segments 必须闭合，否则删除会漏出去。

### Triangle Graph

Triangle 输出三角形后，可以把每个三角形当作一个 region：

```text
triangle = discrete region/state
```

边的解释：

```text
shared unconstrained edge
-> candidate transition

shared constrained edge
-> barrier / no transition
```

因此 Triangle 负责几何分解，当前项目负责在此基础上构造 transition system。

## 与当前项目的关系

当前项目第一版建议采用：

```text
polygonal environment
-> constrained triangulation
-> triangle adjacency graph
-> formation-aware transition filtering
-> DFTS / temporal logic planning
-> QP / CBF / CLF controller execution
```

Triangle 对应第一步：

```text
map geometry -> triangle regions
```

它不直接解决：

```text
formation feasibility
through-width
controller feasibility
temporal logic synthesis
```

这些是当前项目真正需要继续做的部分。

## 需要快速带过的内容

这些内容不用深读：

- divide-and-conquer / sweepline / incremental insertion 速度比较
- quad-edge 与 triangle-based data structure 的实现细节
- ghost triangles
- Ruppert refinement 的证明
- encroached segment / bad triangle 的完整推导
- exact arithmetic 和 robust adaptive predicates 的实现
- Appendix implementation notes

只需要知道：

```text
Triangle 比自己手写 triangulation 更鲁棒。
```

## 当前阅读结论

已经抓住的重点：

- Triangle 是成熟 2D constrained triangulation 工具
- 输入是 PSLG：vertices + segments
- obstacle / wall boundary 应作为 constrained segments
- holes 用 hole point 删除
- 输出 free-space triangles
- triangle adjacency graph 可以作为 transition system 的几何骨架

下一步应该从读论文转向最小 demo：

```text
input polygon + obstacles
-> call Triangle / Python wrapper
-> plot triangulation
-> extract triangle neighbors
-> mark constrained edges
-> build candidate transition graph
```
