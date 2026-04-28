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

X, y = next(iter(train_iter))
print("一个 batch 的 X 形状:", X.shape)  # [256, 1, 28, 28]
print("一个 batch 的 y 形状:", y.shape)  # [256]


# =========================
# 模块 3：定义 MLP 模型
# =========================

net = nn.Sequential(
    nn.Flatten(),          # [batch_size, 1, 28, 28] -> [batch_size, 784]
    nn.Linear(784, 256),   # 784 个输入特征 -> 256 个隐藏特征
    nn.ReLU(),             # 激活函数，引入非线性
    nn.Linear(256, 10),    # 256 个隐藏特征 -> 10 个类别 logits
)

net.to(device)

# 测试一次前向计算，确认输出是 [batch_size, 10]。
X = X.to(device)
y_hat = net(X)
print("y_hat:", y_hat.shape)


# =========================
# 模块 4：初始化参数
# =========================

def init_weights(module):
    """只初始化 Linear 层的 weight 和 bias。"""
    if type(module) == nn.Linear:
        nn.init.normal_(module.weight, mean=0, std=0.01)
        nn.init.zeros_(module.bias)


net.apply(init_weights)

print("第一层 weight:", net[1].weight.shape)  # [256, 784]
print("第一层 bias:", net[1].bias.shape)      # [256]
print("第二层 weight:", net[3].weight.shape)  # [10, 256]
print("第二层 bias:", net[3].bias.shape)      # [10]


# =========================
# 模块 5：loss、优化器和准确率
# =========================

# CrossEntropyLoss 内部已经包含 softmax，不需要自己手动 softmax。
loss = nn.CrossEntropyLoss()

# net.parameters() 会把两层 Linear 的 weight/bias 都交给优化器。
trainer = torch.optim.SGD(net.parameters(), lr=learning_rate)


def accuracy(y_hat, y):
    """返回一个 batch 中预测正确的样本数量。"""
    y_pred = y_hat.argmax(dim=1)
    return (y_pred == y).float().sum().item()


def evaluate_accuracy(net, data_iter):
    """在整个数据集上计算准确率，只评估，不更新参数。"""
    net.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for X, y in data_iter:
            X = X.to(device)
            y = y.to(device)

            correct += accuracy(net(X), y)
            total += y.numel()

    net.train()
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
# 3.7 softmax 回归是 Flatten + Linear(784, 10)。
# 4.3 MLP 简洁实现是 Flatten + Linear(784, 256) + ReLU + Linear(256, 10)。
# 训练流程没有变，变的是模型中间多了隐藏层和激活函数。
