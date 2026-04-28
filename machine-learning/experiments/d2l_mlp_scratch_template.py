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
lr = 0.1

num_inputs = 784
num_hiddens = 256
num_outputs = 10

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
# 模块 3：手动初始化 MLP 参数
# =========================

# 第一层：784 个输入特征 -> 256 个隐藏特征
W1 = torch.randn(num_inputs, num_hiddens, device=device) * 0.01
b1 = torch.zeros(num_hiddens, device=device)

# 第二层：256 个隐藏特征 -> 10 个类别 logits
W2 = torch.randn(num_hiddens, num_outputs, device=device) * 0.01
b2 = torch.zeros(num_outputs, device=device)

params = [W1, b1, W2, b2]

for param in params:
    param.requires_grad_(True)

print("W1:", W1.shape)  # [784, 256]
print("b1:", b1.shape)  # [256]
print("W2:", W2.shape)  # [256, 10]
print("b2:", b2.shape)  # [10]


# =========================
# 模块 4：手写 ReLU 和 MLP 前向计算
# =========================

def relu(X):
    """ReLU(x) = max(x, 0)，负数变 0，正数保持不变。"""
    return torch.max(X, torch.zeros_like(X))


def net(X):
    """手写两层 MLP：reshape -> Linear1 -> ReLU -> Linear2。"""
    X = X.reshape((-1, num_inputs))
    H = relu(X @ W1 + b1)
    return H @ W2 + b2


# 测试一次前向计算，确认输出是 [batch_size, 10]。
X = X.to(device)
y_hat = net(X)
print("y_hat:", y_hat.shape)


# =========================
# 模块 5：loss、准确率和手写 SGD
# =========================

# CrossEntropyLoss 内部会处理 softmax，所以 net 输出 logits 即可。
loss = nn.CrossEntropyLoss()


def accuracy(y_hat, y):
    """返回一个 batch 中预测正确的样本数量。"""
    y_pred = y_hat.argmax(dim=1)
    return (y_pred == y).float().sum().item()


def sgd(params, lr):
    """手写随机梯度下降。"""
    with torch.no_grad():
        for param in params:
            param -= lr * param.grad
            param.grad.zero_()


def evaluate_accuracy(data_iter):
    """在整个测试集上计算准确率，只评估，不更新参数。"""
    correct = 0
    total = 0

    with torch.no_grad():
        for X, y in data_iter:
            X = X.to(device)
            y = y.to(device)

            correct += accuracy(net(X), y)
            total += y.numel()

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

        # 手写版没有 trainer.zero_grad() 和 trainer.step()。
        # l.backward() 负责算梯度，sgd() 负责更新参数并清空梯度。
        l.backward()
        sgd(params, lr)

        total_loss += l.item() * y.numel()
        total_correct += accuracy(y_hat, y)
        total_num += y.numel()

    train_loss = total_loss / total_num
    train_acc = total_correct / total_num
    test_acc = evaluate_accuracy(test_iter)

    print(
        f"epoch {epoch + 1}, "
        f"loss {train_loss:.4f}, "
        f"train acc {train_acc:.3f}, "
        f"test acc {test_acc:.3f}"
    )


# 小结：
# W1,b1 对应第一层 nn.Linear(784, 256)。
# relu 对应 nn.ReLU()。
# W2,b2 对应第二层 nn.Linear(256, 10)。
# sgd(params, lr) 对应 torch.optim.SGD 的核心参数更新逻辑。
