"""D2L 3.2 linear regression from scratch template.

This script keeps the full training loop explicit:

1. Generate synthetic data from known true parameters.
2. Read data in mini-batches.
3. Initialize learnable parameters.
4. Define the linear model and squared loss.
5. Update parameters with mini-batch SGD.
6. Check whether learned parameters recover the true ones.
"""

import random

import torch


def synthetic_data(w, b, num_examples):
    """Generate y = Xw + b + noise."""
    X = torch.normal(0, 1, (num_examples, len(w)))
    y = torch.matmul(X, w) + b
    y += torch.normal(0, 0.01, y.shape)
    return X, y.reshape((-1, 1))


def data_iter(batch_size, features, labels):
    """Yield mini-batches after shuffling sample indices."""
    num_examples = len(features)
    indices = list(range(num_examples))
    random.shuffle(indices)

    for i in range(0, num_examples, batch_size):
        batch_indices = torch.tensor(indices[i : min(i + batch_size, num_examples)])
        yield features[batch_indices], labels[batch_indices]


def linreg(X, w, b):
    """Linear regression model: y_hat = Xw + b."""
    return torch.matmul(X, w) + b


def squared_loss(y_hat, y):
    """Squared loss for each sample, not averaged over the batch."""
    return (y_hat - y.reshape(y_hat.shape)) ** 2 / 2


def sgd(params, lr, batch_size):
    """Mini-batch stochastic gradient descent."""
    with torch.no_grad():
        for param in params:
            param -= lr * param.grad / batch_size
            param.grad.zero_()


def main():
    random.seed(0)
    torch.manual_seed(0)

    # 1. Generate a dataset with known true parameters.
    true_w = torch.tensor([2, -3.4])
    true_b = 4.2
    features, labels = synthetic_data(true_w, true_b, 1000)

    print("features.shape:", features.shape)
    print("labels.shape:", labels.shape)
    print("first sample:", features[0], labels[0])

    # 2. Inspect one mini-batch.
    batch_size = 10
    for X, y in data_iter(batch_size, features, labels):
        print("first batch shapes:", X.shape, y.shape)
        break

    # 3. Initialize learnable parameters.
    w = torch.normal(0, 0.01, size=(2, 1), requires_grad=True)
    b = torch.zeros(1, requires_grad=True)

    # 4. Train with the explicit scratch training loop.
    lr = 0.03
    num_epochs = 3
    net = linreg
    loss = squared_loss

    for epoch in range(num_epochs):
        for X, y in data_iter(batch_size, features, labels):
            batch_loss = loss(net(X, w, b), y)
            batch_loss.sum().backward()
            sgd([w, b], lr, batch_size)

        with torch.no_grad():
            train_loss = loss(net(features, w, b), labels)
            print(f"epoch {epoch + 1}, loss {float(train_loss.mean()):f}")

    # 5. Compare learned parameters with the known true parameters.
    with torch.no_grad():
        print("w error:", true_w - w.reshape(true_w.shape))
        print("b error:", true_b - b)


if __name__ == "__main__":
    main()
