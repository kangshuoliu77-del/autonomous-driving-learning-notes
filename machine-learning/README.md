# 机器学习与深度学习

这个目录用于记录机器学习、深度学习以及 learning-based planning 的学习资料和笔记。

## 当前定位

Phase 1-4 已经完成了传统泊车规划控制闭环：

```text
Hybrid A* -> path interpolation -> CasADi/IPOPT MPC
```

Phase 5 / Phase 6 已经把 learning 方法接入过这个闭环，当前定位需要稍微调整：

```text
Phase 5: Hybrid A* success path -> cost_to_go label -> MLP heuristic -> tie-breaker
Phase 6: 2D map -> Dijkstra label -> CNN heuristic -> Neural A* toy
```

这两步的意义是理解 learning 如何辅助 search，而不是长期死磕单一 learned heuristic。后续更重要的是把 deep learning 工具箱补完整，并为 imitation learning / RL / 多车交互 planning 做准备。

重点不是泛泛学习深度学习，而是围绕 planning 实验思考：

- 能不能用优秀轨迹训练一个网络
- 能不能学习 A* / Hybrid A* 的启发式函数
- 能不能用 learning 方法预测中间位姿、参考轨迹或搜索方向
- 能不能把 RL、监督学习和传统规划控制结合起来
- 能不能用 expert trajectory 做 behavior cloning / pre-train，再用 RL 在 simulation 里 fine-tune

## 推荐资料

### 动手学深度学习

- 目标：补 PyTorch、神经网络、训练流程、CNN/RNN/Transformer/CV/NLP 基础
- 用法：先跑通基础网络和训练循环，再回到泊车实验里构造数据集
- 当前重点：快速补完 CNN、Transformer、CV/NLP 的基本语言，不在感知方向过深挖掘

### 吴恩达机器学习 / 深度学习课程

- 目标：建立机器学习基本框架
- 重点：监督学习、损失函数、梯度下降、神经网络、泛化、训练/验证/测试集

## 建议目录

```text
machine-learning/
├── README.md
├── resources/          # PDF、课程资料、参考书
├── notes/              # 学习笔记
└── experiments/        # 小实验代码或数据集说明
```

## 实验模板

- `experiments/d2l_linear_regression_scratch_template.py`：D2L 3.2 线性回归从零实现模板，保留数据生成、mini-batch、模型、loss、SGD、训练循环的完整骨架。
- `experiments/d2l_linear_regression_concise_template.py`：D2L 3.3 线性回归简洁实现模板，用 `DataLoader`、`nn.Linear`、`nn.MSELoss`、`torch.optim.SGD` 替代手写训练组件。
- `experiments/d2l_softmax_regression_concise_template.py`：D2L 3.7 softmax 回归简洁实现模板，用 `Fashion-MNIST`、`nn.Flatten`、`nn.Linear`、`nn.CrossEntropyLoss` 和 `torch.optim.SGD` 完成多分类训练，并输出训练集/测试集准确率。
- `experiments/d2l_mlp_scratch_template.py`：D2L 4.2 多层感知机从零实现模板，手写 `W1/b1`、`ReLU`、`W2/b2` 和 SGD，展示 MLP 相比 softmax 回归多出的隐藏层和激活函数。
- `experiments/d2l_mlp_concise_template.py`：D2L 4.3 多层感知机简洁实现模板，用 `nn.Sequential`、`nn.Flatten`、`nn.Linear`、`nn.ReLU` 和 `torch.optim.SGD` 完成 MLP 图像分类训练。
- `experiments/d2l_mlp_regularization_template.py`：D2L 4.5/4.6 正则化模板，在 MLP 中同时加入 `weight_decay` 权重衰减和 `nn.Dropout`，用于理解缓解过拟合的两种常用方法。
- `experiments/parking_heuristic_module_template.py`：D2L 5.1 `nn.Module` 自定义模型模板，模拟 `state + goal + env -> heuristic cost` 的泊车 learning heuristic 网络结构。
- `experiments/d2l_parameter_management_template.py`：D2L 5.2 参数管理复习模板，覆盖 `parameters()`、`named_parameters()`、参数形状、梯度、初始化和冻结参数。
- `experiments/d2l_save_load_template.py`：D2L 5.5 保存和加载模板，演示 `torch.save`、`torch.load`、`state_dict`、`load_state_dict` 和推理模式。
- `experiments/d2l_gpu_template.py`：D2L 5.6 GPU 模板，演示 `device`、`net.to(device)`、`X.to(device)`，强调模型和数据必须在同一个设备。
- `experiments/d2l_cnn_local_map_template.py`：D2L 第 6 章 CNN 局部地图模板，用 `Conv2d -> ReLU -> MaxPool2d` 从 `local_map` 提取 `map_feature`，并演示和 `state/goal` 特征拼接后预测 `cost_to_go`。

## 与泊车项目的连接

已经完成的连接：

1. 用 Hybrid A* 成功路径生成 `cost_to_go` 数据集
2. 训练 MLP heuristic
3. 做离线误差和 ranking accuracy 评估
4. 将 MLP 作为 tie-breaker 接回 Hybrid A*，观察 expanded nodes 和 planning time
5. 用二维 toy 理解 Neural A* / CNN heuristic 的基本流程

后续更自然的实验路线：

1. 用现有 Hybrid A* / MPC 生成成功泊车轨迹
2. 保存状态、障碍物、目标位姿、参考轨迹、控制量等数据
3. 先做 behavior cloning / imitation learning 的最小实验
4. 再尝试 PPO / RL fine-tuning，而不是只做监督学习 heuristic
5. 把网络接回传统规划器或仿真器，观察 success rate、collision、expanded nodes、planning time、path quality
