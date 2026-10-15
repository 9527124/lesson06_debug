"""画面表示に依存しない計算処理(testの対象)."""

import numpy as np


def mean_rgb(image: np.ndarray) -> np.ndarray:
    """shape [H,W,3] の配列から [R平均, G平均, B平均] を返す."""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("RGB image [H,W,3] required")
    return image.mean(axis=(0, 1))


def rgb_histograms(image: np.ndarray) -> dict:
    """R/G/B各channelの256 binヒストグラムを返す."""
    bin_edges = np.arange(257)
    return {
        label: np.histogram(image[..., ch], bins=bin_edges)[0]
        for ch, label in enumerate(("R", "G", "B"))
    }
