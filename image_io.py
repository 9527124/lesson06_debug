"""画像fileの読込処理."""

import numpy as np
from PIL import Image


def load_rgb_image(uploaded_file) -> np.ndarray:
    """画像fileを読み込み、shape [H,W,3] のRGB配列を返す."""
    image = Image.open(uploaded_file).convert("RGB")
    return np.asarray(image)
