"""画像読込時のRGB変換に関する回帰テスト."""

import numpy as np
from pathlib import Path

from image_io import load_rgb_image
from analysis import mean_rgb


def test_rgba_red_pixel_is_converted_to_rgb():
    """RGBA画像を読み込んでもRGBの3チャンネル配列になる."""
    path = Path(__file__).parent / "data" / "red_1px.png"

    with path.open("rb") as uploaded_file:
        result = load_rgb_image(uploaded_file)

    expected = np.array([[[255, 0, 0]]], dtype=np.uint8)

    assert result.shape == (1, 1, 3)
    np.testing.assert_array_equal(result, expected)
    np.testing.assert_allclose(mean_rgb(result), [255, 0, 0])
