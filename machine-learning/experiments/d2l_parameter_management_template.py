import torch
from torch import nn


# D2L 5.2 参数管理复习模板
# 重点：查看参数、理解形状、查看梯度、初始化参数、冻结参数。


net = nn.Sequential(
    nn.Linear(4, 8),  # 输入 4 个特征，输出 8 个隐藏特征
    nn.ReLU(),
    nn.Linear(8, 1),  # 输入 8 个隐藏特征，输出 1 个预测值
)

X = torch.randn(3, 4)  # 3 条样本，每条样本 4 个特征
y_hat = net(X)

print("X.shape:", X.shape)
print("y_hat.shape:", y_hat.shape)

# nn.Linear(in_features, out_features)
# weight.shape = [out_features, in_features]
# bias.shape = [out_features]
print("net[0].weight.shape:", net[0].weight.shape)
print("net[0].bias.shape:", net[0].bias.shape)
print("net[2].weight.shape:", net[2].weight.shape)
print("net[2].bias.shape:", net[2].bias.shape)

print("\nparameters():")
for param in net.parameters():
    print(param.shape)

print("\nnamed_parameters():")
for name, param in net.named_parameters():
    print(name, param.shape)

# 构造一个简单 loss，让 PyTorch 可以反向传播并生成梯度。
loss = y_hat.sum()
loss.backward()

print("\ngrad shape:")
print("net[0].weight.grad.shape:", net[0].weight.grad.shape)
print("net[0].bias.grad.shape:", net[0].bias.grad.shape)


def init_weights(m):
    # net.apply 会把网络里的每一层都传进来，这里只处理 Linear 层。
    if type(m) == nn.Linear:
        nn.init.normal_(m.weight, mean=0, std=0.01)
        nn.init.zeros_(m.bias)


net.apply(init_weights)

print("\nafter init:")
print(net[0].weight.data)
print(net[0].bias.data)

# 冻结第一层参数：这层不再计算梯度，也不会被训练更新。
for param in net[0].parameters():
    param.requires_grad = False

print("\nrequires_grad:")
for name, param in net.named_parameters():
    print(name, param.requires_grad)
