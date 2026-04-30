import torch
from torch import nn


# D2L 第 6 章 CNN 复习模板
# 目标：local_map -> CNN -> map_feature


# 模拟一批泊车局部地图
# 8 条样本，1 个地图通道，地图大小 40x40
X = torch.randn(8, 1, 40, 40)


map_net = nn.Sequential(
    # [8, 1, 40, 40] -> [8, 16, 40, 40]
    # 3x3 卷积 + padding=1：高宽不变，通道数从 1 变成 16
    nn.Conv2d(1, 16, kernel_size=3, padding=1),
    # ReLU 加入非线性，不改变 shape
    nn.ReLU(),
    # [8, 16, 40, 40] -> [8, 16, 20, 20]
    # MaxPool2d(2)：通道不变，高宽减半
    nn.MaxPool2d(2),
    # [8, 16, 20, 20] -> [8, 32, 20, 20]
    # 第二层卷积继续提取特征，通道数从 16 变成 32
    nn.Conv2d(16, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    # [8, 32, 20, 20] -> [8, 32, 10, 10]
    nn.MaxPool2d(2),
    # [8, 32, 10, 10] -> [8, 3200]
    nn.Flatten(),
    # [8, 3200] -> [8, 128]
    # 把整张地图压成 128 维 map feature
    nn.Linear(32 * 10 * 10, 128),
    nn.ReLU(),
)

map_feature = map_net(X)

print("X.shape:", X.shape)
print("map_feature.shape:", map_feature.shape)


# 一层一层检查 shape，复习 Conv2d / ReLU / MaxPool2d / Flatten 的作用
print("\nlayer by layer:")
Y = X
for layer in map_net:
    Y = layer(Y)
    print(layer.__class__.__name__, Y.shape)


# 后续 learning heuristic 里，map feature 可以和 state/goal feature 拼接
state_goal = torch.randn(8, 6)  # 例如 state(x,y,theta) + goal(x,y,theta)
state_goal_net = nn.Sequential(
    nn.Linear(6, 64),
    nn.ReLU(),
)

state_goal_feature = state_goal_net(state_goal)
feature = torch.cat((map_feature, state_goal_feature), dim=1)

head = nn.Sequential(
    nn.Linear(128 + 64, 64),
    nn.ReLU(),
    nn.Linear(64, 1),
)

cost_to_go = head(feature)

print("\nstate_goal_feature.shape:", state_goal_feature.shape)
print("feature.shape:", feature.shape)
print("cost_to_go.shape:", cost_to_go.shape)
