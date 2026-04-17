# 自动泊车 Phase 3：基于运动学的 Hybrid A* 算法实现笔记 🏎️

本篇笔记详细记录了自动泊车项目 **Phase 3** 中的核心数学模型与算法原理，涵盖了从《Modern Robotics》理论到实际工程实现的转化过程。

---

## 1. $SE(2)$ 特殊欧几里得群与刚体位姿
在 Phase 1 & 2 中，我们将车辆简化为点或等效圆。而在 Phase 3，为了适配真实的泊车场景，必须考虑车辆的**航向角（Heading）**，即在 $SE(2)$ 空间内描述车辆。

### 1.1 状态表达
车辆的状态由位姿向量 $q$ 表示：
$$q = [x, y, \theta]^T \in SE(2)$$
* **$(x, y)$**：车辆后轴中心的坐标。
* **$\theta$**：车辆纵轴与世界坐标系 $X$ 轴的夹角。

### 1.2 刚体变换与碰撞检测
为了实现精确的碰撞检测，我们需要将车辆包络（矩形）从局部坐标系 $\{b\}$ 转换到全局坐标系 $\{s\}$。利用齐次变换矩阵 $T_{sb}$：

$$
T_{sb} = \left[
\begin{array}{ccc}
\cos\theta & -\sin\theta & x \\
\sin\theta & \cos\theta & y \\
0 & 0 & 1
\end{array}
\right]
$$

通过该矩阵，我们可以实时计算车身四个顶点在世界地图中的绝对位置，从而实现从“点圆检测”到“多矩形包络检测”的升级。

---

## 2. 车辆运动学模型 (Kinematic Bicycle Model)
由于汽车受到**非完整性约束（Nonholonomic Constraints）**，它无法像 Phase 2 中的 8 连通模型那样原地旋转或平移。

### 2.1 运动学方程
我们采用单轨模型（自行车模型）作为系统的状态转移方程：

$$\dot{x} = v \cos(\theta)$$
$$\dot{y} = v \sin(\theta)$$
$$\dot{\theta} = \omega = \frac{v \tan(\phi)}{L}$$

* **$v$**：车辆线速度（支持正负，对应前进与倒车）。
* **$\omega$**：角速度，即车身转向的快慢。
* **$L$**：车辆轴距（Wheelbase）。
* **$\phi$**：前轮转角（Steering angle），受机械极限限制 $|\phi| \leq \phi_{max}$。

### 2.2 最小转弯半径
由上述方程可推导出轨迹曲率 $\kappa = \frac{\omega}{v} = \frac{\tan(\phi)}{L}$，对应的最小转弯半径 $R_{min}$ 为：

$$R_{min} = \frac{L}{\tan(\phi_{max})}$$

这决定了 Hybrid A* 在搜索时，“运动基元”扩展所能达到的最大曲率极限。

---

## 3. Hybrid A* 算法逻辑核心
Hybrid A* 的精髓在于它结合了**连续空间的运动轨迹**与**离散空间的状态管理**。

### 3.1 状态空间离散化与剪枝 (Pruning)
为了防止搜索树在连续空间无限膨胀，我们将连续坐标投影到 3D 栅格桶中进行剪枝：
* **XY 离散化**：将 $(x, y)$ 投影到栅格分辨率 `res_xy`。
* **Theta 离散化**：将 $\theta$ 投影到角度分辨率 `res_theta`（如 2° 或 5°）。
* **规则**：若新状态落入已访问过的 3D 桶且路径代价（G值）更高，则执行剪枝。

### 3.2 节点扩展 (Primitive Expansion)
在每一个 Step，算法尝试不同的前轮转角 `phi ∈ {-phi_max, 0, phi_max}` 以及不同的方向 `v ∈ {v_forward, v_backward}`，生成 6 组符合物理特性的**运动基元**。
角度更新遵循： 
**&theta;<sub>new</sub> = &theta; + &omega; &middot; dt**

### 3.3 代价函数设计 (Cost Function)
$$TotalCost = G(q) + H(q)$$
为了诱导算法生成“老司机”般的路径，G 值除了包含物理距离，还额外引入：
* **换挡惩罚 (Gear Switch Cost)**：当 $v$ 正负号切换时增加巨额惩罚，显著减少无意义的揉库动作。

