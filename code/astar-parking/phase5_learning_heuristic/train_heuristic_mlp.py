from pathlib import Path
import random

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


SEED = 0
BATCH_SIZE = 64
NUM_EPOCHS = 100
LEARNING_RATE = 1e-3

# 所有路径都基于当前脚本所在目录，避免从别的目录运行时读错数据。
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datasets" / "parking_cost_to_go_v1.npz"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "heuristic_mlp_v1.pth"


def set_seed(seed):
    """固定随机种子，让每次训练结果更可复现。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_dataset(data_path):
    """读取 dataset_generator.py 生成的 X/y，并转成 PyTorch tensor。"""
    data = np.load(data_path)
    X = torch.tensor(data["X"], dtype=torch.float32)
    y = torch.tensor(data["y"], dtype=torch.float32)
    return X, y


def split_dataset(X, y, train_ratio=0.7, val_ratio=0.15):
    """随机切成训练集、验证集、测试集。"""
    num_samples = X.shape[0]
    indices = torch.randperm(num_samples)

    train_size = int(num_samples * train_ratio)
    val_size = int(num_samples * val_ratio)

    train_indices = indices[:train_size]
    val_indices = indices[train_size:train_size + val_size]
    test_indices = indices[train_size + val_size:]

    return (
        X[train_indices],
        y[train_indices],
        X[val_indices],
        y[val_indices],
        X[test_indices],
        y[test_indices],
    )


def make_loader(X, y, batch_size, shuffle):
    """把 X/y 打包成 DataLoader，训练时按 batch 取数据。"""
    dataset = TensorDataset(X, y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def build_model():
    """第一版 learned heuristic：8维 state-goal 特征 -> 1维 cost_to_go。"""
    return nn.Sequential(
        nn.Linear(8, 64),
        nn.ReLU(),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Linear(64, 1),
    )


def evaluate_loss(net, data_loader, loss_fn):
    """在验证集或测试集上计算平均 MSE loss，不更新参数。"""
    net.eval()

    total_loss = 0.0
    total_num = 0

    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            pred = net(X_batch)
            loss = loss_fn(pred, y_batch)

            total_loss += loss.item() * X_batch.shape[0]
            total_num += X_batch.shape[0]

    net.train()
    return total_loss / total_num


def train(net, train_loader, val_loader, loss_fn, optimizer, num_epochs):
    """标准训练循环：前向计算、loss、反向传播、参数更新。"""
    for epoch in range(num_epochs):
        total_train_loss = 0.0
        total_train_num = 0

        for X_batch, y_batch in train_loader:
            pred = net(X_batch)
            loss = loss_fn(pred, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item() * X_batch.shape[0]
            total_train_num += X_batch.shape[0]

        train_loss = total_train_loss / total_train_num
        val_loss = evaluate_loss(net, val_loader, loss_fn)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(
                f"epoch {epoch + 1}, "
                f"train loss {train_loss:.4f}, "
                f"val loss {val_loss:.4f}"
            )


def print_sample_predictions(net, X_test, y_test, num_samples=10):
    """打印几个真实 cost 和预测 cost，方便直观看模型有没有学到趋势。"""
    net.eval()

    with torch.no_grad():
        X_sample = X_test[:num_samples]
        y_sample = y_test[:num_samples]
        pred_sample = net(X_sample)

    print("\nSample predictions:")
    for i in range(num_samples):
        print(
            f"true={y_sample[i].item():.2f}, "
            f"pred={pred_sample[i].item():.2f}"
        )


def main():
    set_seed(SEED)

    # 1. 读取数据：X 是 8维输入，y 是 cost_to_go 标签。
    X, y = load_dataset(DATA_PATH)
    print("DATA_PATH:", DATA_PATH)
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    # 2. 切分数据：train 用来训练，val 用来观察过拟合，test 最后评估。
    X_train, y_train, X_val, y_val, X_test, y_test = split_dataset(X, y)
    print("train:", X_train.shape, y_train.shape)
    print("val:", X_val.shape, y_val.shape)
    print("test:", X_test.shape, y_test.shape)

    # 3. DataLoader：训练集打乱，验证/测试不需要打乱。
    train_loader = make_loader(X_train, y_train, BATCH_SIZE, shuffle=True)
    val_loader = make_loader(X_val, y_val, BATCH_SIZE, shuffle=False)
    test_loader = make_loader(X_test, y_test, BATCH_SIZE, shuffle=False)

    # 4. 定义模型、loss、优化器。
    net = build_model()
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=LEARNING_RATE)

    # 5. 训练模型，并在 test 集上做最终评估。
    train(net, train_loader, val_loader, loss_fn, optimizer, NUM_EPOCHS)

    test_loss = evaluate_loss(net, test_loader, loss_fn)
    print("test loss:", test_loss)
    print_sample_predictions(net, X_test, y_test)

    # 6. 保存模型参数。后续接回 Hybrid A* 时会加载这个文件。
    MODEL_DIR.mkdir(exist_ok=True)
    torch.save(net.state_dict(), MODEL_PATH)
    print("saved model:", MODEL_PATH)


if __name__ == "__main__":
    main()
