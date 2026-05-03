import argparse
import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


matplotlib.use("Agg")

import matplotlib.pyplot as plt


class GridHeuristicCNN(nn.Module):
    """输入地图、起点、终点，输出整张 cost-to-go 预测图。"""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=2, dilation=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=4, dilation=4),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=8, dilation=8),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=4, dilation=4),
            nn.ReLU(),
            nn.Conv2d(64, 32, kernel_size=3, padding=2, dilation=2),
            nn.ReLU(),
            nn.Conv2d(32, 1, kernel_size=1),
        )

    def forward(self, x):
        return self.net(x)


def masked_mse_loss(pred, target, mask):
    """只在 free 且 reachable 的格子上计算 MSE。"""
    squared_error = (pred - target) ** 2
    return (squared_error * mask).sum() / mask.sum().clamp_min(1.0)


def masked_mae(pred, target, mask):
    absolute_error = torch.abs(pred - target)
    return (absolute_error * mask).sum() / mask.sum().clamp_min(1.0)


def load_dataset(dataset_path):
    data = np.load(dataset_path)
    inputs = torch.tensor(data["inputs"], dtype=torch.float32)
    targets = torch.tensor(data["targets"], dtype=torch.float32)
    masks = torch.tensor(data["masks"], dtype=torch.float32)
    maps = data["maps"]
    starts = data["starts"]
    goals = data["goals"]
    return inputs, targets, masks, maps, starts, goals


def split_dataset(inputs, targets, masks, seed):
    num_samples = len(inputs)
    generator = torch.Generator().manual_seed(seed)
    indices = torch.randperm(num_samples, generator=generator)

    train_end = int(num_samples * 0.7)
    val_end = int(num_samples * 0.85)

    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]

    return (
        TensorDataset(inputs[train_idx], targets[train_idx], masks[train_idx]),
        TensorDataset(inputs[val_idx], targets[val_idx], masks[val_idx]),
        TensorDataset(inputs[test_idx], targets[test_idx], masks[test_idx]),
        train_idx.numpy(),
        val_idx.numpy(),
        test_idx.numpy(),
    )


def evaluate(model, data_loader, device, target_scale):
    model.eval()
    total_loss = 0.0
    total_mae = 0.0
    total_count = 0

    with torch.no_grad():
        for X, y, mask in data_loader:
            X = X.to(device)
            y = y.to(device)
            mask = mask.to(device)

            pred = model(X)
            batch_loss = masked_mse_loss(pred, y, mask)
            batch_mae = masked_mae(pred * target_scale, y * target_scale, mask)

            batch_size = X.shape[0]
            total_loss += batch_loss.item() * batch_size
            total_mae += batch_mae.item() * batch_size
            total_count += batch_size

    return total_loss / total_count, total_mae / total_count


def train_model(args):
    torch.manual_seed(args.seed)

    inputs, targets, masks, maps, starts, goals = load_dataset(args.dataset)
    target_scale = float(targets[masks == 1].max().item())
    targets = targets / target_scale

    train_set, val_set, test_set, _, _, test_idx = split_dataset(
        inputs, targets, masks, args.seed
    )

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_set, batch_size=args.batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    model = GridHeuristicCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    print(f"device: {device}")
    print(f"dataset: {args.dataset}")
    print(f"train/val/test: {len(train_set)}/{len(val_set)}/{len(test_set)}")
    print(f"target scale: {target_scale:.2f}")

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_train_loss = 0.0
        total_count = 0

        for X, y, mask in train_loader:
            X = X.to(device)
            y = y.to(device)
            mask = mask.to(device)

            pred = model(X)
            loss = masked_mse_loss(pred, y, mask)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            batch_size = X.shape[0]
            total_train_loss += loss.item() * batch_size
            total_count += batch_size

        train_loss = total_train_loss / total_count
        val_loss, val_mae = evaluate(model, val_loader, device, target_scale)

        if epoch == 1 or epoch % args.print_every == 0 or epoch == args.epochs:
            print(
                f"epoch {epoch:03d}, "
                f"train loss {train_loss:.4f}, "
                f"val loss {val_loss:.4f}, "
                f"val MAE {val_mae:.4f}"
            )

    test_loss, test_mae = evaluate(model, test_loader, device, target_scale)
    print(f"test loss: {test_loss:.4f}")
    print(f"test MAE: {test_mae:.4f}")

    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "target_scale": target_scale,
        },
        args.model_path,
    )
    print(f"saved model: {args.model_path}")

    save_prediction_figure(
        model=model,
        device=device,
        inputs=inputs,
        targets=targets,
        masks=masks,
        target_scale=target_scale,
        maps=maps,
        starts=starts,
        goals=goals,
        sample_index=int(test_idx[0]),
        output_path=args.figure_path,
    )


def save_prediction_figure(
    model,
    device,
    inputs,
    targets,
    masks,
    target_scale,
    maps,
    starts,
    goals,
    sample_index,
    output_path,
):
    model.eval()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    X = inputs[sample_index : sample_index + 1].to(device)
    with torch.no_grad():
        pred = model(X).cpu()[0, 0].numpy() * target_scale

    target = targets[sample_index, 0].numpy() * target_scale
    mask = masks[sample_index, 0].numpy()
    grid = maps[sample_index]
    start = starts[sample_index]
    goal = goals[sample_index]

    visible_target = target.copy()
    visible_pred = pred.copy()
    visible_error = np.abs(pred - target)
    visible_target[mask == 0] = np.nan
    visible_pred[mask == 0] = np.nan
    visible_error[mask == 0] = np.nan

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].imshow(grid, cmap="gray_r", origin="upper")
    axes[0].scatter(start[1], start[0], c="lime", s=70, marker="o")
    axes[0].scatter(goal[1], goal[0], c="red", s=80, marker="*")
    axes[0].set_title("map")

    target_img = axes[1].imshow(visible_target, cmap="viridis", origin="upper")
    axes[1].set_title("Dijkstra target")
    fig.colorbar(target_img, ax=axes[1], fraction=0.046, pad=0.04)

    pred_img = axes[2].imshow(visible_pred, cmap="viridis", origin="upper")
    axes[2].set_title("CNN prediction")
    fig.colorbar(pred_img, ax=axes[2], fraction=0.046, pad=0.04)

    error_img = axes[3].imshow(visible_error, cmap="magma", origin="upper")
    axes[3].set_title("absolute error")
    fig.colorbar(error_img, ax=axes[3], fraction=0.046, pad=0.04)

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"saved prediction figure: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("datasets/grid2d_heuristic_v1.npz"),
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("models/grid_heuristic_cnn_v1.pth"),
    )
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=Path("results/cnn_prediction_v1.png"),
    )
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--print-every", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--cpu", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    train_model(args)


if __name__ == "__main__":
    main()
