"""D2L 3.3 线性回归简洁实现模板。

这个模板和 3.2 做同一个训练任务，但使用 PyTorch 常用封装：

- TensorDataset 和 DataLoader 负责 mini-batch
- nn.Linear 负责线性模型
- nn.MSELoss 负责平方损失
- torch.optim.SGD 负责参数更新
"""

import torch
from torch import nn
from torch.utils import data


# 模块 1：生成数据
def synthetic_data(w, b, num_examples):
    X = torch.normal(0, 1, (num_examples, len(w)))
    # torch.normal(0, 1, shape)：从正态分布里随机生成数字。
    # 这里 X 的形状是 [1000, 2]：1000 条样本，每条样本 2 个特征。

    y = torch.matmul(X, w) + b
    # 根据真实线性公式生成标签。
    # X.shape = [1000, 2]，w.shape = [2]，所以每条样本得到一个 y。
    # 这时 y 通常是形状 [1000]。

    y += torch.normal(0, 0.01, y.shape)
    # 加一点和 y 形状相同的小噪声。

    return X, y.reshape((-1, 1))
    # 把标签从形状 [1000] 改成 [1000, 1]。


true_w = torch.tensor([2, -3.4])
true_b = 4.2
features, labels = synthetic_data(true_w, true_b, 1000)


# 模块 2：用 DataLoader 读取数据
def load_array(data_arrays, batch_size, is_train=True):
    # data_arrays：要打包的数据，比如 (features, labels)。
    # batch_size：每个 mini-batch 有多少条样本。
    # is_train：是否是训练模式，训练时通常需要打乱数据。
    dataset = data.TensorDataset(*data_arrays)
    # 等价于 data.TensorDataset(features, labels)。
    # 它会把 features[i] 和 labels[i] 配成一条样本。

    return data.DataLoader(dataset, batch_size, shuffle=is_train)
    # DataLoader 会从 dataset 里一批一批取数据。


batch_size = 10
data_iter = load_array((features, labels), batch_size)

X_batch, y_batch = next(iter(data_iter))
# next(iter(data_iter)) 表示取出第一个 mini-batch。
# X_batch.shape = [10, 2]，y_batch.shape = [10, 1]。


# 模块 3：定义模型
net = nn.Sequential(nn.Linear(2, 1))
# nn.Linear(2, 1)：2 个输入特征 -> 1 个输出值。
# 它会自动创建 weight 和 bias。
# nn.Sequential 会按顺序保存网络层；这里 net[0] 就是 Linear 层。


# 模块 4：初始化参数
net[0].weight.data.normal_(0, 0.01)
# 把 weight 初始化成接近 0 的小随机数。

net[0].bias.data.fill_(0)
# 把 bias 初始化成 0。


# 模块 5：定义损失函数
loss = nn.MSELoss()
# Mean Squared Error，均方误差：预测值和真实值差值的平方，再求平均。

y_hat = net(X_batch)
batch_loss = loss(y_hat, y_batch)
# batch_loss 是一个标量，所以训练循环里可以直接 backward()。


# 模块 6：定义优化器
trainer = torch.optim.SGD(net.parameters(), lr=0.03)
# net.parameters() 会返回模型里所有需要学习的参数。
# 注意要写括号：net.parameters()，不能写成 net.parameters。


# 模块 7：训练
num_epochs = 3

for epoch in range(num_epochs):
    for X, y in data_iter:
        batch_loss = loss(net(X), y)
        trainer.zero_grad()
        batch_loss.backward()
        trainer.step()

    epoch_loss = loss(net(features), labels)
    print(f"epoch {epoch + 1}, loss {epoch_loss:f}")


# 模块 8：比较学到的参数和真实参数的差距
w = net[0].weight.data
print("w error:", true_w - w.reshape(true_w.shape))

b = net[0].bias.data
print("b error:", true_b - b)
