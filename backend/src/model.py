"""Small CNN that classifies a 3-channel ELA image."""

import torch
from torch import nn

import config


class ForgeryCNN(nn.Module):
    """Conv stack 3→16→32→64, then a single logit.

    The logit is the raw score for the positive class
    (Potentially Manipulated). Apply sigmoid outside the loss.
    """

    def __init__(self, dropout: float = config.DROPOUT):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.AdaptiveAvgPool2d(output_size=1),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=dropout),
            nn.Linear(64, 1),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(inputs)).squeeze(-1)


def build_model(dropout: float = config.DROPOUT) -> ForgeryCNN:
    model = ForgeryCNN(dropout=dropout)
    return model.to(torch.device("cpu"))
