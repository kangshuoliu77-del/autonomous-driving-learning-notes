# Phase 2: Configuration Space (C-Space) & 8-Connected A* 🚗

这是自动泊车项目的第二阶段成果：**基于配置空间膨胀与 8 连通的 A* 算法**。

## 🎯 阶段目标
本阶段在 Phase 1 的基础上，引入了《Modern Robotics》第 10.4 节的核心思想，重点解决了路径安全余量与移动自由度的问题。

### 核心改进
1.  **工作空间到配置空间的转换 (Workspace to C-Space)**：通过**障碍物膨胀 (Inflation)** 逻辑，根据车辆半径预留安全边距，避免了 Phase 1 中路径紧贴障碍物的问题。
2.  **8 连通运动模型**：从 4 连通升级为 8 连通，允许节点向对角线方向移动。
3.  **非均匀代价计算**：严格遵循物理距离，将水平/垂直移动代价设为 $1.0$，对角线移动代价设为 $\sqrt{2} \approx 1.414$。
4.  **启发式函数适配**：继续沿用**欧几里得距离**，确保在 8 连通环境下的搜索效率与最优性。

## 📂 文件清单
- `node.py`: 升级节点结构，新增 `step_cost` 属性以适配非均匀代价。
- `map.py`: 核心新增 `get_inflated_map` 函数，实现障碍物自动膨胀。
- `heuristic.py`: 计算欧几里得距离，引导搜索方向。
- `astar.py`: 算法核心，支持 8 方向邻居扩展及 $g$ 值权重累加。
- `visualize.py`: 新增 `compare_inflation` 接口，支持原图与膨胀图的并排对比。
- `main.py`: 集成地图膨胀逻辑与高分辨率地图生成的程序入口。

## 📊 运行结果

下图展示了在配置空间中规划出的路径。红色路径自动绕开了膨胀后的黑色区域，确保了车辆在原始环境（Workspace）中行驶时的安全性：

![Phase 2 Result](https://github.com/kangshuoliu77-del/autonomous-driving-learning-notes/blob/main/code/astar-parking/phase2_inflated_astar/result.png)

*(左侧为原始工作空间，右侧为膨胀后的配置空间及规划出的安全路径)*

## 🚸 存在的问题（Phase 3 的切入点）
1.  **运动学约束缺失**：路径虽然平滑，但未考虑车辆的最小转弯半径（非完整性约束）。
2.  **姿态表达不足**：目前仅处理了位置 $(x, y)$，尚未引入车辆的朝向角 $\theta$（即 $SE(2)$ 空间规划）。

---
*下一步计划：进入 [Phase 3: Kinematic Constraints](../phase3_kinematics/)，引入车辆运动学模型与旋转矩阵。*
