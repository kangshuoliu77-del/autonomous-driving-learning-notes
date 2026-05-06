# Chapter 2: Convex Sets

Current reading goal: understand the geometry needed for convex decomposition and Graphs of Convex Sets.

## Must Read

### 2.1 Affine and Convex Sets

Key ideas:

- line
- line segment
- affine set
- convex set
- convex combination
- affine hull
- convex hull

Minimum target: understand why a convex polygon is a convex set, and why a convex region can become one node in a GCS graph.

### 2.2 Important Examples

Most important formulas:

```text
hyperplane: a^T x = b
halfspace:  a^T x <= b
polyhedron: Ax <= b
```

For planning, a convex polygon or convex polytope is often represented as the intersection of halfspaces.

### 2.3 Operations That Preserve Convexity

Most important facts:

- The intersection of convex sets is convex.
- Affine mappings preserve convexity.

These facts explain why multiple linear constraints can still define one convex feasible region.

### 2.5 Separating and Supporting Hyperplanes

Read for intuition, not proof.

The key idea is that convex sets can be separated or supported by hyperplanes. This connects to linear obstacle boundaries, safe regions, and geometric constraints.

## Can Skim For Now

- 2.4 generalized inequalities
- 2.6 proper cones
- proof details of separation theorems

## Minimum Completion Standard

After this chapter, I should be able to explain:

1. What a convex set means geometrically.
2. What convex hull means.
3. Why `Ax <= b` can represent a convex polygon or polyhedron.
4. Why intersecting halfspaces still gives a convex set.
5. Why GCS needs convex sets rather than arbitrary nonconvex regions.

