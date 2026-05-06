# Mathematics Notes

This directory collects the math background needed for my robotics and autonomous driving research path.

The current priority is convex optimization, because it directly supports the CDC-to-TRO extension line:

- formal multi-robot planning and control
- convex decomposition of complex environments
- Graphs of Convex Sets
- CBF / CLF / QP based control refinement
- optimization-based motion planning

## Structure

- `convex-optimization/`: Boyd Convex Optimization notes, convex sets, convex functions, standard convex problems, duality, and links to GCS.
- `numerical-optimization/`: numerical analysis, linear programming, nonlinear programming, numerical solvers, and optimization algorithms.
- `optimal-control/`: Bellman principle, HJB, Pontryagin maximum principle, LQR, MPC, and robot motion optimality.

## Current Focus

For the current TRO/GCS direction, the short-term reading order is:

1. Boyd Chapter 1: optimization problem map.
2. Boyd Chapter 2: convex sets, halfspaces, polyhedra, convex hulls, and separating hyperplanes.
3. Boyd Chapter 3: convex functions.
4. Boyd Chapter 4: standard convex optimization problems, especially LP and QP.
5. Boyd Chapter 5: duality and KKT, only after the modeling picture is clear.

