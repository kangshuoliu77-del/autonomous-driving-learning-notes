from pathlib import Path

import torch
import torchvision
from torch import nn
from torch.utils import data
from torchvision import transforms


# =========================
# 模块 1：超参数和运行设备
# =========================

batch_size = 256
num_epochs = 10
learning_rate = 0.1

# 权重衰减：限制权重别太大，用来缓解过拟合。
weight_decay = 1e-4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")


# =========================
# 模块 2：读取 Fashion-MNIST 数据
# =========================

trans = transforms.ToTensor()

# 当前仓库在 ClaudeTest/autonomous-driving-learning-notes 下，
# 数据放在 ClaudeTest/data，和 dl_code 里的练习文件共用一份数据。
data_root = Path(__file__).resolve().parents[3] / "data"

mnist_train = torchvision.datasets.FashionMNIST(
    root=data_root,
    train=True,
    transform=trans,
    download=True,
)

mnist_test = torchvision.datasets.FashionMNIST(
    root=data_root,
    train=False,
    transform=trans,
    download=True,
)

train_iter = data.DataLoader(
    mnist_train,
    batch_size=batch_size,
    shuffle=True,
)

test_iter = data.DataLoader(
    mnist_test,
    batch_size=batch_size,
    shuffle=False,
)


# =========================
# 模块 3：定义带 Dropout 的 MLP
# =========================

net = nn.Sequential(
    nn.Flatten(),

    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(p=0.2),    # 训练时随机丢掉 20% 的隐藏特征输出

    nn.Linear(256, 256),
    nn.ReLU(),
    nn.Dropout(p=0.5),    # 训练时随机丢掉 50% 的隐藏特征输出

    nn.Linear(256, 10),
)

net.to(device)


# =========================
# 模块 4：初始化参数
# =========================

def init_weights(module):
    """只初始化 Linear 层。"""
    if type(module) == nn.Linear:
        nn.init.normal_(module.weight, mean=0, std=0.01)
        nn.init.zeros_(module.bias)


net.apply(init_weights)


# =========================
# 模块 5：loss、优化器和准确率
# =========================

loss = nn.CrossEntropyLoss()

# weight_decay 是权重衰减；Dropout 已经写在 net 里面。
trainer = torch.optim.SGD(
    net.parameters(),
    lr=learning_rate,
    weight_decay=weight_decay,
)


def accuracy(y_hat, y):
    """返回一个 batch 中预测正确的样本数量。"""
    y_pred = y_hat.argmax(dim=1)
    return (y_pred == y).float().sum().item()


def evaluate_accuracy(net, data_iter):
    """在整个数据集上计算准确率，只评估，不更新参数。"""
    net.eval()  # 评估时关闭 Dropout
    correct = 0
    total = 0

    with torch.no_grad():
        for X, y in data_iter:
            X = X.to(device)
            y = y.to(device)

            correct += accuracy(net(X), y)
            total += y.numel()

    net.train()  # 评估结束后切回训练模式
    return correct / total


# =========================
# 模块 6：训练循环
# =========================

for epoch in range(num_epochs):
    total_loss = 0
    total_correct = 0
    total_num = 0

    for X, y in train_iter:
        X = X.to(device)
        y = y.to(device)

        y_hat = net(X)
        l = loss(y_hat, y)

        trainer.zero_grad()
        l.backward()
        trainer.step()

        total_loss += l.item() * y.numel()
        total_correct += accuracy(y_hat, y)
        total_num += y.numel()

    train_loss = total_loss / total_num
    train_acc = total_correct / total_num
    test_acc = evaluate_accuracy(net, test_iter)

    print(
        f"epoch {epoch + 1}, "
        f"loss {train_loss:.4f}, "
        f"train acc {train_acc:.3f}, "
        f"test acc {test_acc:.3f}"
    )


# 小结：
# Dropout 写在模型里，训练时随机丢隐藏单元，测试时通过 net.eval() 自动关闭。
# weight_decay 写在优化器里，更新参数时限制权重不要过大。
