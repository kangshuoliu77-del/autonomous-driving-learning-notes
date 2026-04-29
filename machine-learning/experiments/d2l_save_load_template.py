from pathlib import Path

import torch
from torch import nn


# D2L 5.5 保存和加载复习模板
# 重点：保存 tensor，保存模型参数 state_dict，加载时先创建同样结构的模型。


output_dir = Path("/tmp/d2l_save_load_template")
output_dir.mkdir(exist_ok=True)


x = torch.arange(4)
tensor_path = output_dir / "x.pt"
torch.save(x, tensor_path)

x2 = torch.load(tensor_path)
print("x2:", x2)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.net(x)


net = Net()

X = torch.randn(5, 6)
y_hat = net(X)

model_path = output_dir / "net.pth"

# 推荐保存方式：只保存模型参数，不直接保存整个模型对象。
torch.save(net.state_dict(), model_path)

# 加载时必须先创建同样结构的模型，再把参数加载进去。
net2 = Net()
net2.load_state_dict(torch.load(model_path))

y_hat2 = net2(X)
print("same output:", torch.allclose(y_hat, y_hat2))

# 推理模式：关闭训练专用行为；no_grad 表示不记录梯度，省显存和计算。
net2.eval()
with torch.no_grad():
    pred = net2(X)

print("pred.shape:", pred.shape)
