import torch
from torch import nn


# D2L 5.6 GPU 复习模板
# 重点：创建 device，把模型和数据放到同一个设备上。


print("cuda available:", torch.cuda.is_available())

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device:", device)

X = torch.randn(4, 3)
y = torch.randn(4, 1)

net = nn.Sequential(
    nn.Linear(3, 8),
    nn.ReLU(),
    nn.Linear(8, 1),
)

# 模型和数据必须在同一个设备，否则前向计算会报错。
net = net.to(device)
X = X.to(device)
y = y.to(device)

print("X.device:", X.device)
print("y.device:", y.device)
print("model device:", next(net.parameters()).device)

loss = nn.MSELoss()
trainer = torch.optim.SGD(net.parameters(), lr=0.03)

y_hat = net(X)
l = loss(y_hat, y)

trainer.zero_grad()
l.backward()
trainer.step()

print("loss:", l.item())
