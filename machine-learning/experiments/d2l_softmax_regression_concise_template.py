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

# 如果 PyTorch 能找到 NVIDIA GPU，就用 cuda；否则自动退回 CPU。
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")


# =========================
# 模块 2：读取 Fashion-MNIST 数据
# =========================

# ToTensor 会把图片转成 tensor，并把像素值从 0-255 缩放到 0-1。
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

# 只取一个 batch 看形状：X 是图片，y 是标签。
X, y = next(iter(train_iter))
print("一个 batch 的 X 形状:", X.shape)  # [256, 1, 28, 28]
print("一个 batch 的 y 形状:", y.shape)  # [256]


# =========================
# 模块 3：定义模型
# =========================

net = nn.Sequential(
    # Flatten 默认保留第 0 维 batch_size，把后面的 [1, 28, 28] 拉平成 784。
    nn.Flatten(),
    # 每张图片有 784 个像素，输出 10 个类别的原始分数 logits。
    nn.Linear(784, 10),
)

# 把模型参数放到 device 上。device 可能是 cuda，也可能是 cpu。
net.to(device)


def init_weights(module):
    """初始化线性层参数。"""
    if type(module) == nn.Linear:
        nn.init.normal_(module.weight, std=0.01)
        nn.init.zeros_(module.bias)


# apply 会把 init_weights 应用到网络的每一层。
net.apply(init_weights)


# =========================
# 模块 4：定义损失函数和优化器
# =========================

# CrossEntropyLoss 内部已经包含 softmax，不需要自己再手动 softmax。
loss = nn.CrossEntropyLoss()

# SGD 会根据反向传播得到的梯度更新 net 里的参数。
trainer = torch.optim.SGD(net.parameters(), lr=learning_rate)


# =========================
# 模块 5：定义准确率评估函数
# =========================

def accuracy(y_hat, y):
    """返回一个 batch 中预测正确的样本数量。"""
    # y_hat.shape = [batch_size, 10]
    # argmax(dim=1) 表示在每一行 10 个类别分数里找最大值的位置。
    y_pred = y_hat.argmax(dim=1)
    return (y_pred == y).float().sum().item()


def evaluate_accuracy(net, data_iter):
    """在整个数据集上计算准确率，只评估，不更新参数。"""
    net.eval()
    correct = 0
    total = 0

    # 评估时不需要梯度，关闭梯度记录可以更省内存。
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
    # 这三个统计量每个 epoch 重新清零。
    total_loss = 0
    total_correct = 0
    total_num = 0

    for X, y in train_iter:
        # 一次拿 256 张图片和 256 个标签。
        # X.shape = [256, 1, 28, 28]
        # y.shape = [256]
        X = X.to(device)
        y = y.to(device)

        # 前向计算：得到每张图片属于 10 个类别的原始分数 logits。
        y_hat = net(X)

        # 计算 loss。这里传入 logits 和真实标签 y。
        l = loss(y_hat, y)

        # 反向传播前先清空旧梯度。
        trainer.zero_grad()

        # 根据当前 batch 的 loss，计算模型参数梯度。
        l.backward()

        # 根据梯度更新参数。
        trainer.step()

        # 统计这一批的总 loss 和预测正确数量。
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
# for X, y in train_iter 会遍历所有 batch。
# X, y = next(iter(train_iter)) 只取第一个 batch。
# accuracy 只看“猜对没”；loss 看“对真实类别有多自信，以及错得有多离谱”。
