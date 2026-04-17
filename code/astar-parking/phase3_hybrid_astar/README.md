# Phase 3: Hybrid A* Path Planning & SE(2) Space 🏎️

这是自动泊车项目的第三阶段成果：**基于混合 A\* (Hybrid A\*) 算法的非完整性约束路径规划**。

[点击查看 Phase 3 运动学模型与算法学习笔记](https://github.com/kangshuoliu77-del/autonomous-driving-learning-notes/blob/main/code/astar-parking/phase3_hybrid_astar/Phase3_HybridAStar_Notes.md)

## 🎯 阶段目标
本阶段实现了从“栅格寻路”到“真实车辆运动学规划”的质变。重点解决了路径在物理上的**可行驶性 (Feasibility)** 问题。

### 核心改进
1.  **从 $R^2$ 到 $SE(2)$ 配置空间**：状态表达由 $(x, y)$ 升级为 $(x, y, \theta)$。算法不仅寻找位置，更规划车辆的航向角，真正实现了三维配置空间的搜索。
2.  **混合状态空间 (Hybrid State Space)**：结合了连续空间的运动学扩展与离散空间的栅格剪枝，通过“状态去重”解决了 $SE(2)$ 空间维度爆炸导致的搜索效率问题。
3.  **非完整性运动学约束 (Non-holonomic Constraints)**：引入基于 Ackermann 转向几何的**运动学自行车模型 (Kinematic Bicycle Model)**，确保路径完全符合车辆的最小转弯半径限制。
4.  **多向行驶与换挡逻辑**：算法原生支持前进与倒车切换。在代价函数中引入“换挡惩罚”，使车辆能够像老司机一样自动选择最优的“揉库”时机。
5.  **精细化碰撞检测**：摒弃了 Phase 2 的圆形简化模型，采用多矩形组合包络描述车身，实现厘米级的障碍物规避。

---

## 📂 文件清单
- `car_model.py`: 定义车辆物理尺寸、转向极值及矩形包络计算。
- `collision_checker.py`: 实现基于车身实时位姿的栅格碰撞检测。
- `state_indexer.py`: 状态投影器，将连续位姿映射到离散桶中进行剪枝。
- `hybrid_astar.py`: 核心算法，包含运动基元扩展及优先队列维护。
- `main_vertical.py`: **垂直泊车演示**，支持随机起点生成。
- `main_parallel.py`: **极限侧方位演示**，挑战窄位操控与换挡逻辑。

## 📊 运行结果

### 1. 基础工况验证 (Simple Scenario)
验证在 $SE(2)$ 空间内绕过简单障碍物并达到指定航向角的能力：

![Phase 3 Simple](https://github.com/kangshuoliu77-del/autonomous-driving-learning-notes/blob/main/code/astar-parking/phase3_hybrid_astar/result_simple.png)

### 2. 垂直泊车实战 (Vertical Parking)
模拟真实的倒车入库场景，红色曲线展示了符合运动学约束的平滑轨迹：

![Phase 3 Vertical](https://github.com/kangshuoliu77-del/autonomous-driving-learning-notes/blob/main/code/astar-parking/phase3_hybrid_astar/result_vertical.png)

### 3. 极限侧方实战 (Parallel Parking)
在极窄空间内通过多次换挡（黄色圆点）实现的精准位姿调整：

![Phase 3 Parallel](https://github.com/kangshuoliu77-del/autonomous-driving-learning-notes/blob/main/code/astar-parking/phase3_hybrid_astar/result_parallel.png)


*(注：红色线为路径中心轨迹，蓝色箭头表示车身航向角度)*


---

## 🚀 部署与运行
确保所有模块位于同一目录下，直接运行对应的 Demo 脚本：

```bash
# 验证基础避障逻辑
python main_simple.py

# 验证垂直泊车场景
python main_vertical.py

# 验证侧方位停车场景
python main_parallel.py
```
---

## 🚸 存在的问题（后续研究方向）
1.  **曲率不连续**：目前的路径由离散的运动基元拼接而成，在转向切换处存在曲率突变。
2.  **轨迹平滑需求**：目前的路径虽然可行驶，但仍有“锯齿感”，需要通过数值优化进一步平滑。

---
*本项目是自动驾驶学习系列的一部分。从 Phase 1 的简单寻路到 Phase 3 的运动学规划，逐步接近工业级泊车方案。*
