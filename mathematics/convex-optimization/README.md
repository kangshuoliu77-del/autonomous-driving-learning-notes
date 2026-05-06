# Convex Optimization

This folder is for notes on Boyd and Vandenberghe's *Convex Optimization* and its connection to robot planning.

## Why This Matters

The current CDC-to-TRO project needs convex optimization because the original simple multi-robot formation environment must be extended to more complex environments.

The key idea is:

```text
complex nonconvex environment
-> decompose free space into convex regions
-> represent each region with linear inequalities
-> connect convex regions as a graph
-> optimize continuous paths inside convex sets
```

This is the mathematical language behind Graphs of Convex Sets and convex decomposition.

## Notes

- `chapter-01-introduction.md`: optimization problem map.
- `boyd-chapter-01-notes.pdf`: my Chapter 1 notes for Boyd sections 1.1-1.4.
- `chapter-02-convex-sets.md`: convex sets, halfspaces, polyhedra, convex hulls, and geometry for GCS.
