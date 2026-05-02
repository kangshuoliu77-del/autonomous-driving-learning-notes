from pathlib import Path

import numpy as np
import torch
from torch import nn


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "datasets" / "parking_cost_to_go_v1.npz"
MODEL_PATH = BASE_DIR / "models" / "heuristic_mlp_v1.pth"

RANDOM_SEED = 0
NUM_RANKING_PAIRS = 10000


def build_model():
    # 必须和 train_heuristic_mlp.py 里保存参数时的模型结构一致。
    return nn.Sequential(
        nn.Linear(8, 64),
        nn.ReLU(),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Linear(64, 1),
    )


def main():
    torch.manual_seed(RANDOM_SEED)

    data = np.load(DATA_PATH)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.float32)

    print("Dataset:")
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    X_tensor = torch.tensor(X)
    y_tensor = torch.tensor(y)

    model = build_model()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    with torch.no_grad():
        pred = model(X_tensor)

    print("\nSample predictions:")
    for i in range(10):
        true_value = y_tensor[i].item()
        pred_value = pred[i].item()
        print(f"true={true_value:.2f}, pred={pred_value:.2f}")

    error = pred - y_tensor
    abs_error = torch.abs(error)

    mae = abs_error.mean().item()
    rmse = torch.sqrt((error ** 2).mean()).item()
    max_error = abs_error.max().item()

    print("\nOverall error:")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"Max error: {max_error:.4f}")

    print("\nError by cost range:")

    ranges = [
        ("0-5", 0, 5),
        ("5-10", 5, 10),
        ("10-15", 10, 15),
        ("15-20", 15, 20),
        ("20+", 20, 100),
    ]

    for name, low, high in ranges:
        mask = (y_tensor >= low) & (y_tensor < high)

        if mask.sum().item() == 0:
            continue

        range_abs_error = abs_error[mask]
        range_mae = range_abs_error.mean().item()
        range_max_error = range_abs_error.max().item()
        count = mask.sum().item()

        print(
            f"{name:<6} "
            f"count={count:>4}, "
            f"MAE={range_mae:.4f}, "
            f"Max={range_max_error:.4f}"
        )

    idx_a = torch.randint(0, len(y_tensor), (NUM_RANKING_PAIRS,))
    idx_b = torch.randint(0, len(y_tensor), (NUM_RANKING_PAIRS,))

    true_a = y_tensor[idx_a]
    true_b = y_tensor[idx_b]
    pred_a = pred[idx_a]
    pred_b = pred[idx_b]

    true_order = true_a < true_b
    pred_order = pred_a < pred_b
    valid = true_a != true_b

    ranking_acc = (true_order[valid] == pred_order[valid]).float().mean().item()

    print("\nRanking accuracy:")
    print(f"Ranking acc: {ranking_acc:.4f}")


if __name__ == "__main__":
    main()
