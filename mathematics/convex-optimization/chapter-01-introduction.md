# Chapter 1: Introduction

Optimization problems package choices as a variable vector `x`, define what should be minimized as an objective function `f0(x)`, and define what cannot be violated as constraints `fi(x) <= bi`.

The main map:

- Linear programming and least squares are basic tractable examples.
- General nonlinear optimization is broad and often difficult.
- Convex optimization is special because local optimality implies global optimality.
- The hard part of convex optimization is usually modeling the problem into a convex form, not pressing the solver button.

For the current TRO/GCS project, the important point is that complex planning problems become more controllable when the search space is represented by convex sets.

