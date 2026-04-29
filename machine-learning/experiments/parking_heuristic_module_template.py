import torch
from torch import nn


# =========================
# 模块 1：定义泊车 heuristic 网络
# =========================

class ParkingHeuristicNet(nn.Module):
    """一个贴近泊车 learning heuristic 的最小自定义 nn.Module 示例。"""

    def __init__(self):
        super().__init__()

        # 当前车辆状态: [x, y, theta] -> 32 个状态特征
        self.state_net = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
        )

        # 目标位姿: [goal_x, goal_y, goal_theta] -> 32 个目标特征
        self.goal_net = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
        )

        # 环境特征: 比如障碍物距离、车位宽度、安全距离等 10 个数 -> 64 个环境特征
        self.env_net = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
        )

        # 拼接后: 32 + 32 + 64 = 128
        # 输出: 1 个 heuristic cost
        self.head = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, state, goal, env):
        """定义数据怎么流过网络。"""
        state_feat = self.state_net(state)
        goal_feat = self.goal_net(goal)
        env_feat = self.env_net(env)

        # dim=1 表示在“特征维度”拼接，batch_size 这一维不变。
        feat = torch.cat((state_feat, goal_feat, env_feat), dim=1)

        cost = self.head(feat)
        return cost


# =========================
# 模块 2：创建模型和假数据
# =========================

net = ParkingHeuristicNet()

batch_size = 8

# state: 当前车辆状态 [x, y, theta]
state = torch.randn(batch_size, 3)

# goal: 目标位姿 [goal_x, goal_y, goal_theta]
goal = torch.randn(batch_size, 3)

# env: 环境特征，比如障碍物距离、车位宽度、安全距离等
env = torch.randn(batch_size, 10)


# =========================
# 模块 3：前向计算
# =========================

cost = net(state, goal, env)

print("state shape:", state.shape)
print("goal shape:", goal.shape)
print("env shape:", env.shape)
print("cost shape:", cost.shape)

# 一个 batch 有 8 个样本，每个样本预测 1 个 heuristic cost。
assert cost.shape == (batch_size, 1)


# =========================
# 模块 4：查看参数
# =========================

for name, param in net.named_parameters():
    print(name, param.shape)


# =========================
# 模块 5：简单检查 backward 是否能工作
# =========================

# 假设 Hybrid A* / MPC 给出的真实 cost-to-go 标签。
target_cost = torch.randn(batch_size, 1)

loss = nn.MSELoss()
trainer = torch.optim.Adam(net.parameters(), lr=1e-3)

l = loss(cost, target_cost)

trainer.zero_grad()
l.backward()
trainer.step()

print("one-step loss:", l.item())


# 小结：
# __init__ 里定义子网络。
# forward 里定义 state、goal、env 怎么分别编码、拼接、输出 cost。
# net(state, goal, env) 会自动调用 forward。
# net.named_parameters() 可以查看所有被 self.xxx 管理的参数。
