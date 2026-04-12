# 🧮 状态空间表达式的解

---

## 🔹 齐次状态方程 $u=0$

$\dot{x} = A x$

**解的形式** $x(t) = e^{At} x(0)$

**状态转移矩阵** $\Phi(t) = e^{At}$

$x(t) = \Phi(t) x(0)$

---

## 🔹 状态转移矩阵性质

1. $\Phi(0) = I$ 初始时刻状态不变
2. $\dot{\Phi}(t) = A\Phi(t)$ 满足原方程
3. $\Phi(t_1+t_2) = \Phi(t_1)\Phi(t_2)$ 时间可叠加
4. $\Phi^{-1}(t) = \Phi(-t)$ 可逆

---

## 🔹 典型矩阵指数

**对角阵** $A = [\lambda_1 \ 0; 0 \ \lambda_2] \Rightarrow e^{At} = [e^{\lambda_1 t} \ 0; 0 \ e^{\lambda_2 t}]$

**Jordan块** $A = [\lambda \ 1; 0 \ \lambda] \Rightarrow e^{At} = e^{\lambda t}[1 \ t; 0 \ 1]$

---

## 🔹 非齐次状态方程 $u \neq 0$

$\dot{x} = A x + B u$

**核心公式**

$x(t) = \Phi(t)x(0) + \int_0^t \Phi(t-\tau) B u(\tau) d\tau$

- **零输入响应** $\Phi(t)x(0)$ 由初始状态驱动
- **零状态响应** 积分项 由历史控制输入驱动

---

## 🔹 与 RL 对照

| 线性系统 | 强化学习 |
|:---|:---|
| $\dot{x} = Ax + Bu$ | $s_{t+1} = f(s_t, a_t)$ |
| 确定性白盒模型 | 随机性黑盒模型 |
| $x(t) = \Phi x_0 + \int \Phi B u$ | $V(s_t) = r_t + \gamma V(s_{t+1})$ |

**思想同源** 当前状态 = 初始影响 + 历史累积

---

## 🔹 小结

- 齐次解 $x(t) = e^{At}x(0)$
- 状态转移矩阵 $\Phi(t) = e^{At}$
- 非齐次解 = 零输入响应 + 零状态响应
- 与贝尔曼方程思想一致 当前 = 初始 + 累积
