# Machine Learning & Deep Learning

这个目录用于记录机器学习、深度学习以及 learning-based planning 的学习资料和笔记。

## 当前定位

Phase 1-4 已经完成了传统泊车规划控制闭环：

```text
Hybrid A* -> path interpolation -> CasADi/IPOPT MPC
```

下一阶段开始把 learning 方法接入这个闭环，重点不是泛泛学习深度学习，而是围绕泊车实验思考：

- 能不能用优秀轨迹训练一个网络
- 能不能学习 A* / Hybrid A* 的启发式函数
- 能不能用 learning 方法预测中间位姿、参考轨迹或搜索方向
- 能不能把 RL、监督学习和传统规划控制结合起来

## 推荐资料

### 动手学深度学习

- 目标：补 PyTorch、神经网络、训练流程、CNN/RNN/Transformer 基础
- 用法：先跑通基础网络和训练循环，再回到泊车实验里构造数据集

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

## 与泊车项目的连接

后续最自然的实验路线：

1. 用现有 Hybrid A* / MPC 生成成功泊车轨迹
2. 保存状态、障碍物、目标位姿、参考轨迹、控制量等数据
3. 训练一个小网络学习某个子任务
4. 把网络接回传统规划器，观察是否能减少搜索节点或改善轨迹质量
