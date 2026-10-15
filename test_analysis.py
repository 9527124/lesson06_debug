import numpy as np
import pytest
from numpy.testing import assert_allclose

from analysis import mean_rgb


def test_mean_rgb_one_pixel():
    image = np.array([[[10, 20, 30]]], dtype=np.uint8)
    assert_allclose(mean_rgb(image), [10, 20, 30])


def test_mean_rgb_two_pixels():
    image = np.array([[[0, 10, 20], [20, 30, 40]]])
    assert_allclose(mean_rgb(image), [10, 20, 30])


def test_mean_rgb_all_zero():
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    assert_allclose(mean_rgb(image), [0, 0, 0])


def test_mean_rgb_all_max():
    image = np.full((2, 2, 3), 255, dtype=np.uint8)
    assert_allclose(mean_rgb(image), [255, 255, 255])


def test_mean_rgb_rejects_gray():
    gray = np.zeros((4, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        mean_rgb(gray)
