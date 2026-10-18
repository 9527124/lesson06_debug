import io

import numpy as np
from PIL import Image

from image_io import load_rgb_image


def test_load_rgb_image_converts_rgba_to_rgb():
    image = Image.new("RGBA", (2, 1))
    image.putdata([
        (10, 20, 30, 0),
        (40, 50, 60, 255),
    ])

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    result = load_rgb_image(buffer)

    expected = np.array(
        [[[10, 20, 30], [40, 50, 60]]],
        dtype=np.uint8,
    )

    assert result.shape == (1, 2, 3)
    np.testing.assert_array_equal(result, expected)
